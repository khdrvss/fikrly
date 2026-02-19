# 🔐 Secrets Configuration Guide

## Current Status

| Secret | Status | Priority | Required For |
|--------|--------|----------|--------------|
| SECRET_KEY | ✅ Set | Critical | Django core |
| DB_PASSWORD | ✅ Set | Critical | Database access |
| TELEGRAM_BOT_TOKEN | ✅ Set | Optional | Notifications |
| TELEGRAM_ADMIN_CHAT_IDS | ✅ Set | Optional | Admin alerts |
| TELEGRAM_REVIEWS_CHAT_IDS | ✅ Set | Optional | Review alerts |
| EMAIL_HOST_USER | ❌ Placeholder | 🔴 High | Password reset, notifications |
| EMAIL_HOST_PASSWORD | ❌ Placeholder | 🔴 High | Email sending |
| ESKIZ_EMAIL | ❌ Placeholder | 🟡 Medium | Phone verification |
| ESKIZ_PASSWORD | ❌ Placeholder | 🟡 Medium | SMS sending |
| GOOGLE_CLIENT_ID | ❌ Placeholder | 🟡 Medium | Google OAuth login |
| GOOGLE_CLIENT_SECRET | ❌ Placeholder | 🟡 Medium | Google OAuth login |

---

## 🔴 CRITICAL - Configure These First

### 1. EMAIL Configuration (Gmail)

**Why needed:** Password resets, email verification, user notifications

**Step-by-step setup:**

#### Option A: Gmail (Easiest for testing)
```bash
# 1. Use your Gmail account
EMAIL_HOST_USER=your.email@gmail.com

# 2. Generate App Password:
#    - Go to https://myaccount.google.com/security
#    - Enable 2-Step Verification
#    - Search "App passwords" in settings
#    - Create app password for "Mail"
#    - Copy 16-character code (remove spaces)
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop  # Use without spaces: abcdefghijklmnop
```

#### Option B: SendGrid (Better for production)
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your-sendgrid-api-key-here
DEFAULT_FROM_EMAIL=noreply@fikrly.uz
```

**Get SendGrid API Key:**
1. Sign up at https://sendgrid.com (Free: 100 emails/day)
2. Settings → API Keys → Create API Key
3. Choose "Restricted Access" → Mail Send (Full Access)
4. Copy the key (starts with `SG.`)

#### Option C: Mailgun (Alternative)
```bash
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@mg.fikrly.uz
EMAIL_HOST_PASSWORD=your-mailgun-smtp-password
```

---

## 🟡 HIGH PRIORITY - Configure for Full Features

### 2. SMS Provider (Eskiz.uz) - Phone Authentication

**Why needed:** SMS verification for user registration (common in Uzbekistan)

**Setup:**
```bash
# 1. Register account
Visit: https://eskiz.uz/
Click: "Регистрация" (Registration)

# 2. Verify your business
- Submit business documents
- Add company details
- Wait for approval (usually 1-2 days)

# 3. Add balance
- Minimum: $5 (covers ~500 SMS)
- Payment: Click, Payme, or bank transfer

# 4. Get credentials
Dashboard → API → Copy credentials

ESKIZ_EMAIL=your-registered-email@example.com
ESKIZ_PASSWORD=your-eskiz-account-password
```

**Alternative SMS Providers:**
- **Twilio**: International, $0.0075/SMS in Uzbekistan
- **Playmobile**: Local Uzbek provider
- **SMS.uz**: Another local option

### 3. Google OAuth - Social Login

**Why needed:** Allow users to "Sign in with Google"

**Setup:**
```bash
# 1. Go to Google Cloud Console
https://console.cloud.google.com/

# 2. Create project
- Click "Select Project" → "New Project"
- Name: "Fikrly Production"
- Click "Create"

# 3. Enable Google+ API
- Go to "APIs & Services" → "Library"
- Search "Google+ API"
- Click "Enable"

# 4. Create OAuth credentials
- APIs & Services → Credentials
- Click "Create Credentials" → "OAuth client ID"
- Application type: Web application
- Name: Fikrly Production

# 5. Configure authorized URLs
Authorized JavaScript origins:
- https://fikrly.uz
- https://www.fikrly.uz
- http://localhost:8000 (for testing)

Authorized redirect URIs:
- https://fikrly.uz/accounts/google/login/callback/
- https://www.fikrly.uz/accounts/google/login/callback/
- http://localhost:8000/accounts/google/login/callback/

