import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
try:
    u = User.objects.get(username='manjaro')
    u.delete()
    print("Deleted user manjaro")
except User.DoesNotExist:
    print("User manjaro does not exist")
