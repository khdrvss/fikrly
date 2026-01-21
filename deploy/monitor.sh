#!/bin/bash
# System monitoring and health check script
# Add to crontab: */5 * * * * /var/www/fikrly/deploy/monitor.sh

set -e

PROJECT_DIR="/var/www/fikrly"
LOG_FILE="/var/log/fikrly/monitor.log"
ALERT_EMAIL="admin@fikrly.uz"

# Log timestamp
echo "[$(date '+%Y-%m-%d %H:%M:%S')]" >> $LOG_FILE

# Check if Gunicorn is running
if ! systemctl is-active --quiet gunicorn; then
    echo "❌ Gunicorn is down! Attempting restart..." >> $LOG_FILE
    systemctl restart gunicorn
    echo "Gunicorn was down and has been restarted at $(date)" | mail -s "ALERT: Gunicorn Down" $ALERT_EMAIL || true
fi

# Check if Nginx is running
if ! systemctl is-active --quiet nginx; then
    echo "❌ Nginx is down! Attempting restart..." >> $LOG_FILE
    systemctl restart nginx
    echo "Nginx was down and has been restarted at $(date)" | mail -s "ALERT: Nginx Down" $ALERT_EMAIL || true
fi

# Check if PostgreSQL is running
if ! systemctl is-active --quiet postgresql; then
    echo "❌ PostgreSQL is down! Attempting restart..." >> $LOG_FILE
    systemctl restart postgresql
    echo "PostgreSQL was down and has been restarted at $(date)" | mail -s "ALERT: PostgreSQL Down" $ALERT_EMAIL || true
fi

# Check if Redis is running
if ! systemctl is-active --quiet redis-server; then
    echo "❌ Redis is down! Attempting restart..." >> $LOG_FILE
    systemctl restart redis-server
    echo "Redis was down and has been restarted at $(date)" | mail -s "ALERT: Redis Down" $ALERT_EMAIL || true
fi

# Check application health endpoint
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://fikrly.uz/health/ || echo "000")
if [ "$HTTP_CODE" != "200" ]; then
    echo "❌ Health check failed with HTTP $HTTP_CODE" >> $LOG_FILE
    echo "Health check endpoint returned HTTP $HTTP_CODE at $(date)" | mail -s "ALERT: Health Check Failed" $ALERT_EMAIL || true
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    echo "⚠️  Disk usage is at ${DISK_USAGE}%" >> $LOG_FILE
    if [ $DISK_USAGE -gt 90 ]; then
        echo "Disk usage is critically high at ${DISK_USAGE}% on $(date)" | mail -s "ALERT: Low Disk Space" $ALERT_EMAIL || true
    fi
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2 {printf "%.0f", $3/$2 * 100}')
if [ $MEM_USAGE -gt 90 ]; then
    echo "⚠️  Memory usage is at ${MEM_USAGE}%" >> $LOG_FILE
    echo "Memory usage is high at ${MEM_USAGE}% on $(date)" | mail -s "WARNING: High Memory Usage" $ALERT_EMAIL || true
fi

# Check log file sizes (prevent runaway logs)
if [ -f /var/log/fikrly/django.log ]; then
    LOG_SIZE=$(du -m /var/log/fikrly/django.log | cut -f1)
    if [ $LOG_SIZE -gt 500 ]; then
        echo "⚠️  Log file is ${LOG_SIZE}MB" >> $LOG_FILE
        # Rotate manually if needed
        mv /var/log/fikrly/django.log /var/log/fikrly/django.log.old
        touch /var/log/fikrly/django.log
        chown www-data:www-data /var/log/fikrly/django.log
    fi
fi

echo "✅ All checks passed" >> $LOG_FILE
