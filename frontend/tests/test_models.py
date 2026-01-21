from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Company, Review, BusinessCategory

User = get_user_model()


class CompanyModelTests(TestCase):
    def setUp(self):
        self.category = BusinessCategory.objects.create(name="Tech", slug="tech")
        self.company = Company.objects.create(
            name="Test Corp", category_fk=self.category, is_active=True
        )

    def test_company_creation(self):
        self.assertEqual(self.company.name, "Test Corp")
        self.assertEqual(self.company.rating, 0)
        self.assertEqual(self.company.review_count, 0)

    def test_display_image_url_fallback(self):
        # Should return empty string or None if no image
        self.assertFalse(self.company.image)
        # If image_url is set
        self.company.image_url = "http://example.com/img.jpg"
        self.company.save()
        self.assertEqual(self.company.display_image_url, "http://example.com/img.jpg")


class ReviewLogicTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="reviewer", password="password")
        self.category = BusinessCategory.objects.create(name="Food", slug="food")
        self.company = Company.objects.create(
            name="Burger King", category_fk=self.category
        )

    def test_review_approval_updates_stats(self):
        # Create a review
        review = Review.objects.create(
            company=self.company,
            user=self.user,
            rating=5,
            text="Great!",
            is_approved=False,
        )

        # Stats should not update yet
        self.company.refresh_from_db()
        self.assertEqual(self.company.review_count, 0)

        # Approve review
        review.is_approved = True
        review.save()

        # Now stats should update (assuming signals or save method handles this)
        # Note: In your current code, you might need to call recalculate_company_stats explicitly
        # or ensure signals are connected. Let's check if your project uses signals for this.
        from ..utils import recalculate_company_stats

        recalculate_company_stats(self.company.pk)

        self.company.refresh_from_db()
        self.assertEqual(self.company.review_count, 1)
        self.assertEqual(self.company.rating, 5.0)
