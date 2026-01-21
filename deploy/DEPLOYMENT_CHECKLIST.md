# Production deployment checklist for Fikrly
# Complete this before deploying to VPS

## ✅ Pre-Deployment Checklist

### 1. Environment Variables
- [ ] Copy `.env.production.example` to `.env` on VPS
- [ ] Generate new SECRET_KEY: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS` with actual domain
- [ ] Set strong database password
- [ ] Configure email settings (SMTP)
- [ ] Add Google OAuth credentials
- [ ] Configure Telegram bot tokens
- [ ] Set ESKIZ.UZ SMS credentials

### 2. Database
- [ ] Create PostgreSQL database on VPS
- [ ] Create database user with strong password
- [ ] Grant proper permissions
- [ ] Test connection from Django
- [ ] Set up automatic backups (cron job)

### 3. Static & Media Files
- [ ] Run `python manage.py collectstatic`
- [ ] Configure Nginx to serve static files
- [ ] Configure Nginx to serve media files
- [ ] Set proper file permissions (www-data)
- [ ] Test file uploads

### 4. SSL/HTTPS
- [ ] Install Certbot
- [ ] Obtain SSL certificate: `sudo certbot --nginx -d fikrly.uz -d www.fikrly.uz`
- [ ] Test SSL: https://www.ssllabs.com/ssltest/
- [ ] Enable auto-renewal: `sudo systemctl enable certbot.timer`
- [ ] Verify HSTS headers

### 5. Web Server (Nginx)
- [ ] Copy `deploy/nginx.conf` to `/etc/nginx/sites-available/fikrly`
- [ ] Create symlink: `sudo ln -s /etc/nginx/sites-available/fikrly /etc/nginx/sites-enabled/`
- [ ] Test config: `sudo nginx -t`
- [ ] Restart Nginx: `sudo systemctl restart nginx`
- [ ] Enable on boot: `sudo systemctl enable nginx`

### 6. Application Server (Gunicorn)
- [ ] Install gunicorn: `pip install gunicorn`
- [ ] Copy `deploy/gunicorn.service` to `/etc/systemd/system/`
- [ ] Reload systemd: `sudo systemctl daemon-reload`
- [ ] Start Gunicorn: `sudo systemctl start gunicorn`
- [ ] Enable on boot: `sudo systemctl enable gunicorn`
- [ ] Check status: `sudo systemctl status gunicorn`

### 7. Security
- [ ] Configure UFW firewall (SSH, HTTP, HTTPS only)
- [ ] Install and configure Fail2ban
- [ ] Disable Silk profiler in production (SILK_ENABLED=False)
- [ ] Remove debug toolbar
- [ ] Review ALLOWED_HOSTS
- [ ] Check CSRF_TRUSTED_ORIGINS
- [ ] Enable secure cookies (SESSION_COOKIE_SECURE=True)
- [ ] Test rate limiting
- [ ] Review admin user permissions

### 8. Monitoring & Logging
- [ ] Set up log rotation (logrotate)
- [ ] Configure error email notifications (ADMINS setting)
- [ ] Test health check endpoint (/health/)
- [ ] Set up uptime monitoring (optional: UptimeRobot)
- [ ] Configure database query logging
- [ ] Set up application monitoring

### 9. Backups
- [ ] Make backup script executable: `chmod +x deploy/backup.sh`
- [ ] Test manual backup: `./deploy/backup.sh`
- [ ] Add to crontab: `crontab -e` → `0 2 * * * /var/www/fikrly/deploy/backup.sh`
- [ ] Test backup restoration
- [ ] Configure remote backup storage (optional)

### 10. Performance
- [ ] Enable Redis caching
- [ ] Configure PostgreSQL connection pooling
- [ ] Optimize database indexes
- [ ] Enable Nginx compression (gzip)
- [ ] Set proper cache headers
- [ ] Test page load times
- [ ] Run load testing (optional: Apache Bench, wrk)

### 11. Django Admin
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Access admin at https://fikrly.uz/admin/
- [ ] Review admin permissions
- [ ] Test admin dashboard
- [ ] Test bulk actions

### 12. Final Testing
- [ ] Test user registration/login
- [ ] Test business creation
- [ ] Test review submission
- [ ] Test image uploads
- [ ] Test email sending
- [ ] Test SMS sending (phone verification)
- [ ] Test Google OAuth login
- [ ] Test search functionality
- [ ] Test API endpoints
- [ ] Test rate limiting (try spamming)
- [ ] Test error pages (404, 500, 403)
- [ ] Test mobile responsiveness
- [ ] Check browser console for errors

### 13. SEO & Analytics
- [ ] Submit sitemap to Google Search Console
- [ ] Verify robots.txt: https://fikrly.uz/robots.txt
- [ ] Set up Google Analytics (if needed)
- [ ] Test meta tags and Open Graph tags
- [ ] Verify canonical URLs

### 14. Post-Deployment
- [ ] Monitor logs for errors: `tail -f /var/log/fikrly/gunicorn-error.log`
- [ ] Monitor Nginx logs: `tail -f /var/log/nginx/fikrly-error.log`
- [ ] Check disk space: `df -h`
- [ ] Monitor database size
- [ ] Review user feedback
- [ ] Plan for scaling

## 🚨 Critical Security Fixes Applied

### Already Implemented ✅
1. ✅ Environment-based configuration (.env)
2. ✅ DEBUG=False in production
3. ✅ ALLOWED_HOSTS restriction
4. ✅ HTTPS enforcement (SECURE_SSL_REDIRECT)
5. ✅ Secure cookies (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE)
6. ✅ HSTS headers (1 year)
7. ✅ Security headers (CSP, XSS, referrer-policy)
8. ✅ Rate limiting on API endpoints
9. ✅ Health check endpoint
10. ✅ Structured logging with rotation
11. ✅ Custom error pages (no debug info leakage)

### Still Missing ⚠️
1. ⚠️ ADMINS setting for error emails
2. ⚠️ Email backend configuration
3. ⚠️ Gunicorn configuration
4. ⚠️ Nginx configuration
5. ⚠️ SSL certificate
6. ⚠️ Automated backups
7. ⚠️ Database connection pooling
8. ⚠️ Celery for async tasks (optional)

## 📊 Recommended VPS Specs

**Minimum:**
- 2 CPU cores
- 4 GB RAM
- 40 GB SSD
- Ubuntu 22.04 or 24.04 LTS

**Recommended:**
- 4 CPU cores
- 8 GB RAM
- 80 GB SSD
- Ubuntu 24.04 LTS

## 🛠️ Quick Deploy Commands

```bash
# 1. Initial VPS setup (run once as root)
sudo bash deploy/initial_setup.sh

# 2. Clone repository
cd /var/www
sudo git clone YOUR_REPO_URL fikrly
sudo chown -R www-data:www-data fikrly

# 3. Setup environment
cd /var/www/fikrly
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configure environment
cp .env.production.example .env
nano .env  # Fill in actual values

# 5. Database setup
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic

# 6. Install services
sudo cp deploy/gunicorn.service /etc/systemd/system/
sudo cp deploy/nginx.conf /etc/nginx/sites-available/fikrly
sudo ln -s /etc/nginx/sites-available/fikrly /etc/nginx/sites-enabled/
sudo systemctl daemon-reload
sudo systemctl enable gunicorn nginx
sudo systemctl start gunicorn
sudo nginx -t && sudo systemctl restart nginx

# 7. Get SSL certificate
sudo certbot --nginx -d fikrly.uz -d www.fikrly.uz

# 8. Test
curl https://fikrly.uz/health/
```

## 📞 Support

If you encounter issues during deployment:
1. Check logs: `journalctl -u gunicorn -f`
2. Check Nginx: `sudo nginx -t`
3. Check permissions: `ls -la /var/www/fikrly`
4. Verify .env file exists and has correct values
5. Test database connection: `python manage.py dbshell`
