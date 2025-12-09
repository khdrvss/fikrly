from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from frontend.forms import ReviewForm
from frontend.models import Company, BusinessCategory

class ReviewFileUploadTests(TestCase):
    def setUp(self):
        self.category = BusinessCategory.objects.create(name="Test Cat", slug="test-cat")
        self.company = Company.objects.create(name="Test Company", category_fk=self.category, is_active=True)

    def test_large_file_upload_validation(self):
        # Create a dummy file content > 5MB
        large_content = b'0' * (5 * 1024 * 1024 + 1)
        large_file = SimpleUploadedFile("large_receipt.jpg", large_content, content_type="image/jpeg")

        data = {
            'company': self.company.pk,
            'user_name': 'Test User',
            'rating': 5,
            'text': 'Test review text',
        }
        files = {
            'receipt': large_file
        }

        form = ReviewForm(data=data, files=files)
        self.assertFalse(form.is_valid())
        self.assertIn('receipt', form.errors)

    def test_small_file_upload_validation(self):
        # Valid GIF content (1x1 pixel)
        small_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        small_file = SimpleUploadedFile("small_receipt.gif", small_content, content_type="image/gif")

        data = {
            'company': self.company.pk,
            'user_name': 'Test User',
            'rating': 5,
            'text': 'Test review text',
        }
        files = {
            'receipt': small_file
        }

        form = ReviewForm(data=data, files=files)
        self.assertTrue(form.is_valid(), form.errors)
