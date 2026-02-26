from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from urllib.parse import urlsplit
from frontend.models import UserProfile
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings


class AuthFlowTests(TestCase):
    def setUp(self):
        site_id = int(getattr(settings, "SITE_ID", 1))
        site, _ = Site.objects.get_or_create(
            id=site_id,
            defaults={"domain": "testserver", "name": "testserver"},
        )
        app, _ = SocialApp.objects.get_or_create(
            provider="google",
            defaults={
                "name": "Google",
                "client_id": "test-client-id",
                "secret": "test-secret",
            },
        )
        app.sites.add(site)

    def test_signup_and_login(self):
        # Signup
        resp = self.client.post(
            reverse("account_signup"),
            {
                "email": "user@gmail.com",
                "username": "user1",
                "password1": "StrongPass!234",
                "password2": "StrongPass!234",
            },
            follow=True,
            secure=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(get_user_model().objects.filter(username="user1").exists())

        # Logout just in case
        self.client.get(reverse("account_logout"), follow=True, secure=True)

        # Login by username
        resp2 = self.client.post(
            reverse("account_login"),
            {
                "login": "user1",
                "password": "StrongPass!234",
            },
            follow=True,
            secure=True,
        )
        self.assertEqual(resp2.status_code, 200)
        # Home should be accessible and authenticated
        # Note: Home view sets a session var that triggers a redirect to profile via middleware
        home = self.client.get("/", follow=True, secure=True)
        self.assertEqual(home.status_code, 200)

    def test_login_preserves_next_redirect_target(self):
        user = get_user_model().objects.create_user(
            username="nextuser",
            email="nextuser@gmail.com",
            password="StrongPass!234",
        )

        target = "/sharh-yozish/?company=57"
        response = self.client.post(
            reverse("account_login"),
            {
                "login": user.username,
                "password": "StrongPass!234",
                "next": target,
            },
            follow=False,
            secure=True,
        )

        self.assertEqual(response.status_code, 302)
        parsed = urlsplit(response["Location"])
        self.assertEqual(f"{parsed.path}?{parsed.query}", target)

    def test_signup_preserves_next_redirect_target(self):
        target = "/sharh-yozish/?company=57"
        response = self.client.post(
            reverse("account_signup"),
            {
                "email": "signupnext@gmail.com",
                "username": "signupnext",
                "password1": "StrongPass!234",
                "password2": "StrongPass!234",
                "next": target,
            },
            follow=False,
            secure=True,
        )

        self.assertEqual(response.status_code, 302)
        parsed = urlsplit(response["Location"])
        self.assertEqual(f"{parsed.path}?{parsed.query}", target)

    def test_profile_username_must_be_unique(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="alphauser",
            email="alphauser@gmail.com",
            password="StrongPass!234",
        )
        User.objects.create_user(
            username="existinguser",
            email="existinguser@gmail.com",
            password="StrongPass!234",
        )

        self.client.login(username="alphauser", password="StrongPass!234")
        response = self.client.post(
            reverse("user_profile"),
            {
                "username": "existinguser",
                "first_name": "Ali",
                "last_name": "Valiyev",
                "bio": "test",
            },
            follow=True,
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.username, "alphauser")

    def test_profile_username_change_limited_to_two_in_three_days(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="limituser",
            email="limituser@gmail.com",
            password="StrongPass!234",
        )
        profile, _ = UserProfile.objects.get_or_create(user=user)
        now = timezone.now()
        profile.username_change_log = [
            (now - timedelta(days=1)).isoformat(),
            (now - timedelta(days=2)).isoformat(),
        ]
        profile.save(update_fields=["username_change_log"])

        self.client.login(username="limituser", password="StrongPass!234")
        response = self.client.post(
            reverse("user_profile"),
            {
                "username": "limituser_new",
                "first_name": "Ali",
                "last_name": "Valiyev",
                "bio": "test",
            },
            follow=True,
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.username, "limituser")
