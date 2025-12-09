import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from frontend.models import Company

companies = Company.objects.filter(name__in=['Click', 'ANGLESEY FOOD', 'Max way', 'Asaxiy Books'])

for c in companies:
    print(f"Name: {c.name}")
    print(f"  Logo: {c.logo}")
    if c.logo:
        print(f"  Logo URL: {c.logo.url}")
    print(f"  Image: {c.image}")
    if c.image:
        print(f"  Image URL: {c.image.url}")
    print(f"  Image URL Field: {c.image_url}")
    print(f"  Library Image Path: {c.library_image_path}")
    print(f"  Display Image URL: {c.display_image_url}")
    print("-" * 20)
