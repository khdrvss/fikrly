
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from frontend.models import BusinessCategory

CATEGORY_COLORS = {
    'Restoran': 'orange',
    'Klinika': 'blue',
    'Ta\'lim': 'purple',
    'Go\'zallik': 'pink',
    'Chakana': 'green',
    'Bank': 'blue',
    'Avto kompaniyalar': 'red',
    'Ichimliklar': 'yellow',
    'Neft va gaz': 'gray',
    'Telekommunikatsiya': 'blue',
    'Mobil operator': 'purple',
    'Gaz tashish': 'gray',
    'Elektronika': 'blue',
    'Aviatsiya': 'blue',
    'Aviakompaniya': 'blue',
    'Supermarket': 'green',
    'Temir yo\'l': 'gray',
    'Kimyo sanoati': 'yellow',
    'E-commerce va Fintech': 'blue',
    'Metallurgiya': 'gray',
    'Konchilik va metallurgiya': 'gray',
    'Fast-food': 'orange',
    'E-commerce': 'blue',
    'IT xizmatlari': 'blue',
    'Qishloq xo\'jaligi texnologiyalari': 'green',
    'Startap': 'purple',
    'Keytering': 'orange',
    'To\'qimachilik': 'pink',
    'Qurilish materiallari': 'yellow',
    'Oziq-ovqat yetkazib berish': 'green',
    'Ko\'chmas mulk': 'blue',
    'Fintech': 'blue',
    'IT': 'blue'
}

def run():
    print("Updating category colors...")
    for name, color in CATEGORY_COLORS.items():
        try:
            # Try to find by name (English or Russian/Uzbek depending on how they were saved)
            # The migration script saved them with the keys from the JSON which were English-ish or Uzbek
            # Let's try to match loosely
            cats = BusinessCategory.objects.filter(name__icontains=name)
            if not cats.exists():
                 cats = BusinessCategory.objects.filter(name_ru__icontains=name)

            for cat in cats:
                cat.color = color
                cat.save()
                print(f"Updated {cat.name} to {color}")

        except Exception as e:
            print(f"Error updating {name}: {e}")

    print("Done.")

if __name__ == '__main__':
    run()
