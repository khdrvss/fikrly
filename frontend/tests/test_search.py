from django.test import TestCase
from django.urls import reverse
from frontend.models import Company, BusinessCategory

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
