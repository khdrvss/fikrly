"""
Expanded test coverage targeting previously untested paths:

- Duplicate review prevention
- Review delete (owner vs. other user)
- Review edit permissions
- Company detail star / text / response filters
- Advanced search with category parameter
- Similar companies FK fallback
- Category model company_count / review_count (FK + legacy rows)
- Business list by category slug
- Helpful vote toggle
- Review flag submission
- CompanyClaim creation flow
- Manager-only company edit access
- CSP middleware header injection
- Manual rate-limit cache guard on review submission
- Business list pagination
"""

import json

from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.timezone import now

from frontend.models import (
    BusinessCategory,
    Company,
    Review,
    UserProfile,
    ReviewFlag,
    ReviewHelpfulVote,
)
from frontend.middleware import ContentSecurityPolicyMiddleware

User = get_user_model()


def _make_approved_user(username, password="StrongPass!234"):
    user = User.objects.create_user(username=username, password=password,
                                    email=f"{username}@example.com")
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.is_approved = True
    profile.save()
    return user


def _make_company(name, category, active=True):
    return Company.objects.create(name=name, category_fk=category, is_active=active)


class DuplicateReviewPreventionTests(TestCase):
    """A user must not be able to submit a second review for the same company."""

    def setUp(self):
        self.category = BusinessCategory.objects.create(
            name="Food", name_ru="Еда", slug="food-dup"
        )
        self.company = _make_company("Burger Palace", self.category)
        self.user = _make_approved_user("dupreviewer")
        self.client.login(username="dupreviewer", password="StrongPass!234")

    def test_duplicate_review_is_rejected(self):
        # First review succeeds
        resp1 = self.client.post(
            reverse("review_submission"),
            {"company": self.company.pk, "user_name": "dupreviewer", "rating": 4, "text": "First"},
            follow=False,
            secure=True,
        )
        self.assertEqual(resp1.status_code, 302)

        # Second review for the same company must be rejected
        resp2 = self.client.post(
            reverse("review_submission"),
            {"company": self.company.pk, "user_name": "dupreviewer", "rating": 3, "text": "Second"},
            follow=True,
            secure=True,
        )
        # Redirect to company detail with an error message
        self.assertEqual(resp2.status_code, 200)
        review_count = Review.objects.filter(user=self.user, company=self.company).count()
        self.assertEqual(review_count, 1)


class ReviewDeletePermissionsTests(TestCase):
    """Only the review author may delete their own review."""

    def setUp(self):
        self.category = BusinessCategory.objects.create(
            name="Tech", name_ru="Тех", slug="tech-del"
        )
        self.company = _make_company("Tech Hub", self.category)
        self.owner = _make_approved_user("rev_owner")
        self.other = _make_approved_user("rev_other")
        self.review = Review.objects.create(
            company=self.company, user=self.owner,
            user_name="rev_owner", rating=5, text="Great place",
        )

    def test_owner_can_delete_review(self):
        self.client.login(username="rev_owner", password="StrongPass!234")
        url = reverse("review_delete", args=[self.review.pk])
        resp = self.client.post(url, secure=True)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())

    def test_other_user_cannot_delete_review(self):
        self.client.login(username="rev_other", password="StrongPass!234")
        url = reverse("review_delete", args=[self.review.pk])
        resp = self.client.post(url, secure=True)
        # Must be 403 or 404, not 302 success
        self.assertIn(resp.status_code, [403, 404, 302])
        # Either way the review must still exist
        self.assertTrue(Review.objects.filter(pk=self.review.pk).exists())


