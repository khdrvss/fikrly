# Security Hardening Checklist for Fikrly VPS

## 🔒 Operating System Security

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
```

### 2. Configure Automatic Security Updates
```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 3. SSH Hardening
Edit `/etc/ssh/sshd_config`:
```bash
sudo nano /etc/ssh/sshd_config
```

Add/modify these lines:
```
# Disable root login
PermitRootLogin no

# Use SSH key authentication only
PasswordAuthentication no
PubkeyAuthentication yes

# Disable empty passwords
PermitEmptyPasswords no

# Limit users who can SSH
AllowUsers deployer

# Change default port (optional but recommended)
Port 2222

# Disable X11 forwarding
X11Forwarding no

# Set idle timeout
ClientAliveInterval 300
ClientAliveCountMax 2
```

Restart SSH:
```bash
sudo systemctl restart sshd
```

### 4. Install and Configure Fail2ban
```bash
sudo apt install fail2ban -y
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```

Add custom jails:
```ini
[sshd]
enabled = true
port = ssh,2222
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/fikrly-error.log
maxretry = 5
bantime = 600

[nginx-noscript]
enabled = true
filter = nginx-noscript
logpath = /var/log/nginx/fikrly-access.log
maxretry = 3
```

Create filter for nginx rate limiting:
```bash
sudo nano /etc/fail2ban/filter.d/nginx-limit-req.conf
```
```ini
[Definition]
failregex = limiting requests, excess:.* by zone.*client: <HOST>
ignoreregex =
```

Restart Fail2ban:
```bash
sudo systemctl restart fail2ban
sudo fail2ban-client status
```

### 5. Configure UFW Firewall
```bash
# Reset UFW
sudo ufw --force reset

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (adjust port if changed)
sudo ufw allow 2222/tcp comment 'SSH'

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# Rate limit SSH
sudo ufw limit 2222/tcp

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status verbose
```

### 6. File Permissions
```bash
# Project files
sudo chown -R www-data:www-data /var/www/fikrly
sudo chmod -R 755 /var/www/fikrly
sudo chmod -R 644 /var/www/fikrly/staticfiles/*

# Sensitive files
sudo chmod 600 /var/www/fikrly/.env

# Scripts
sudo chmod +x /var/www/fikrly/deploy/*.sh

# Logs
sudo chown -R www-data:www-data /var/log/fikrly
sudo chmod -R 640 /var/log/fikrly/*
```

### 7. Disable Unused Services
```bash
# List all running services
systemctl list-units --type=service --state=running

# Disable unnecessary services (example)
sudo systemctl disable bluetooth
sudo systemctl stop bluetooth
```

## 🗄️ Database Security

### 1. PostgreSQL Hardening
Edit `/etc/postgresql/14/main/postgresql.conf`:
```bash
sudo nano /etc/postgresql/14/main/postgresql.conf
```

Set:
```
# Only listen on localhost
listen_addresses = 'localhost'

# Limit connections
max_connections = 100

# Enable logging
log_connections = on
log_disconnections = on
log_duration = on
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '

# Enable slow query logging
log_min_duration_statement = 1000  # Log queries over 1 second
```

Edit `/etc/postgresql/14/main/pg_hba.conf`:
```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

Set:
```
# Local connections only
local   all             postgres                                peer
local   all             fikrly_user                             md5
host    fikrly_production  fikrly_user  127.0.0.1/32           md5
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### 2. Strong Database Password
```bash
sudo -u postgres psql
```
```sql
ALTER USER fikrly_user WITH PASSWORD 'VERY_STRONG_PASSWORD_HERE_MIN_32_CHARS';
```

## 🌐 Web Server Security

### 1. Nginx Security Headers (already in deploy/nginx.conf)
Verify these headers are set:
- Strict-Transport-Security
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Referrer-Policy
- Content-Security-Policy

### 2. Hide Nginx Version
Edit `/etc/nginx/nginx.conf`:
```bash
sudo nano /etc/nginx/nginx.conf
```
Add:
```nginx
http {
    server_tokens off;
    ...
}
```

### 3. Rate Limiting (already in deploy/nginx.conf)
Verify rate limit zones are configured.

## 🔐 SSL/TLS Security

### 1. Strong SSL Configuration (already in deploy/nginx.conf)
- TLS 1.2 and 1.3 only
- Strong cipher suites
- Perfect Forward Secrecy
- OCSP Stapling

### 2. Test SSL Configuration
```bash
# Online test
https://www.ssllabs.com/ssltest/analyze.html?d=fikrly.uz

# Command line test
curl -I https://fikrly.uz
```

## 📧 Application Security

