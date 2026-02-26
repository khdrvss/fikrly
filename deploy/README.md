# 🚀 Fikrly Production Deployment Guide

## 📋 Overview

This guide covers deploying Fikrly to a production VPS with maximum security, performance, and reliability.

## 🎯 What's Missing & What We Fixed

### ❌ Critical Issues Found (Now Fixed ✅)

1. **Security Vulnerabilities**
   - ❌ Silk profiler exposed in production → ✅ Now conditional (SILK_ENABLED)
   - ❌ No error email notifications → ✅ ADMINS configured
   - ❌ Email backend not configured → ✅ SMTP settings added
   - ❌ Session cookies not secure enough → ✅ Added SameSite attribute
   - ❌ No rate limiting at Nginx level → ✅ Added comprehensive rate limiting
   - ❌ Missing security headers → ✅ CSP, HSTS, XSS protection configured

2. **Infrastructure Missing**
   - ❌ No Gunicorn service → ✅ Created gunicorn.service
   - ❌ No Nginx configuration → ✅ Created production nginx.conf
   - ❌ No SSL setup → ✅ Added Let's Encrypt guide
   - ❌ No automated backups → ✅ Created backup.sh script
   - ❌ No health monitoring → ✅ Created monitor.sh script
   - ❌ No deployment script → ✅ Created deploy.sh

3. **Performance Optimizations**
   - ❌ No database indexes → ✅ Created optimization SQL
   - ❌ No Nginx caching → ✅ Added static file caching (1 year)
   - ❌ No compression → ✅ Gzip enabled in Nginx
   - ❌ No connection pooling → ✅ Gunicorn workers + threads configured

4. **Operational Issues**
   - ❌ No log rotation → ✅ Added logrotate config
   - ❌ No SSL renewal automation → ✅ Created ssl_renew.sh
   - ❌ No system monitoring → ✅ Monitoring cron jobs
   - ❌ No firewall configuration → ✅ UFW setup in initial_setup.sh
   - ❌ No Fail2ban → ✅ Included in hardening guide

## 📦 Files Created

### Deployment Scripts (10 files)
```
deploy/
├── DEPLOYMENT_CHECKLIST.md    # 100-item deployment checklist
├── SECURITY_HARDENING.md       # Complete security hardening guide
├── initial_setup.sh            # One-time VPS setup (run as root)
├── deploy.sh                   # Automated deployment script
├── backup.sh                   # Database + media backup
├── monitor.sh                  # Health monitoring (runs every 5 min)
├── ssl_renew.sh               # SSL certificate renewal
├── gunicorn.service           # Systemd service for Gunicorn
├── nginx.conf                 # Production Nginx configuration
└── database_optimization.sql  # PostgreSQL performance tuning
```

### Configuration Files
```
.env.production.example        # Complete production environment vars
requirements-prod.txt          # Production dependencies (Gunicorn, etc.)
```

## 🔧 Settings.py Improvements

### Added:
```python
# Error reporting
ADMINS = [('Admin', 'admin@fikrly.uz')]
MANAGERS = ADMINS

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# ... etc

# Conditional Silk profiler (disabled in production)
SILK_ENABLED = os.environ.get('SILK_ENABLED', str(DEBUG))

# Enhanced cookie security
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
```

## 🚀 Quick Deploy (Step by Step)

### Phase 1: VPS Setup (15 minutes)
```bash
# 1. SSH into your VPS
ssh root@YOUR_VPS_IP

# 2. Run initial setup
wget https://raw.githubusercontent.com/YOUR_REPO/deploy/initial_setup.sh
sudo bash initial_setup.sh

# 3. Clone repository
cd /var/www
git clone YOUR_REPO_URL fikrly
cd fikrly
```

### Phase 2: Application Setup (10 minutes)
```bash
# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt
pip install -r requirements-prod.txt

# 6. Configure environment
cp .env.production.example .env
nano .env  # Fill in all values

# 7. Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Copy to .env
```

### Phase 3: Database Setup (5 minutes)
```bash
# 8. Create database user and database (already done in initial_setup.sh)
# Update password in .env

# 9. Run migrations
python manage.py migrate

# 10. Create superuser
python manage.py createsuperuser

# 11. Collect static files
python manage.py collectstatic --noinput

# 12. Optimize database
sudo -u postgres psql fikrly_production < deploy/database_optimization.sql
```

