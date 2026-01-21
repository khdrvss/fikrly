from django.core.management.base import BaseCommand
from frontend.models import Company


class Command(BaseCommand):
    help = "Translates English category names to Uzbek"

    def handle(self, *args, **options):
        # Mapping of English (or other) -> Uzbek
        mapping = {
            "Automotive": "Avto kompaniyalar",
            "Beverage": "Ichimliklar",
            "Oil and Gas": "Neft va gaz",
            "Telecommunications": "Telekommunikatsiya",
            "Mobile Operator": "Mobil operator",
            "Gas Transportation": "Gaz tashish",
            "Bank": "Bank",
            "Electronics": "Elektronika",
            "Airline": "Aviakompaniya",
            "Supermarket": "Supermarket",
            "Railway Transportation": "Temir yo'l",
            "Chemical Industry": "Kimyo sanoati",
            "E-commerce and Fintech": "E-commerce va Fintech",
            "Metallurgy": "Metallurgiya",
            "Mining and Metallurgy": "Konchilik va metallurgiya",
            "Fast-food": "Fast-food",
            "E-commerce": "E-commerce",
            "IT Services": "IT xizmatlari",
            "Agricultural Technology": "Qishloq xo'jaligi texnologiyalari",
            "Startup": "Startap",
            "Catering": "Keytering",
            "Textile": "To'qimachilik",
            "Construction Materials": "Qurilish materiallari",
            "Food Delivery": "Oziq-ovqat yetkazib berish",
            "Real Estate": "Ko'chmas mulk",
            "Restaurant": "Restoran",
            "Fintech": "Fintech",
            "IT": "IT",
            # Fixes for existing mixed data
            "Avtomobil": "Avto kompaniyalar",
        }

        companies = Company.objects.all()
        updated_count = 0

        for company in companies:
            current_cat = company.category.strip()

            # Check if we have a direct mapping
            if current_cat in mapping:
                new_cat = mapping[current_cat]
                if current_cat != new_cat:
                    self.stdout.write(
                        f"Renaming '{current_cat}' -> '{new_cat}' for {company.name}"
                    )
                    company.category = new_cat
                    company.save()
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully updated {updated_count} companies.")
        )
