#!/bin/bash
# Backup script for Docker containers

set -e

# Load environment variables from .env file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
fi

# Set defaults from environment
DB_USER=${POSTGRES_USER:-fikrly_user}
DB_NAME=${POSTGRES_DB:-fikrly_db}

BACKUP_DIR="$PROJECT_DIR/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "📦 Starting backup process..."

# Backup PostgreSQL database
echo "🗄️  Backing up database..."
cd "$PROJECT_DIR" && docker compose exec -T db pg_dump -U $DB_USER $DB_NAME > "$BACKUP_DIR/db_backup_$DATE.sql"
gzip "$BACKUP_DIR/db_backup_$DATE.sql"

# Backup media files
echo "📸 Backing up media files..."
docker run --rm -v fikrly-1_media_volume:/data -v $(pwd)/$BACKUP_DIR:/backup alpine \
    tar czf /backup/media_backup_$DATE.tar.gz -C /data .

echo "✅ Backup complete!"
echo "Files:"
ls -lh $BACKUP_DIR/*_$DATE.*

# Clean old backups (keep last 30 days)
echo "🗑️  Cleaning old backups..."
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete
find $BACKUP_DIR -name "media_backup_*.tar.gz" -mtime +30 -delete

echo "✅ Backup process finished!"
