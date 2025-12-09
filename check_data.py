import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from frontend.models import Company, BusinessCategory

print(f"Companies count: {Company.objects.count()}")
print(f"Categories count: {BusinessCategory.objects.count()}")
