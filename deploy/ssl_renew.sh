#!/bin/bash
# SSL certificate renewal and monitoring
# Add to crontab: 0 3 * * 1 /var/www/fikrly/deploy/ssl_renew.sh

set -e

echo "🔐 Checking SSL certificate renewal..."

# Attempt renewal (will only renew if within 30 days of expiry)
certbot renew --quiet --no-self-upgrade

# Reload Nginx if certificates were renewed
if [ -f /var/log/letsencrypt/letsencrypt.log ]; then
    if tail -n 50 /var/log/letsencrypt/letsencrypt.log | grep -q "Certificate not yet due for renewal"; then
        echo "✅ Certificate is still valid"
    else
        echo "🔄 Certificate renewed, reloading Nginx..."
        systemctl reload nginx
        echo "📧 Sending notification email..."
        echo "SSL certificate for fikrly.uz was renewed on $(date)" | mail -s "SSL Certificate Renewed" admin@fikrly.uz || true
    fi
fi

# Check certificate expiry
EXPIRY=$(echo | openssl s_client -connect fikrly.uz:443 -servername fikrly.uz 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))

echo "📅 Certificate expires in $DAYS_LEFT days"

# Warn if less than 14 days
if [ $DAYS_LEFT -lt 14 ]; then
    echo "⚠️  WARNING: Certificate expires soon!"
    echo "SSL certificate for fikrly.uz expires in $DAYS_LEFT days!" | mail -s "SSL Certificate Expiry Warning" admin@fikrly.uz || true
fi
