#!/usr/bin/env bash
set -euo pipefail

# Bootstrap Fikrly Docker deployment:
# - creates .env from .env.docker if missing (and fills core secrets)
# - starts docker compose stack

cd "$(dirname "$0")/.."

if [ ! -f ".env" ]; then
  if [ ! -f ".env.docker" ]; then
    echo "❌ .env.docker not found" >&2
    exit 1
  fi

  cp .env.docker .env

  # Replace placeholders for core secrets so the app can start.
  # Telegram/Eskiz/Google remain as-is until you set real credentials.
  secret_key="$(openssl rand -hex 64)"
  db_password="$(openssl rand -hex 32)"

  # Linux sed -i
  sed -i "s/^SECRET_KEY=.*/SECRET_KEY=${secret_key}/" .env
  sed -i "s/^DB_PASSWORD=.*/DB_PASSWORD=${db_password}/" .env

  # Ensure HTTPS flags exist (bootstrap runs over HTTP until you install certs)
  if ! grep -q '^USE_HTTPS=' .env; then
    printf '\nUSE_HTTPS=False\nSECURE_SSL_REDIRECT=False\n' >> .env
  fi

  echo "✅ Created .env with generated SECRET_KEY and DB_PASSWORD."
  echo "ℹ️  Edit .env to set TELEGRAM_* / ESKIZ_* / GOOGLE_* if you need them."
fi

docker compose up -d --build
docker compose ps
