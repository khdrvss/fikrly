from django.test import TestCase


class LanguageSwitchTests(TestCase):
    def test_legacy_setlang_uz_strips_ru_prefix(self):
        response = self.client.post(
            "/i18n/setlang/",
            {"language": "uz", "next": "/ru/bizneslar/?q=test"},
            secure=True,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/bizneslar/?q=test")

    def test_legacy_setlang_ru_adds_ru_prefix(self):
        response = self.client.post(
            "/i18n/setlang/",
            {"language": "ru", "next": "/bizneslar/?q=test"},
            secure=True,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/ru/bizneslar/?q=test")

    def test_legacy_setlang_uz_home_from_ru(self):
        response = self.client.post(
            "/i18n/setlang/",
            {"language": "uz", "next": "/ru/"},
            secure=True,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")
