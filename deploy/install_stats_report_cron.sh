#!/usr/bin/env bash
# Install/refresh every-3-days Telegram stats report cron.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SCHEDULE="${STATS_REPORT_CRON_SCHEDULE:-0 9 */3 * *}"
LOG_FILE="${STATS_REPORT_LOG_FILE:-$PROJECT_DIR/logs/stats_report.log}"
REPORT_SCRIPT="$SCRIPT_DIR/send_stats_report.sh"
TARGET="${STATS_REPORT_CRON_TARGET:-auto}" # auto|user|root

mkdir -p "$(dirname "$LOG_FILE")"
chmod +x "$REPORT_SCRIPT"

CRON_ENTRY="$SCHEDULE cd $PROJECT_DIR && $REPORT_SCRIPT >> $LOG_FILE 2>&1"

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

NEW_CRONTAB="$(printf '%s\n' "$CURRENT_CRONTAB" | sed '/deploy\/send_stats_report\.sh/d')"
NEW_CRONTAB="$(printf '%s\n%s\n' "$NEW_CRONTAB" "$CRON_ENTRY" | awk 'NF')"

if [[ "$TARGET" == "root" ]]; then
    printf '%s\n' "$NEW_CRONTAB" | sudo crontab -
else
    printf '%s\n' "$NEW_CRONTAB" | crontab -
fi

echo "✅ Stats report cron installed"
echo "   Target:   $TARGET crontab"
echo "   Schedule: $SCHEDULE"
echo "   Command:  $REPORT_SCRIPT"
echo "   Log file: $LOG_FILE"
