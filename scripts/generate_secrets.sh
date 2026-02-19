#!/bin/bash
# Generate secure secrets for production

echo "==================================="
echo "🔐 FIKRLY SECRETS GENERATOR"
echo "==================================="
echo ""

# Django Secret Key
echo "1. DJANGO SECRET_KEY (128 chars):"
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
echo ""

# Database Password
echo "2. DATABASE PASSWORD (64 chars):"
openssl rand -hex 32
echo ""

# General Secret (32 chars)
echo "3. GENERAL SECRET (32 chars):"
openssl rand -hex 16
echo ""

# Session Secret
echo "4. SESSION SECRET (64 chars):"
openssl rand -base64 48
echo ""

echo "==================================="
echo "✅ Copy these to your .env file"
echo "⚠️  Keep these secrets secure!"
echo "==================================="