### Phase 4: Web Server Setup (10 minutes)
```bash
# 13. Install Gunicorn service
sudo cp deploy/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn  # Check it's running

# 14. Install Nginx config
sudo cp deploy/nginx.conf /etc/nginx/sites-available/fikrly
sudo ln -s /etc/nginx/sites-available/fikrly /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx

# 15. Get SSL certificate
sudo certbot --nginx -d fikrly.uz -d www.fikrly.uz

# 16. Test HTTPS
curl https://fikrly.uz/health/
```

### Phase 5: Security & Monitoring (15 minutes)
```bash
# 17. Setup automated backups
sudo chmod +x deploy/*.sh
./deploy/install_backup_cron.sh
# Optional schedule override example:
# BACKUP_CRON_SCHEDULE="30 2 * * *" ./deploy/install_backup_cron.sh

# Add other monitoring jobs:
crontab -e
# Keep this line:
*/5 * * * * /var/www/fikrly/deploy/monitor.sh
0 3 * * 1 /var/www/fikrly/deploy/ssl_renew.sh

# 3-kunlik Telegram statistika hisobotini yoqish:
./deploy/install_stats_report_cron.sh
# Optional schedule override:
# STATS_REPORT_CRON_SCHEDULE="0 10 */3 * *" ./deploy/install_stats_report_cron.sh

# 18. Configure Fail2ban
# See deploy/SECURITY_HARDENING.md

# 19. Verify firewall
sudo ufw status

# 20. Test everything
curl -I https://fikrly.uz
curl https://fikrly.uz/health/
```

## 🔒 Security Checklist

### Critical (Do Before Going Live)
- [ ] `DEBUG=False` in `.env`
- [ ] Strong `SECRET_KEY` (minimum 50 chars random)
- [ ] Strong database password (minimum 32 chars)
- [ ] `ALLOWED_HOSTS` set to actual domain only
- [ ] SSL certificate installed and working
- [ ] Firewall enabled (only ports 22, 80, 443)
- [ ] SSH key authentication (disable password login)
- [ ] Change default SSH port
- [ ] Fail2ban installed and configured
- [ ] `SILK_ENABLED=False` in production
- [ ] Email error reporting working
- [ ] Backups automated and tested

### Important (Do Within First Week)
- [ ] Setup monitoring (UptimeRobot, Pingdom, etc.)
- [ ] Test backup restoration
- [ ] Configure log rotation
- [ ] Setup database connection pooling
- [ ] Optimize PostgreSQL settings
- [ ] Run security audit (`python manage.py check --deploy`)
- [ ] Test rate limiting
- [ ] Review all admin users
- [ ] Setup Google Analytics (if needed)
- [ ] Submit sitemap to Google Search Console

### Recommended (Do Within First Month)
- [ ] Setup CDN for static files (Cloudflare, etc.)
- [ ] Configure Redis for session storage
- [ ] Implement Celery for async tasks
- [ ] Setup application monitoring (Sentry alternatives)
- [ ] Load testing
- [ ] Penetration testing
- [ ] GDPR compliance review
- [ ] Privacy policy and terms of service

## 📊 Performance Optimizations Applied

### Nginx
- ✅ Gzip compression (text, CSS, JS, JSON)
- ✅ Static file caching (1 year)
- ✅ Media file caching (1 month)
- ✅ HTTP/2 enabled
- ✅ Browser caching headers
- ✅ Connection reuse

### Gunicorn
- ✅ 4 workers (2 × CPU cores)
- ✅ 2 threads per worker
- ✅ gthread worker class
- ✅ 60s timeout
- ✅ Unix socket (faster than TCP)

### Database
- ✅ Connection pooling ready
- ✅ Indexes on foreign keys
- ✅ Indexes on search fields
- ✅ PostgreSQL query optimization
- ✅ Slow query logging

### Django
- ✅ WhiteNoise for static files
- ✅ Template caching
- ✅ Database query optimization
- ✅ Lazy loading of heavy data
- ✅ Pagination on list views

## 🔍 Monitoring & Alerting

### Automated Monitoring (Every 5 Minutes)
- Gunicorn status
- Nginx status
- PostgreSQL status
- Redis status
- Health endpoint (HTTP 200)
- Disk space (alert at >85%)
- Memory usage (alert at >90%)
- Log file sizes

### Email Alerts Configured For:
- Service failures (Gunicorn, Nginx, PostgreSQL, Redis)
- Health check failures
- High disk usage (>90%)
- High memory usage (>90%)
- SSL certificate expiring (<14 days)
- Django errors (500 errors)
- Database errors

### Logs to Monitor:
- `/var/log/fikrly/gunicorn-error.log` - Application errors
- `/var/log/nginx/fikrly-error.log` - Web server errors
- `/var/log/fikrly/django.log` - Django application logs
- `/var/log/fikrly/errors.log` - Django ERROR level logs
- `/var/log/auth.log` - SSH login attempts
- `/var/log/fail2ban.log` - Banned IPs

