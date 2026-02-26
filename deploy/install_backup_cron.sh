#!/usr/bin/env bash
# Install/refresh nightly DB backup cron entry for current user.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SCHEDULE="${BACKUP_CRON_SCHEDULE:-0 2 * * *}"
LOG_FILE="${BACKUP_LOG_FILE:-$PROJECT_DIR/logs/backup.log}"
BACKUP_SCRIPT="$SCRIPT_DIR/backup.sh"
TARGET="${BACKUP_CRON_TARGET:-auto}" # auto|user|root

mkdir -p "$(dirname "$LOG_FILE")"
chmod +x "$BACKUP_SCRIPT"

CRON_ENTRY="$SCHEDULE cd $PROJECT_DIR && $BACKUP_SCRIPT >> $LOG_FILE 2>&1"

if [[ "$TARGET" == "auto" ]]; then
	if docker compose ps >/dev/null 2>&1; then
		TARGET="user"
	else
		TARGET="root"
	fi
fi

if [[ "$TARGET" == "root" ]]; then
	CURRENT_CRONTAB="$(sudo crontab -l 2>/dev/null || true)"
else
	CURRENT_CRONTAB="$(crontab -l 2>/dev/null || true)"
fi

NEW_CRONTAB="$(printf '%s\n' "$CURRENT_CRONTAB" | sed '/deploy\/backup\.sh/d')"
NEW_CRONTAB="$(printf '%s\n%s\n' "$NEW_CRONTAB" "$CRON_ENTRY" | awk 'NF' )"

if [[ "$TARGET" == "root" ]]; then
	printf '%s\n' "$NEW_CRONTAB" | sudo crontab -
else
	printf '%s\n' "$NEW_CRONTAB" | crontab -
fi

echo "✅ Nightly backup cron installed"
echo "   Target:   $TARGET crontab"
echo "   Schedule: $SCHEDULE"
echo "   Command:  $BACKUP_SCRIPT"
echo "   Log file: $LOG_FILE"