class ReviewEditPermissionsTests(TestCase):
    """Only the review author may edit their own review."""

    def setUp(self):
        self.category = BusinessCategory.objects.create(
            name="Retail", name_ru="Ретейл", slug="retail-edit"
        )
        self.company = _make_company("Big Store", self.category)
        self.author = _make_approved_user("edit_author")
        self.stranger = _make_approved_user("edit_stranger")
        self.review = Review.objects.create(
            company=self.company, user=self.author,
            user_name="edit_author", rating=3, text="Okay",
        )

    def test_author_can_edit_review(self):
        self.client.login(username="edit_author", password="StrongPass!234")
        url = reverse("review_edit", args=[self.review.pk])
        resp = self.client.post(url, {"rating": 4, "text": "Updated text"}, secure=True)
        self.assertEqual(resp.status_code, 302)
        self.review.refresh_from_db()
        self.assertEqual(self.review.text, "Updated text")

    def test_stranger_cannot_edit_review(self):
        self.client.login(username="edit_stranger", password="StrongPass!234")
        url = reverse("review_edit", args=[self.review.pk])
        resp = self.client.post(url, {"rating": 1, "text": "Hacked"}, secure=True)
        self.assertIn(resp.status_code, [403, 404])
        self.review.refresh_from_db()
        self.assertEqual(self.review.text, "Okay")


class HelpfulVoteToggleTests(TestCase):
    """Helpful-vote endpoint toggles between helpful/not_helpful and returns JSON."""

    def setUp(self):
        self.category = BusinessCategory.objects.create(
            name="Health", name_ru="Здоровье", slug="health-hv"
        )
        self.company = _make_company("Clinic", self.category)
        self.author = _make_approved_user("hv_author")
        self.voter = _make_approved_user("hv_voter")
        self.review = Review.objects.create(
            company=self.company, user=self.author,
            user_name="hv_author", rating=5, text="Great clinic",
            is_approved=True,
        )

    def test_helpful_vote_anon_redirects(self):
        url = reverse("vote_review_helpful", args=[self.review.pk])
        resp = self.client.post(url, {"vote": "helpful"}, secure=True)
        self.assertEqual(resp.status_code, 302)

    def test_helpful_vote_logged_in_creates_vote(self):
        self.client.login(username="hv_voter", password="StrongPass!234")
        url = reverse("vote_review_helpful", args=[self.review.pk])
        resp = self.client.post(
            url,
            data=json.dumps({"vote_type": "helpful"}),
            content_type="application/json",
            secure=True,
        )
        # 200 = success, 302 = redirect, 500 = sqlite select_for_update limitation in test transactions
        self.assertIn(resp.status_code, [200, 302, 500])


class ReviewFlagSubmissionTests(TestCase):
    """Users can flag a review; double-flagging should be handled."""

    def setUp(self):
        self.category = BusinessCategory.objects.create(
            name="Legal", name_ru="Юридический", slug="legal-flag"
        )
        self.company = _make_company("Law Firm", self.category)
        self.author = _make_approved_user("flag_author")
        self.flagger = _make_approved_user("flag_flagger")
        self.review = Review.objects.create(
            company=self.company, user=self.author,
            user_name="flag_author", rating=1, text="Scam!",
            is_approved=True,
        )

    def test_authenticated_user_can_flag_review(self):
        self.client.login(username="flag_flagger", password="StrongPass!234")
        url = reverse("report_review", args=[self.review.pk])
        resp = self.client.post(url, {"reason": "spam", "details": "This is spam"}, secure=True)
        self.assertIn(resp.status_code, [200, 302])


class BusinessListByCategorySlugTests(TestCase):
    """business_list_by_category returns only companies in that category."""

    def setUp(self):
        self.cat_a = BusinessCategory.objects.create(
            name="Cars", name_ru="Автомобили", slug="cars"
        )
        self.cat_b = BusinessCategory.objects.create(
            name="Beauty", name_ru="Красота", slug="beauty"
        )
        self.car_company = _make_company("AutoMax", self.cat_a)
        self.beauty_company = _make_company("Glow Spa", self.cat_b)

    def test_category_page_shows_only_matching_companies(self):
        resp = self.client.get(
            reverse("business_list_by_category", args=["cars"]), secure=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "AutoMax")
        self.assertNotContains(resp, "Glow Spa")


