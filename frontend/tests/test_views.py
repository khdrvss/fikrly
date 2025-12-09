from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Company, BusinessCategory, UserProfile

User = get_user_model()

class ReviewSubmissionViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = BusinessCategory.objects.create(name="Test Cat", slug="test-cat")
        self.company = Company.objects.create(name="Test Company", category_fk=self.category, is_active=True)
        self.url = reverse('review_submission')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_access_if_logged_in(self):
        user = User.objects.create_user(username='testuser', password='password')
        # Ensure profile is approved to avoid redirect
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_approved = True
        profile.save()

        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

class ReportReviewViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = BusinessCategory.objects.create(name="Test Cat", slug="test-cat")
        self.company = Company.objects.create(name="Test Company", category_fk=self.category, is_active=True)
        # Create a dummy review to report
        from ..models import Review
        self.user = User.objects.create_user(username='reviewer', password='password')
        self.review = Review.objects.create(company=self.company, user=self.user, rating=5, text="Good")
        self.url = reverse('report_review', args=[self.review.pk])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_access_if_logged_in(self):
        user = User.objects.create_user(username='reporter', password='password')
        # Approve profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_approved = True
        profile.save()

        self.client.login(username='reporter', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
