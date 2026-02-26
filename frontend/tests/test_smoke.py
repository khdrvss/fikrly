from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from allauth.socialaccount.models import SocialApp

from frontend.models import BusinessCategory, Company, Review, UserProfile


User = get_user_model()


class CriticalFlowSmokeTests(TestCase):
    def setUp(self):
        self.password = "StrongPass!234"
        self.user = User.objects.create_user(
            username="smokeuser",
            email="smokeuser@gmail.com",
            password=self.password,
            first_name="Smoke",
            last_name="User",
        )
        self.category = BusinessCategory.objects.create(
            name="Smoke Category",
            name_ru="Смоук категория",
            slug="smoke-category",
        )
        self.company = Company.objects.create(
            name="Smoke Company",
            category_fk=self.category,
            is_active=True,
        )
        # A separate company with no existing reviews, used for submission tests
        # so the duplicate-review guard doesn't block them.
        self.fresh_company = Company.objects.create(
            name="Fresh Smoke Company",
            category_fk=self.category,
            is_active=True,
        )
        self.review = Review.objects.create(
            company=self.company,
            user=self.user,
            user_name=self.user.username,
            rating=5,
            text="Initial review",
            is_approved=True,
        )

        site = Site.objects.get_current()
        google_app, _ = SocialApp.objects.get_or_create(
            provider="google",
            name="Google Test App",
            defaults={
                "client_id": "test-client-id",
                "secret": "test-secret",
            },
        )
        if not google_app.client_id:
            google_app.client_id = "test-client-id"
            google_app.secret = "test-secret"
            google_app.save(update_fields=["client_id", "secret"])
        google_app.sites.add(site)

    def test_login_page_contains_google_signin(self):
        response = self.client.get(reverse("account_login"), secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Google bilan kirish")

    def test_review_submission_creates_pending_review(self):
        self.client.login(username=self.user.username, password=self.password)

        response = self.client.post(
            reverse("review_submission"),
            {
                "company": self.fresh_company.pk,
                "user_name": "Smoke User",
                "rating": 4,
                "text": "Smoke review submit works",
            },
            follow=False,
            secure=True,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("company_detail", args=[self.fresh_company.pk]))

        created = Review.objects.filter(
            company=self.fresh_company,
            user=self.user,
            text="Smoke review submit works",
        ).first()
        self.assertIsNotNone(created)
        self.assertFalse(created.is_approved)

    def test_company_detail_renders_share_button(self):
        response = self.client.get(
            reverse("company_detail", args=[self.company.pk]), secure=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="shareBtn"')
        self.assertContains(response, "data-share-url")

    def test_company_like_toggle_returns_json(self):
        self.client.login(username=self.user.username, password=self.password)

        like_url = reverse("like_company", args=[self.company.pk])
        first = self.client.post(like_url, secure=True)
        second = self.client.post(like_url, secure=True)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertJSONEqual(first.content, {"ok": True, "like_count": 1, "liked": True})
        self.assertJSONEqual(second.content, {"ok": True, "like_count": 0, "liked": False})

    def test_review_like_toggle_returns_json(self):
        other = User.objects.create_user(
            username="smokeother",
            email="smokeother@gmail.com",
            password=self.password,
        )
        self.client.login(username=other.username, password=self.password)

        like_url = reverse("like_review", args=[self.review.pk])
        first = self.client.post(like_url, secure=True)
        second = self.client.post(like_url, secure=True)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertJSONEqual(first.content, {"ok": True, "like_count": 1, "liked": True})
        self.assertJSONEqual(second.content, {"ok": True, "like_count": 0, "liked": False})

    def test_profile_update_happy_path_updates_username_and_names(self):
        self.client.login(username=self.user.username, password=self.password)

        response = self.client.post(
            reverse("user_profile"),
            {
                "username": "smokeuser_new",
                "first_name": "Updated",
                "last_name": "Name",
                "bio": "Smoke bio",
            },
            follow=False,
            secure=True,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("user_profile"))

        self.user.refresh_from_db()
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(self.user.username, "smokeuser_new")
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Name")
        self.assertEqual(len(profile.username_change_log), 1)

    def test_review_submit_success_exposes_flash_toast_payload(self):
        self.client.login(username=self.user.username, password=self.password)

        response = self.client.post(
            reverse("review_submission"),
            {
                "company": self.fresh_company.pk,
                "user_name": "Smoke User",
                "rating": 5,
                "text": "Smoke review for flash popup",
            },
            follow=True,
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-flash-level="success"')
        self.assertContains(
            response,
            "Sharhingiz qabul qilindi va moderator tasdiqlagandan keyin",
        )

    def test_review_submit_invalid_shows_error_popup_trigger(self):
        self.client.login(username=self.user.username, password=self.password)

        response = self.client.post(
            reverse("review_submission"),
            {
                "company": self.company.pk,
                "user_name": "Smoke User",
                "rating": "",
                "text": "",
            },
            follow=False,
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Iltimos, formadagi xatolarni to'g'rilang.")
