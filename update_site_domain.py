import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.sites.models import Site

def check_and_update_site():
    try:
        site = Site.objects.get(pk=1)
        print(f"Current Site (ID=1): domain='{site.domain}', name='{site.name}'")

        if site.domain != 'fikrly.uz':
            print("Updating Site object to 'fikrly.uz'...")
            site.domain = 'fikrly.uz'
            site.name = 'Fikrly'
            site.save()
            print(f"Updated Site (ID=1): domain='{site.domain}', name='{site.name}'")
        else:
            print("Site object is already correct.")

    except Site.DoesNotExist:
        print("Site with ID=1 does not exist. Creating it...")
        Site.objects.create(pk=1, domain='fikrly.uz', name='Fikrly')
        print("Created Site (ID=1): domain='fikrly.uz', name='Fikrly'")

if __name__ == '__main__':
    check_and_update_site()
