from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class AuthFlowTests(TestCase):
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
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(get_user_model().objects.filter(username="user1").exists())

        # Logout just in case
        self.client.get(reverse("account_logout"), follow=True)

        # Login by username
        resp2 = self.client.post(
            reverse("account_login"),
            {
                "login": "user1",
                "password": "StrongPass!234",
            },
            follow=True,
        )
        self.assertEqual(resp2.status_code, 200)
        # Home should be accessible and authenticated
        # Note: Home view sets a session var that triggers a redirect to profile via middleware
        home = self.client.get("/", follow=True)
        self.assertEqual(home.status_code, 200)
