import os, django, urllib.request
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()
from django.conf import settings
print(f'DEBUG: {settings.DEBUG}')
print(f'MEDIA_ROOT: {settings.MEDIA_ROOT}')
from frontend.models import Company
try:
    c = Company.objects.get(name='Click')
    if c.logo:
        url = f'http://127.0.0.1:8000{c.logo.url}'
        print(f'Testing URL: {url}')
        try:
            code = urllib.request.urlopen(url).getcode()
            print(f'Status: {code}')
        except Exception as e:
            print(f'Error: {e}')
    else:
        print("No logo set for Click")
except Company.DoesNotExist:
    print("Company Click not found")
