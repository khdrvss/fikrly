import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'manjaro'
password = 'manjaro'
email = 'manjaro@example.com'

try:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"Successfully reset password for user '{username}' to '{password}'")
except User.DoesNotExist:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Successfully created superuser '{username}' with password '{password}'")
