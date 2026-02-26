#!/usr/bin/env bash
# Nightly PostgreSQL backup + restore verification for Fikrly (Docker Compose)
# Suggested cron: 0 2 * * * /home/maymun/fikrly/deploy/backup.sh >> /home/maymun/fikrly/logs/backup.log 2>&1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups/nightly}"
KEEP_DAYS="${KEEP_DAYS:-30}"
DATE="$(date +%Y%m%d_%H%M%S)"
DB_SERVICE="${DB_SERVICE:-db}"
COMPOSE_CMD_RAW="${COMPOSE_CMD:-docker compose}"

BACKUP_FILE="$BACKUP_DIR/db_backup_${DATE}.dump"
SHA256_FILE="$BACKUP_FILE.sha256"
CONTAINER_DUMP_PATH="/tmp/fikrly_restore_verify_${DATE}.dump"
VERIFY_DB="restore_verify_${DATE}"

mkdir -p "$BACKUP_DIR" "$PROJECT_DIR/logs"

cd "$PROJECT_DIR"

detect_compose_cmd() {
    if ${COMPOSE_CMD_RAW} ps >/dev/null 2>&1; then
        COMPOSE_CMD=(docker compose)
        return
    fi

    if sudo -n docker compose ps >/dev/null 2>&1; then
        COMPOSE_CMD=(sudo -n docker compose)
        return
    fi

    echo "[$(date -Is)] ❌ Cannot access Docker daemon."
    echo "    Fix by either:"
    echo "    1) Adding user to docker group, or"
    echo "    2) Allowing passwordless sudo for docker compose"
    exit 1
}

detect_compose_cmd

echo "[$(date -Is)] 📦 Creating PostgreSQL backup..."
"${COMPOSE_CMD[@]}" exec -T "$DB_SERVICE" sh -lc 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc --no-owner --no-privileges' > "$BACKUP_FILE"

if [[ ! -s "$BACKUP_FILE" ]]; then
    echo "[$(date -Is)] ❌ Backup file is empty: $BACKUP_FILE"
    exit 1
fi

sha256sum "$BACKUP_FILE" > "$SHA256_FILE"

cleanup_verify() {
    set +e
    "${COMPOSE_CMD[@]}" exec -T -e VERIFY_DB="$VERIFY_DB" "$DB_SERVICE" sh -lc 'dropdb -U "$POSTGRES_USER" --if-exists "$VERIFY_DB" >/dev/null 2>&1 || true'
    "${COMPOSE_CMD[@]}" exec -T -e CONTAINER_DUMP_PATH="$CONTAINER_DUMP_PATH" "$DB_SERVICE" sh -lc 'rm -f "$CONTAINER_DUMP_PATH" >/dev/null 2>&1 || true'
    set -e
}

trap cleanup_verify EXIT

echo "[$(date -Is)] 🔍 Verifying backup with restore test..."
"${COMPOSE_CMD[@]}" cp "$BACKUP_FILE" "$DB_SERVICE:$CONTAINER_DUMP_PATH"
"${COMPOSE_CMD[@]}" exec -T -e VERIFY_DB="$VERIFY_DB" "$DB_SERVICE" sh -lc 'createdb -U "$POSTGRES_USER" "$VERIFY_DB"'
"${COMPOSE_CMD[@]}" exec -T -e VERIFY_DB="$VERIFY_DB" -e CONTAINER_DUMP_PATH="$CONTAINER_DUMP_PATH" "$DB_SERVICE" sh -lc 'pg_restore -U "$POSTGRES_USER" -d "$VERIFY_DB" --no-owner --no-privileges "$CONTAINER_DUMP_PATH" >/dev/null'
"${COMPOSE_CMD[@]}" exec -T -e VERIFY_DB="$VERIFY_DB" "$DB_SERVICE" sh -lc 'psql -U "$POSTGRES_USER" -d "$VERIFY_DB" -tAc "SELECT current_database();" | grep -q "^$VERIFY_DB$"'

cleanup_verify
trap - EXIT

echo "[$(date -Is)] 🗑️ Removing backups older than $KEEP_DAYS days..."
find "$BACKUP_DIR" -type f -name 'db_backup_*.dump' -mtime +"$KEEP_DAYS" -delete
find "$BACKUP_DIR" -type f -name 'db_backup_*.dump.sha256' -mtime +"$KEEP_DAYS" -delete

echo "[$(date -Is)] ✅ Backup + restore verification complete"
echo "    Backup: $BACKUP_FILE"
echo "    Checksum: $SHA256_FILE"
