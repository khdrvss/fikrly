#!/usr/bin/env python
"""
Quick test script to verify email configuration
Run: python test_email.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
os.environ['DB_ENGINE'] = 'sqlite3'  # Use SQLite for testing
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 50)
print("📧 EMAIL CONFIGURATION TEST")
print("=" * 50)
print(f"Backend: {settings.EMAIL_BACKEND}")
print(f"Host: {settings.EMAIL_HOST}")
print(f"Port: {settings.EMAIL_PORT}")
print(f"User: {settings.EMAIL_HOST_USER}")
print(f"Password: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else '(not set)'}")
print("=" * 50)

# Check if configured
if settings.EMAIL_HOST_USER == 'your-email@gmail.com':
    print("❌ ERROR: Email not configured!")
    print("Please update EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env")
    exit(1)

if 'your-' in settings.EMAIL_HOST_PASSWORD.lower():
    print("❌ ERROR: App password not set!")
    print("Please update EMAIL_HOST_PASSWORD in .env with your Gmail App Password")
    exit(1)

# Get recipient email
test_email = input("\n📬 Enter email address to send test to: ").strip()
if not test_email or '@' not in test_email:
    print("❌ Invalid email address")
    exit(1)

print(f"\n📤 Sending test email to {test_email}...")

try:
    result = send_mail(
        subject='✅ Fikrly Email Test',
        message='If you received this, your email configuration is working correctly! 🎉',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[test_email],
        fail_silently=False,
    )
    
    if result == 1:
        print("✅ SUCCESS! Email sent successfully!")
        print(f"Check inbox at: {test_email}")
        print("\n🎉 Your email configuration is working!")
    else:
        print("⚠️  Email may not have been sent (result: {result})")
        
except Exception as e:
    print(f"❌ ERROR sending email: {e}")
    print("\nCommon issues:")
    print("1. App password not generated correctly")
    print("2. 2-Step Verification not enabled")
    print("3. Wrong email/password in .env")
    print("4. Gmail blocking 'less secure apps' (use App Password!)")
    exit(1)