### 1. Django Settings Checklist
- ✅ DEBUG=False
- ✅ SECRET_KEY from environment
- ✅ ALLOWED_HOSTS restricted
- ✅ SECURE_SSL_REDIRECT=True
- ✅ SESSION_COOKIE_SECURE=True
- ✅ CSRF_COOKIE_SECURE=True
- ✅ SECURE_HSTS_SECONDS set
- ✅ X_FRAME_OPTIONS set

### 2. Run Django Security Check
```bash
cd /var/www/fikrly
source venv/bin/activate
python manage.py check --deploy
```

### 3. Disable Debug Tools in Production
```bash
# In .env file
SILK_ENABLED=False
DEBUG=False
```

## 🔍 Monitoring & Logging

### 1. Setup Log Rotation
Create `/etc/logrotate.d/fikrly`:
```bash
sudo nano /etc/logrotate.d/fikrly
```
```
/var/log/fikrly/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    sharedscripts
    postrotate
        systemctl reload gunicorn > /dev/null 2>&1 || true
    endscript
}

/var/log/nginx/fikrly-*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    sharedscripts
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}
```

### 2. Monitor Logs Regularly
```bash
# Watch Gunicorn errors
sudo tail -f /var/log/fikrly/gunicorn-error.log

# Watch Nginx errors
sudo tail -f /var/log/nginx/fikrly-error.log

# Watch Django logs
sudo tail -f /var/log/fikrly/django.log

# Watch auth attempts
sudo tail -f /var/log/auth.log

# Check Fail2ban
sudo fail2ban-client status sshd
```

### 3. Setup Monitoring Cron Jobs
```bash
sudo crontab -e
```
Add:
```bash
# System health check every 5 minutes
*/5 * * * * /var/www/fikrly/deploy/monitor.sh

# SSL certificate check weekly
0 3 * * 1 /var/www/fikrly/deploy/ssl_renew.sh

# Database backup daily at 2 AM
0 2 * * * /var/www/fikrly/deploy/backup.sh

# Clean old exports weekly
0 3 * * 0 cd /var/www/fikrly && source venv/bin/activate && python manage.py clean_expired_exports

# Clean old sessions weekly
0 4 * * 0 cd /var/www/fikrly && source venv/bin/activate && python manage.py clearsessions
```

## 🛡️ Additional Hardening

### 1. Install ModSecurity (Optional)
```bash
sudo apt install libapache2-mod-security2 -y
# Configure OWASP rules
```

### 2. Install rkhunter (Rootkit Detection)
```bash
sudo apt install rkhunter -y
sudo rkhunter --update
sudo rkhunter --check
```

### 3. Setup Intrusion Detection (Optional)
```bash
sudo apt install aide -y
sudo aideinit
```

### 4. Kernel Hardening
Edit `/etc/sysctl.conf`:
```bash
sudo nano /etc/sysctl.conf
```
Add:
```
# IP Forwarding
net.ipv4.ip_forward = 0

# Ignore ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0

# Ignore source routed packets
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# Enable SYN cookies
net.ipv4.tcp_syncookies = 1

# Log suspicious packets
net.ipv4.conf.all.log_martians = 1

# Ignore ICMP ping requests
net.ipv4.icmp_echo_ignore_all = 1
```

Apply:
```bash
sudo sysctl -p
```

## 📊 Regular Security Tasks

### Daily
- [ ] Check logs for suspicious activity
- [ ] Review Fail2ban bans: `sudo fail2ban-client status`
- [ ] Monitor disk space: `df -h`
- [ ] Check running processes: `htop`

### Weekly
- [ ] Review system updates: `sudo apt update && sudo apt list --upgradable`
- [ ] Check SSL certificate expiry
- [ ] Review database slow queries
- [ ] Analyze access logs for unusual patterns

### Monthly
- [ ] Full security audit
- [ ] Review user accounts and permissions
- [ ] Check backup integrity (test restoration)
- [ ] Update dependencies: `pip list --outdated`
- [ ] Run security scanners (nmap, nikto)

### Quarterly
- [ ] Password rotation
- [ ] Review firewall rules
- [ ] Penetration testing (if applicable)
- [ ] Disaster recovery drill

## 🚨 Incident Response Plan

1. **Detection**: Monitor logs, alerts, uptime monitors
2. **Containment**: Isolate affected systems
3. **Investigation**: Analyze logs, identify attack vector
4. **Recovery**: Restore from backups, patch vulnerabilities
5. **Post-mortem**: Document incident, improve defenses

## 📞 Emergency Contacts
- Server Provider Support: [CONTACT]
- Database Admin: [CONTACT]
- Security Team: [CONTACT]