# 6. Copy credentials
GOOGLE_CLIENT_ID=123456789-abc123xyz789.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_secret_here_abc123xyz
```

---

## 🟢 OPTIONAL - Can Configure Later

### 4. Analytics & Monitoring

Already partially configured:
```bash
GA_MEASUREMENT_ID=G-VF0K77S81T  # ✅ Google Analytics ID present
```

### 5. Social Media Integration (if planned)
```bash
# Facebook OAuth (if adding Facebook login)
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret

# VK (VKontakte for Russian market)
VK_APP_ID=your-vk-app-id
VK_APP_SECRET=your-vk-app-secret
```

---

## 🔧 Testing Your Secrets

### Test Email Configuration
```bash
# In Django shell
python manage.py shell

from django.core.mail import send_mail
send_mail(
    'Test Email',
    'If you receive this, email is configured!',
    'noreply@fikrly.uz',
    ['your-test-email@gmail.com'],
)
# Should print: 1
# Check your email inbox
```

### Test SMS (Eskiz)
```python
python manage.py shell

from frontend.sms import send_sms_code
result = send_sms_code('+998901234567', '123456')
print(result)  # Should show success message
```

### Test Google OAuth
```bash
# 1. Start server
python manage.py runserver

# 2. Visit
http://localhost:8000/accounts/google/login/

# 3. Should redirect to Google login
# 4. After login, should redirect back to your site
```

---

## 📝 Quick Reference: What's Required for Each Feature

| Feature | Required Secrets |
|---------|------------------|
| **Basic site operation** | SECRET_KEY, DB_PASSWORD |
| **User registration (email)** | EMAIL_HOST_USER, EMAIL_HOST_PASSWORD |
| **User registration (phone)** | ESKIZ_EMAIL, ESKIZ_PASSWORD |
| **Password reset** | EMAIL_HOST_USER, EMAIL_HOST_PASSWORD |
| **Google login** | GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET |
| **Admin notifications** | TELEGRAM_BOT_TOKEN (✅ configured) |
| **Production HTTPS** | SSL Certificate (see below) |

---

## 🔒 SSL Certificate Setup

After configuring basic secrets, you'll need SSL for HTTPS:

### Option 1: Let's Encrypt (Free, Recommended)
```bash
# Using Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d fikrly.uz -d www.fikrly.uz

# Auto-renewal is configured automatically
```

### Option 2: Cloudflare (Free, Easy)
```bash
# 1. Sign up at cloudflare.com
# 2. Add your domain fikrly.uz
# 3. Update nameservers at your registrar
# 4. Enable "Full (strict)" SSL mode
# 5. Cloudflare provides SSL automatically
```

### Then update .env:
```bash
USE_HTTPS=True
SECURE_SSL_REDIRECT=True
```

---

## 🎯 Minimum Viable Production Setup

**Absolute minimum to go live:**
```bash
✅ SECRET_KEY (you have this)
✅ DB_PASSWORD (you have this)
✅ EMAIL_HOST_USER (⚠️ need to configure)
✅ EMAIL_HOST_PASSWORD (⚠️ need to configure)
🔒 SSL Certificate (need to generate)
```

**With these 5 items, you can:**
- ✅ Users can register with email
- ✅ Users can reset passwords
- ✅ Site runs securely over HTTPS
- ✅ Basic functionality works

**Optional for launch:**
- ESKIZ (can add SMS later)
- GOOGLE_CLIENT (can add social login later)

---

## 📋 Action Plan

### Today (30 minutes):
1. ✅ Configure Gmail App Password → Update EMAIL_HOST_USER/PASSWORD
2. ✅ Test email sending
3. ✅ Generate SSL certificate (Let's Encrypt)
4. ✅ Update USE_HTTPS=True

### This Week (optional):
1. Register Eskiz.uz account
2. Set up Google OAuth
3. Test all authentication flows

### Before Marketing:
1. Ensure all features work
2. Test on mobile devices
3. Load test with expected traffic

---

## 🚨 Security Reminders

1. **Never commit .env to git**
   ```bash
   # Check it's in .gitignore
   grep "^\.env$" .gitignore
   ```

2. **Rotate secrets regularly**
   - SECRET_KEY: Every 6 months or after breach
   - DB_PASSWORD: Every 3 months
   - API keys: When team members leave

3. **Use different secrets for dev/staging/prod**
   - .env.development
   - .env.staging
   - .env.production

4. **Store backups securely**
   - Don't email secrets
   - Use password manager (1Password, LastPass, Bitwarden)
   - Encrypt backup files

---

**Need help?** Each section above has step-by-step instructions. Start with email configuration - it's the most critical for launch!