## 🚨 Common Issues & Solutions

### 1. Static files not loading
```bash
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
sudo systemctl reload nginx
```

### 2. Database connection errors
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
python manage.py dbshell

# Check credentials in .env
```

### 3. Gunicorn won't start
```bash
# Check logs
sudo journalctl -u gunicorn -n 50

# Check socket file permissions
ls -la /run/gunicorn.sock

# Recreate socket
sudo systemctl restart gunicorn
```

### 4. 502 Bad Gateway
```bash
# Usually means Gunicorn is down
sudo systemctl status gunicorn
sudo systemctl restart gunicorn

# Check Nginx can connect to socket
sudo nginx -t
```

### 5. SSL certificate errors
```bash
# Renew manually
sudo certbot renew

# Check expiry
echo | openssl s_client -connect fikrly.uz:443 | openssl x509 -noout -dates
```

## 📈 Scaling Recommendations

### When to Scale:
- CPU usage consistently >70%
- Memory usage consistently >80%
- Response time >2 seconds
- Database connections maxed out
- Disk I/O bottleneck

### Vertical Scaling (Easier)
1. Upgrade VPS (more CPU/RAM)
2. Increase Gunicorn workers
3. Add database connection pooling
4. Optimize database queries

### Horizontal Scaling (When Needed)
1. Add application servers (load balancer)
2. Separate database server
3. Add Redis cluster for caching
4. Use CDN for static/media files
5. Implement Celery with separate workers

## 💰 Cost Estimates

### Minimum Setup
- VPS (4GB RAM): $20-30/month
- Domain: $10-15/year
- SSL Certificate: Free (Let's Encrypt)
- **Total: ~$25/month**

### Recommended Setup
- VPS (8GB RAM): $40-60/month
- Domain: $10-15/year
- Email service (SendGrid/Mailgun): $10-20/month
- Monitoring (UptimeRobot free tier): $0
- Backups (S3/DO Spaces): $5-10/month
- **Total: ~$60-90/month**

### Enterprise Setup
- Multiple servers: $200+/month
- Managed PostgreSQL: $50+/month
- Redis cluster: $30+/month
- CDN (Cloudflare Pro): $20/month
- Premium monitoring: $50+/month
- **Total: $350+/month**

## 📞 Support & Resources

### Documentation
- Django deployment: https://docs.djangoproject.com/en/5.2/howto/deployment/
- Gunicorn docs: https://docs.gunicorn.org/
- Nginx docs: https://nginx.org/en/docs/
- PostgreSQL docs: https://www.postgresql.org/docs/

### Security Testing Tools
- SSL Labs: https://www.ssllabs.com/ssltest/
- Security Headers: https://securityheaders.com/
- Mozilla Observatory: https://observatory.mozilla.org/

### Performance Testing
```bash
# Load testing with Apache Bench
ab -n 1000 -c 10 https://fikrly.uz/

# Load testing with wrk
wrk -t4 -c100 -d30s https://fikrly.uz/
```

## ✅ Final Checklist

Before announcing to users:
- [ ] All tests passing
- [ ] Error pages working (404, 500, 403)
- [ ] User registration/login working
- [ ] Email sending working (registration, password reset)
- [ ] SMS verification working
- [ ] Image uploads working
- [ ] Google OAuth working
- [ ] Search functionality working
- [ ] Rate limiting tested
- [ ] Health check endpoint responding
- [ ] SSL certificate valid (A+ on SSL Labs)
- [ ] Backups automated and tested
- [ ] Monitoring alerts working
- [ ] Admin panel accessible
- [ ] Mobile responsive
- [ ] All browser console errors fixed
- [ ] SEO meta tags present
- [ ] Sitemap submitted to Google
- [ ] Privacy policy published
- [ ] Terms of service published

## 🎉 You're Production Ready!

Your Fikrly platform now has:
- ✅ Bank-level security (HTTPS, rate limiting, firewall, Fail2ban)
- ✅ High performance (Nginx caching, Gunicorn, optimized database)
- ✅ Reliability (health monitoring, automated backups, auto-restart)
- ✅ Scalability (ready to handle thousands of users)
- ✅ Maintainability (automated deployments, comprehensive logging)

**Next Steps:**
1. Run through deployment checklist
2. Test everything thoroughly
3. Monitor logs for first week
4. Gather user feedback
5. Iterate and improve

Good luck with your launch! 🚀