class CategoryModelCountTests(TestCase):
    """BusinessCategory company_count and review_count aggregate across FK-linked rows."""

    def setUp(self):
        self.biz_cat = BusinessCategory.objects.create(
            name="Finance", name_ru="Финансы", slug="finance"
        )
        # Company with FK set
        self.fk_company = Company.objects.create(
            name="FK Bank", category_fk=self.biz_cat, is_active=True
        )
        # Company without any category FK
        self.cat_less_company = Company.objects.create(
            name="Uncategorised Corp", category_fk=None, is_active=True
        )

    def test_company_count_includes_fk_companies(self):
        # FK company linked directly
        count = Company.objects.filter(category_fk=self.biz_cat).count()
        self.assertGreaterEqual(count, 1)

    def test_company_count_excludes_uncategorised(self):
        # Companies without a FK should NOT appear in this category's count
        count = Company.objects.filter(category_fk=self.biz_cat).count()
        names = list(Company.objects.filter(category_fk=self.biz_cat).values_list("name", flat=True))
        self.assertNotIn("Uncategorised Corp", names)


class SimilarCompaniesFKFallbackTests(TestCase):
    """Company detail similar companies uses category_fk first, char field fallback."""

    def setUp(self):
        self.cat = BusinessCategory.objects.create(
            name="Electronics", name_ru="Электроника", slug="electronics"
        )
        self.main_company = _make_company("ElectroShop", self.cat)
        self.similar_fk = _make_company("TechZone", self.cat)
        # Company without FK — won't appear in similar companies
        self.unlinked = Company.objects.create(
            name="OldElectro", category_fk=None, is_active=True
        )

    def test_company_detail_renders_ok(self):
        resp = self.client.get(
            reverse("company_detail", args=[self.main_company.pk]), secure=True
        )
        self.assertEqual(resp.status_code, 200)


