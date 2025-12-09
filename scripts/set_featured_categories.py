import os
import sys
import django

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from frontend.models import BusinessCategory

def set_featured_categories():
    featured_slugs = ['chakana', 'restoran', 'gozallik', 'talim']

    # Reset all first (optional, but good for idempotency if we change logic later)
    BusinessCategory.objects.update(is_featured=False)

    # Set specific ones to True
    updated_count = BusinessCategory.objects.filter(slug__in=featured_slugs).update(is_featured=True)

    print(f"Updated {updated_count} categories to be featured.")

    # Verify
    featured = BusinessCategory.objects.filter(is_featured=True).values_list('slug', flat=True)
    print(f"Currently featured: {list(featured)}")

if __name__ == '__main__':
    set_featured_categories()
