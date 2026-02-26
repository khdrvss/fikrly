from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from frontend.models import Company, BusinessCategory, Review


class SecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.category = BusinessCategory.objects.create(
            name="Test Cat", name_ru="Тест категория", slug="test-cat"
        )
        self.company = Company.objects.create(
            name="Test Company", category_fk=self.category, is_active=True
        )
        self.review = Review.objects.create(
            company=self.company,
            user=self.user,
            user_name="testuser",
            rating=5,
            text="Original text",
            is_approved=True,  # Initially approved
        )

    def test_editing_approved_review_resets_approval(self):
        self.client.login(username="testuser", password="password")
        url = reverse("review_edit", args=[self.review.pk])

        data = {
            "rating": 4,
            "text": "Edited text with potential spam",
        }

        response = self.client.post(url, data, secure=True)

        # Check redirection
        self.assertEqual(response.status_code, 302)

        # Reload review from DB
        self.review.refresh_from_db()

        # Assert text changed
        self.assertEqual(self.review.text, "Edited text with potential spam")

        # Assert approval is reset (Security Fix)
        self.assertFalse(
            self.review.is_approved,
            "Editing an approved review should reset is_approved to False",
        )



class AuthConfigSecurityTests(TestCase):
    def test_social_email_autolink_uses_custom_adapter(self):
        """The custom SocialAccountAdapter is always in use regardless of the
        allauth auto-connect setting.  This is the primary security guard."""
        self.assertEqual(
            settings.SOCIALACCOUNT_ADAPTER,
            "frontend.adapters.SocialAccountAdapter",
        )

    def test_account_rate_limits_are_configured(self):
        """Allauth rate limits must be set for login and signup endpoints."""
        rate_limits = getattr(settings, "ACCOUNT_RATE_LIMITS", {})
        self.assertIn("login_failed", rate_limits)
        self.assertIn("signup", rate_limits)
