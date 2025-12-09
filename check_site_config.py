import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

site = Site.objects.get(pk=1)
print(f"Site ID 1: domain={site.domain}, name={site.name}")

apps = SocialApp.objects.filter(provider='google')
for app in apps:
    print(f"SocialApp: name={app.name}, client_id={app.client_id}, sites={[s.domain for s in app.sites.all()]}")