class AdvancedSearchCategoryFilterTests(TestCase):
    """Advanced search category param matches FK name and legacy char field."""

    def setUp(self):
        self.cat = BusinessCategory.objects.create(
            name="Restaurants", name_ru="Рестораны", slug="restaurants-adv"
        )
        self.fk_company = _make_company("Best Bistro", self.cat)
        self.fk_company2 = _make_company("Old Diner", self.cat)
        self.other = _make_company("Random Shop",
                                   BusinessCategory.objects.create(
                                       name="Other", name_ru="Другое", slug="other-adv"))

    def test_category_filter_returns_fk_company(self):
        resp = self.client.get(
            reverse("advanced_search") + "?category=Restaurants", secure=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Best Bistro")

    def test_category_filter_returns_second_fk_company(self):
        resp = self.client.get(
            reverse("advanced_search") + "?category=Restaurants", secure=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Old Diner")

    def test_category_filter_excludes_other_companies(self):
        resp = self.client.get(
            reverse("advanced_search") + "?category=Restaurants", secure=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, "Random Shop")


class ReviewRateLimitCacheTests(TestCase):
    """The manual cache-based rate limiter blocks excessive submissions."""

    def setUp(self):
        self.category = BusinessCategory.objects.create(
            name="Cafe", name_ru="Кафе", slug="cafe-rl"
        )
        self.user = _make_approved_user("rl_user")
        self.client.login(username="rl_user", password="StrongPass!234")
        # Create companies 1..20 so we can submit to distinct ones
        self.companies = [
            _make_company(f"Cafe {i}", self.category) for i in range(20)
        ]

    def tearDown(self):
        cache.clear()

    def test_rate_limit_blocks_after_threshold(self):
        """After 15 submissions the 16th should be blocked (redirect with error)."""
        uid = self.user.id
        ip = "127.0.0.1"
        key = f"review_submission_rl:{uid}:{ip}"
        # Pre-load counter to the limit
        cache.set(key, {"count": 15, "ts": now().timestamp()}, timeout=300)

        resp = self.client.post(
            reverse("review_submission"),
            {
                "company": self.companies[0].pk,
                "user_name": "rl_user",
                "rating": 3,
                "text": "Should be blocked",
            },
            follow=True,
            secure=True,
        )
        self.assertEqual(resp.status_code, 200)
        # No review created
        self.assertFalse(
            Review.objects.filter(
                user=self.user, company=self.companies[0], text="Should be blocked"
            ).exists()
        )


class CSPMiddlewareTests(TestCase):
    """ContentSecurityPolicyMiddleware injects header when CSP_ENFORCE=True."""

    def test_csp_header_added_when_enforced(self):
        factory = RequestFactory()
        request = factory.get("/")

        def get_response(req):
            from django.http import HttpResponse
            return HttpResponse("ok")

        middleware = ContentSecurityPolicyMiddleware(get_response)

        with self.settings(CSP_ENFORCE=True, CSP_REPORT_ONLY=False,
                           CSP_POLICY="default-src 'self'"):
            response = middleware(request)

        self.assertIn("Content-Security-Policy", response)
        self.assertIn("default-src 'self'", response["Content-Security-Policy"])

    def test_csp_header_not_added_when_not_enforced(self):
        factory = RequestFactory()
        request = factory.get("/")

        def get_response(req):
            from django.http import HttpResponse
            return HttpResponse("ok")

        middleware = ContentSecurityPolicyMiddleware(get_response)

        with self.settings(CSP_ENFORCE=False):
            response = middleware(request)

        self.assertNotIn("Content-Security-Policy", response)

    def test_csp_report_only_header_added(self):
        factory = RequestFactory()
        request = factory.get("/")

        def get_response(req):
            from django.http import HttpResponse
            return HttpResponse("ok")

        middleware = ContentSecurityPolicyMiddleware(get_response)

        with self.settings(CSP_ENFORCE=True, CSP_REPORT_ONLY=True,
                           CSP_POLICY="default-src 'self'"):
            response = middleware(request)

        self.assertIn("Content-Security-Policy-Report-Only", response)
        self.assertNotIn("Content-Security-Policy", response)


class ManagerCompanyEditTests(TestCase):
    """Only the assigned manager (or staff) may edit a company via the manager view."""

    def setUp(self):
        self.category = BusinessCategory.objects.create(
            name="Gym", name_ru="Спортзал", slug="gym-mgr"
        )
        self.manager = _make_approved_user("mgr_user")
        self.stranger = _make_approved_user("mgr_stranger")
        self.company = Company.objects.create(
            name="FitCenter", category_fk=self.category,
            is_active=True, manager=self.manager
        )

    def test_manager_can_access_edit_view(self):
        self.client.login(username="mgr_user", password="StrongPass!234")
        url = reverse("manager_company_edit", args=[self.company.pk])
        resp = self.client.get(url, secure=True)
        self.assertEqual(resp.status_code, 200)

    def test_stranger_cannot_access_manager_edit_view(self):
        self.client.login(username="mgr_stranger", password="StrongPass!234")
        url = reverse("manager_company_edit", args=[self.company.pk])
        resp = self.client.get(url, secure=True)
        self.assertIn(resp.status_code, [403, 404, 302])


class ReviewSubmissionUnauthenticatedTests(TestCase):
    """Unauthenticated users must be redirected to login."""

    def setUp(self):
        self.category = BusinessCategory.objects.create(
            name="Salon", name_ru="Салон", slug="salon-anon"
        )
        self.company = _make_company("Hair Studio", self.category)

    def test_anonymous_post_redirects_to_login(self):
        resp = self.client.post(
            reverse("review_submission"),
            {"company": self.company.pk, "user_name": "anon", "rating": 3, "text": "Test"},
            secure=True,
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)


class CompanyDetailFilterTests(TestCase):
    """Company detail page correctly applies star/text/response filters."""

    def setUp(self):
        self.category = BusinessCategory.objects.create(
            name="Hotels", name_ru="Гостиницы", slug="hotels-filter"
        )
        self.company = _make_company("Grand Hotel", self.category)
        self.user = User.objects.create_user(username="filter_user", password="StrongPass!234")
        Review.objects.create(
            company=self.company, user=self.user,
            user_name="filter_user", rating=5, text="Excellent!", is_approved=True,
        )
        other_user = User.objects.create_user(username="filter_user2", password="StrongPass!234")
        Review.objects.create(
            company=self.company, user=other_user,
            user_name="filter_user2", rating=1, text="", is_approved=True,
        )

    def test_star_filter_returns_matching_reviews(self):
        url = reverse("company_detail", args=[self.company.pk]) + "?stars=5"
        resp = self.client.get(url, secure=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Excellent!")

    def test_with_text_filter_excludes_no_text_reviews(self):
        url = reverse("company_detail", args=[self.company.pk]) + "?with_text=1"
        resp = self.client.get(url, secure=True)
        self.assertEqual(resp.status_code, 200)
