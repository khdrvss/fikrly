import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()
client = Client()

# Create user
if not User.objects.filter(username='testuser').exists():
    user = User.objects.create_user(username='testuser', password='password')
else:
    user = User.objects.get(username='testuser')
    user.set_password('password')
    user.save()

# Login
logged_in = client.login(username='testuser', password='password')
print(f"Logged in: {logged_in}")

# Access view
try:
    url = reverse('review_submission')
    print(f"URL: {url}")
    response = client.get(url)
    print(f"Status code: {response.status_code}")
    if response.status_code == 302:
        print(f"Redirect URL: {response.url}")
except Exception as e:
    print(f"Error: {e}")
