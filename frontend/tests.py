from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Company, BusinessCategory
from .views import ReviewForm


class AuthFlowTests(TestCase):
	def test_signup_and_login(self):
		# Signup
		resp = self.client.post(reverse('account_signup'), {
			'email': 'user@gmail.com',
			'username': 'user1',
			'password1': 'StrongPass!234',
			'password2': 'StrongPass!234',
		}, follow=True)
		self.assertEqual(resp.status_code, 200)
		self.assertTrue(get_user_model().objects.filter(username='user1').exists())

		# Logout just in case
		self.client.get(reverse('account_logout'), follow=True)

		# Login by username
		resp2 = self.client.post(reverse('account_login'), {
			'login': 'user1',
			'password': 'StrongPass!234',
		}, follow=True)
		self.assertEqual(resp2.status_code, 200)
		# Home should be accessible and authenticated
		# Note: Home view sets a session var that triggers a redirect to profile via middleware
		home = self.client.get('/', follow=True)
		self.assertEqual(home.status_code, 200)


class SearchTests(TestCase):
	def setUp(self):
		self.category = BusinessCategory.objects.create(
			name="Test Category",
			slug="test-category",
			icon_svg="<path d='...'/>"
		)
		self.company = Company.objects.create(
			name="Test Company",
			category_fk=self.category,
			is_active=True
		)

	def test_search_suggestions_api(self):
		# Test with query matching both
		response = self.client.get(reverse('search_suggestions_api'), {'q': 'Test'})
		self.assertEqual(response.status_code, 200)
		data = response.json()

		# Check results structure
		self.assertIn('results', data)
		results = data['results']

		# Should find both category and company
		self.assertTrue(any(r['type'] == 'category' and r['name'] == 'Test Category' for r in results))
		self.assertTrue(any(r['type'] == 'company' and r['name'] == 'Test Company' for r in results))

	def test_search_suggestions_empty(self):
		response = self.client.get(reverse('search_suggestions_api'), {'q': 'NonExistent'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.json()['results']), 0)

	def test_search_suggestions_short_query(self):
		response = self.client.get(reverse('search_suggestions_api'), {'q': 'a'})
		self.assertEqual(response.status_code, 200)


class ReviewFileUploadTests(TestCase):
	def test_large_file_upload_validation(self):
		# Create a dummy file content > 5MB
		large_content = b'0' * (5 * 1024 * 1024 + 1)
		large_file = SimpleUploadedFile("large_receipt.jpg", large_content, content_type="image/jpeg")

		data = {
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
		small_content = b'0' * (1024) # 1KB
		small_file = SimpleUploadedFile("small_receipt.jpg", small_content, content_type="image/jpeg")

		data = {
			'rating': 5,
			'text': 'Test review text',
		}
		files = {
			'receipt': small_file
		}

		form = ReviewForm(data=data, files=files)
		self.assertTrue(form.is_valid())

		self.assertEqual(len(response.json()['results']), 0)
