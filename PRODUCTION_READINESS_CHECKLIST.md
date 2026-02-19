# Production Readiness Checklist

## ✅ COMPLETED
- [x] Applied all database migrations
- [x] Updated security-critical packages (Pillow, cryptography, PyJWT)
- [x] Created test settings for local development

## 🔴 CRITICAL - Do Before Production Deploy

### 1. Environment Configuration (15 mins)
- [ ] Generate strong SECRET_KEY (use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- [ ] Update `.env.production` with actual secrets
- [ ] Configure database credentials (strong passwords)
- [ ] Set up email provider credentials (SMTP)
- [ ] Configure allowed hosts for your domain

### 2. Security Verification (10 mins)
- [ ] Ensure DEBUG=False in .env.production
- [ ] Verify USE_HTTPS=True is set
- [ ] Test SSL certificate is valid
- [ ] Run: `python manage.py check --deploy` with production settings

### 3. Static Files & Media (10 mins)
```bash
python manage.py collectstatic --noinput
```
- [ ] Verify collectstatic works
- [ ] Ensure media directory has correct permissions
- [ ] Configure nginx/CDN for static files (if applicable)

### 4. Database Production Setup (15 mins)
```bash
# In Docker environment
docker-compose -f docker-compose.prod.yml up -d db
docker-compose -f docker-compose.prod.yml exec db psql -U fikrly_user -d fikrly_db
# Run: \l to verify database exists
```
- [ ] PostgreSQL database created
- [ ] Run migrations on production DB
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Apply database optimizations from deploy/database_optimization.sql

## 🟡 HIGH PRIORITY - First Week

### 5. Monitoring & Logging (1 hour)
- [ ] Configure error reporting (set ADMINS in settings)
- [ ] Set up log rotation
- [ ] Enable health check endpoint
- [ ] Configure uptime monitoring

### 6. Backups (30 mins)
- [ ] Test backup script: `bash deploy/backup.sh`
- [ ] Set up automated backup cron job
- [ ] Verify backup restoration works
- [ ] Configure offsite backup storage

### 7. Performance Testing (1 hour)
- [ ] Load test with expected traffic
- [ ] Monitor database query performance (django-silk)
- [ ] Optimize slow queries
- [ ] Configure Redis cache properly

## 🟢 RECOMMENDED - First Month

### 8. Dependency Updates (2 hours)
⚠️ Test thoroughly in staging first!
- [ ] Plan Django 5.2 → 6.0 upgrade path
- [ ] Update gunicorn: 23.0.0 → 25.1.0
- [ ] Update django-allauth and other packages
- [ ] Run full test suite after updates

### 9. CI/CD Setup (2 hours)
- [ ] Configure GitHub Actions / GitLab CI
- [ ] Automate testing on PRs
- [ ] Set up staging environment
- [ ] Create deployment pipeline

### 10. Documentation (1 hour)
- [ ] Document production deployment process
- [ ] Create runbook for common issues
- [ ] Document environment variables
- [ ] Update README with production setup

---

## Quick Commands Reference

### Generate Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Production Deploy Check
```bash
DEBUG=False USE_HTTPS=True python manage.py check --deploy
```

### Collect Static Files
```bash
python manage.py collectstatic --no-input --clear
```

### Start Production Stack
```bash
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### Backup Database
```bash
bash deploy/backup.sh
```

### Monitor Logs
```bash
docker-compose -f docker-compose.prod.yml logs -f web
```

---

## Testing Before Go-Live

1. **Smoke Tests**
   - [ ] Homepage loads
   - [ ] User can register/login
   - [ ] Company creation works
   - [ ] Review submission works
   - [ ] Admin panel accessible

2. **Security Tests**
   - [ ] HTTPS enforced
   - [ ] CSRF protection working
   - [ ] Rate limiting active
   - [ ] No sensitive data in logs

3. **Performance Tests**
   - [ ] Page load < 2 seconds
   - [ ] API responses < 500ms
   - [ ] Database queries optimized
   - [ ] Static files served efficiently

---

**Last Updated:** February 17, 2026
