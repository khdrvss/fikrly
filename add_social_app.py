import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Configuration
PROVIDER = 'google'
NAME = 'Google'
CLIENT_ID = '812932714498-pb7t5j2tvgk10depcaan70e1bv3ivoae.apps.googleusercontent.com'
# REPLACE THIS WITH YOUR ACTUAL CLIENT SECRET
CLIENT_SECRET = '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'

def add_social_app():
    # 1. Ensure the Site exists and is correct
    site, created = Site.objects.get_or_create(id=1)
    site.domain = 'fikrly.uz'
    site.name = 'Fikrly'
    site.save()
    print(f"✅ Site configured: {site.domain}")

    # 2. Create or Update the SocialApp
    app, created = SocialApp.objects.get_or_create(
        provider=PROVIDER,
        defaults={
            'name': NAME,
            'client_id': CLIENT_ID,
            'secret': CLIENT_SECRET,
        }
    )

    if not created:
        app.client_id = CLIENT_ID
        app.secret = CLIENT_SECRET
        app.name = NAME
        app.save()
        print(f"🔄 Updated existing SocialApp: {app.name}")
    else:
        print(f"✅ Created new SocialApp: {app.name}")

    # 3. Link the App to the Site
    if site not in app.sites.all():
        app.sites.add(site)
        print(f"🔗 Linked {app.name} to {site.domain}")
    else:
        print(f"🔗 {app.name} is already linked to {site.domain}")

if __name__ == '__main__':
    if CLIENT_SECRET == 'YOUR_CLIENT_SECRET_HERE':
        print("⚠️  PLEASE UPDATE THE CLIENT_SECRET IN THIS SCRIPT BEFORE RUNNING!")
    else:
        add_social_app()
