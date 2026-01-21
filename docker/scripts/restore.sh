#!/bin/bash
# Restore script for Docker containers

set -e

if [ -z "$1" ]; then
    echo "Usage: ./docker/scripts/restore.sh <backup_date>"
    echo "Example: ./docker/scripts/restore.sh 20260121_150000"
    echo ""
    echo "Available backups:"
    ls -1 ./backups/ | grep -E "db_backup|media_backup" | sed 's/.*_\([0-9_]*\)\..*/\1/' | sort -u
    exit 1
fi

BACKUP_DATE=$1
BACKUP_DIR="./backups"

echo "⚠️  WARNING: This will overwrite current data!"
read -p "Are you sure you want to restore from $BACKUP_DATE? (yes/no): " -r
if [[ ! $REPLY =~ ^yes$ ]]; then
    echo "Restore cancelled."
    exit 0
fi

# Restore database
if [ -f "$BACKUP_DIR/db_backup_$BACKUP_DATE.sql.gz" ]; then
    echo "🗄️  Restoring database..."
    gunzip < "$BACKUP_DIR/db_backup_$BACKUP_DATE.sql.gz" | \
        docker-compose exec -T db psql -U $DB_USER $DB_NAME
    echo "✅ Database restored!"
else
    echo "❌ Database backup not found: $BACKUP_DIR/db_backup_$BACKUP_DATE.sql.gz"
fi

# Restore media files
if [ -f "$BACKUP_DIR/media_backup_$BACKUP_DATE.tar.gz" ]; then
    echo "📸 Restoring media files..."
    docker run --rm -v fikrly-1_media_volume:/data -v $(pwd)/$BACKUP_DIR:/backup alpine \
        sh -c "rm -rf /data/* && tar xzf /backup/media_backup_$BACKUP_DATE.tar.gz -C /data"
    echo "✅ Media files restored!"
else
    echo "❌ Media backup not found: $BACKUP_DIR/media_backup_$BACKUP_DATE.tar.gz"
fi

echo "✅ Restore complete!"
