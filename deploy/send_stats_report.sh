#!/usr/bin/env bash
# Send Telegram stats report using Django management command (Docker Compose)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DB_SERVICE="${DB_SERVICE:-web}"
COMPOSE_CMD_RAW="${COMPOSE_CMD:-docker compose}"
DRY_RUN="${1:-}"

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

    echo "[$(date -Is)] ❌ Cannot access Docker daemon for stats report"
    exit 1
}

detect_compose_cmd

CMD=("${COMPOSE_CMD[@]}" exec -T "$DB_SERVICE" python manage.py send_stats_report)
if [[ "$DRY_RUN" == "--dry-run" ]]; then
    CMD+=(--dry-run)
fi

"${CMD[@]}"
