from django.test import TestCase
from django.urls import reverse
from frontend.models import Company, BusinessCategory


class SearchTests(TestCase):
    def setUp(self):
        self.category = BusinessCategory.objects.create(
            name="Test Category",
            name_ru="Тестовая категория",
            slug="test-category",
            icon_svg="<path d='...'/>",
        )
        self.company = Company.objects.create(
            name="Test Company", category_fk=self.category, is_active=True
        )

    def test_search_suggestions_api(self):
        # Test with query matching both names; API should return companies only
        response = self.client.get(
            reverse("search_suggestions_api"),
            {"q": "Test", "include_categories": "1"},
            secure=True,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check results structure
        self.assertIn("results", data)
        results = data["results"]

        self.assertTrue(
            any(r["type"] == "company" and r["name"] == "Test Company" for r in results)
        )
        self.assertFalse(any(r["type"] == "category" for r in results))

    def test_search_suggestions_default_companies_only(self):
        response = self.client.get(
            reverse("search_suggestions_api"), {"q": "Test"}, secure=True
        )
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertTrue(any(r["type"] == "company" for r in results))
        self.assertFalse(any(r["type"] == "category" for r in results))

    def test_search_suggestions_empty(self):
        response = self.client.get(
            reverse("search_suggestions_api"), {"q": "NonExistent"}, secure=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 0)

    def test_search_suggestions_short_query(self):
        response = self.client.get(
            reverse("search_suggestions_api"), {"q": "a"}, secure=True
        )
        self.assertEqual(response.status_code, 200)
