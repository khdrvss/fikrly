
import os
import sys
import django
from django.utils.text import slugify

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from frontend.models import Company, BusinessCategory

CATEGORY_ICONS = {
    'Aviatsiya': '<path d="M21 16V4.58C21 4.21 20.81 3.85 20.49 3.62C20.17 3.38 19.73 3.28 19.3 3.34L3.3 5.35C2.67 5.44 2.25 6.03 2.25 6.7V16C2.25 16.69 2.81 17.25 3.5 17.25H21C21.41 17.25 21.75 16.91 21.75 16.5C21.75 16.09 21.41 15.75 21 15.75V16Z"/>',
    'Bank': '<path d="M12 2L3 7V8H21V7L12 2Z"/><path d="M4 9V19H20V9"/><path d="M8 15V13H10V15H8Z"/><path d="M14 15V13H16V15H14Z"/>',
    'Ichimliklar': '<path d="M5 12V7L7 5H17L19 7V12"/><path d="M5 12L2 22H22L19 12"/><path d="M12 5V2"/>',
    'Eksport, logistika': '<path d="M14 18V6C14 5.45 13.55 5 13 5H11C10.45 5 10 5.45 10 6V18L7 21L12 19L17 21L14 18Z"/>',
    'Energetika': '<path d="M13 2L3 14H12L11 22L21 10H12L13 2Z"/>',
    'Fast-food': '<path d="M8.5 8.5C9.33 8.5 10 7.83 10 7S9.33 5.5 8.5 5.5 7 6.17 7 7 7.67 8.5 8.5 8.5Z"/><path d="M12 2C10.89 2 10 2.89 10 4V7C10 8.11 10.89 9 12 9S14 8.11 14 7V4C14 2.89 13.11 2 12 2Z"/><path d="M5 9V20C5 21.1 5.9 22 7 22H17C18.1 22 19 21.1 19 20V9H5Z"/>',
    'Fintech': '<path d="M7 4V2C7 1.45 7.45 1 8 1H16C16.55 1 17 1.45 17 2V4H20C20.55 4 21 4.45 21 5S20.55 6 20 6H19V19C19 20.1 18.1 21 17 21H7C5.9 21 5 20.1 5 19V6H4C3.45 6 3 5.55 3 5S3.45 4 4 4H7Z"/>',
    'IT, Konsalting': '<path d="M20 3H4C2.9 3 2 3.9 2 5V19C2 20.1 2.9 21 4 21H20C21.1 21 22 20.1 22 19V5C22 3.9 21.1 3 20 3Z"/><path d="M8 17L12 13L16 17"/>',
    'IT, Raqamli marketing': '<path d="M12 2L13.09 8.26L22 9L13.09 15.74L12 22L10.91 15.74L2 9L10.91 8.26L12 2Z"/>',
    'IT, Texnologiya': '<path d="M9 12L11 14L15 10"/><path d="M21 12C21 16.97 16.97 21 12 21S3 16.97 3 12S7.03 3 12 3S21 7.03 21 12Z"/>',
    'Kimyo sanoati': '<path d="M10.5 2L8.5 8H15.5L13.5 2H10.5Z"/><path d="M7 8L5 16C4.72 17.2 5.54 18.36 6.76 18.64L17.24 18.64C18.46 18.36 19.28 17.2 19 16L17 8H7Z"/>',
    'Ko\'chmas mulk': '<path d="M10 20V14H14V20H19V12H22L12 3L2 12H5V20H10Z"/>',
    'Konchilik va metallurgiya': '<path d="M12 2L15.09 8.26L22 9L16 14.74L17.18 21.02L12 18.77L6.82 21.02L8 14.74L2 9L8.91 8.26L12 2Z"/>',
    'Metallurgiya': '<path d="M9 11H15L13 13L15 15H9L11 13L9 11Z"/><path d="M12 2L22 8.5V15.5L12 22L2 15.5V8.5L12 2Z"/>',
    'Mobil operator': '<path d="M22 16.92V19.92C22 20.51 21.39 21 20.92 21C18.95 20.87 16.95 20.22 15.21 19.27C13.15 18.15 11.26 16.26 10.14 14.2C9.19 12.46 8.54 10.46 8.41 8.49C8.4 8.18 8.56 7.65 9.01 7.65H12.01"/><path d="M18 2L22 6L18 10"/><path d="M14 6H22"/>',
    'Nodavlat notijorat tashkiloti': '<path d="M12 2L3.5 6.5V17.5L12 22L20.5 17.5V6.5L12 2Z"/><path d="M12 8C13.66 8 15 6.66 15 5S13.66 2 12 2S9 3.34 9 5S10.34 8 12 8Z"/>',
    'Neft va gaz': '<path d="M9 2V13C9 14.1 9.9 15 11 15H13C14.1 15 15 14.1 15 13V2H9Z"/><path d="M12 15V22"/>',
    'Oziq-ovqat ishlab chiqarish': '<path d="M12 2C6.48 2 2 6.48 2 12S6.48 22 12 22 22 17.52 22 12 17.52 2 12 2Z"/><path d="M8 12L11 15L16 10"/>',
    'Oziq-ovqat yetkazib berish': '<path d="M4 16L20 16"/><path d="M4 16L8 12"/><path d="M4 16L8 20"/>',
    'Supermarket': '<path d="M7 4V2C7 1.45 7.45 1 8 1H16C16.55 1 17 1.45 17 2V4"/><path d="M5 7H19L18 17H6L5 7Z"/><path d="M5 7L3 4"/>',
    'Tashqi savdo': '<path d="M21 12C21 16.97 16.97 21 12 21S3 16.97 3 12S7.03 3 12 3S21 7.03 21 12Z"/><path d="M8 12L11 15L16 10"/>',
}

def run():
    print("Starting category migration...")

    # 1. Create categories from dictionary
    for name, icon in CATEGORY_ICONS.items():
        slug = slugify(name)
        cat, created = BusinessCategory.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'icon_svg': icon}
        )
        if created:
            print(f"Created category: {name}")
        else:
            # Update icon if needed
            if not cat.icon_svg:
                cat.icon_svg = icon
                cat.save()
                print(f"Updated icon for: {name}")

    # 2. Link companies to categories
    companies = Company.objects.all()
    for company in companies:
        if not company.category:
            continue

        # Try to find exact match
        cat_name = company.category
        slug = slugify(cat_name)

        try:
            cat = BusinessCategory.objects.get(slug=slug)
        except BusinessCategory.DoesNotExist:
            # Create if not exists (for categories not in dictionary)
            print(f"Creating new category for company {company.name}: {cat_name}")
            cat = BusinessCategory.objects.create(
                name=cat_name,
                slug=slug,
                icon_svg='<path d="M12 2L2 7L12 12L22 7L12 2Z"/>' # Default icon
            )

        company.category_fk = cat
        company.save()
        print(f"Linked {company.name} to {cat.name}")

    print("Migration complete.")

if __name__ == '__main__':
    run()
