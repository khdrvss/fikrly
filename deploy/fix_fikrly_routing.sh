#!/bin/bash
# Emergency fix: ensure fikrly.uz is served by the fikrly project nginx site.

set -euo pipefail

PROJECT_DIR="/home/maymun/fikrly"
SITE_NAME="fikrly"
SOURCE_CONF="$PROJECT_DIR/deploy/nginx.conf"
AVAILABLE_CONF="/etc/nginx/sites-available/$SITE_NAME"
ENABLED_CONF="/etc/nginx/sites-enabled/$SITE_NAME"

if [[ "$EUID" -ne 0 ]]; then
  echo "Run with sudo: sudo bash deploy/fix_fikrly_routing.sh"
  exit 1
fi

if [[ ! -f "$SOURCE_CONF" ]]; then
  echo "Missing source config: $SOURCE_CONF"
  exit 1
fi

cp "$SOURCE_CONF" "$AVAILABLE_CONF"
ln -sfn "$AVAILABLE_CONF" "$ENABLED_CONF"

nginx -t
systemctl reload nginx

echo "Nginx routing fix applied."
echo "Enabled sites:"
ls -la /etc/nginx/sites-enabled
echo
echo "Quick checks:"
echo "curl -I -H 'Host: fikrly.uz' http://127.0.0.1"
echo "curl -I https://fikrly.uz/health/"
