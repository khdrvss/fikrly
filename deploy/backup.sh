#!/bin/bash
# Database and media backup script for Fikrly
# Add to crontab: 0 2 * * * /var/www/fikrly/deploy/backup.sh

set -e

# Configuration
PROJECT_DIR="/var/www/fikrly"
BACKUP_DIR="/var/backups/fikrly"
DATE=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=30

# Database credentials (from .env)
source $PROJECT_DIR/.env
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
echo "📦 Backing up database..."
PGPASSWORD=$DB_PASSWORD pg_dump \
    -U $DB_USER \
    -h localhost \
    -F c \
    -b \
    -v \
    -f "$BACKUP_DIR/db_backup_$DATE.dump" \
    $DB_NAME

# Compress media files
echo "📦 Backing up media files..."
tar -czf "$BACKUP_DIR/media_backup_$DATE.tar.gz" \
    -C $PROJECT_DIR media/ \
    --exclude='*.pyc' \
    --exclude='__pycache__'

# Remove old backups
echo "🗑️  Removing backups older than $KEEP_DAYS days..."
find $BACKUP_DIR -name "db_backup_*.dump" -mtime +$KEEP_DAYS -delete
find $BACKUP_DIR -name "media_backup_*.tar.gz" -mtime +$KEEP_DAYS -delete

# List backup sizes
echo "✅ Backup complete!"
echo ""
echo "📊 Current backups:"
du -sh $BACKUP_DIR/*_$DATE.* || true

# Optional: Upload to remote storage (uncomment if using)
# echo "☁️  Uploading to remote storage..."
# rclone copy $BACKUP_DIR/db_backup_$DATE.dump remote:fikrly-backups/
# rclone copy $BACKUP_DIR/media_backup_$DATE.tar.gz remote:fikrly-backups/
