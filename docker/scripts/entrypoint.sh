#!/bin/sh
# Docker entrypoint script for Fikrly Django application

set -e

echo "🐳 Starting Fikrly Django application..."

# Remove stale .pyc bytecode (prevents AttributeError when files are updated via docker cp)
find /app -name "*.pyc" -delete 2>/dev/null || true
find /app -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Basic env validation (fail fast for core requirements)
if [ -z "${SECRET_KEY:-}" ]; then
    echo "❌ SECRET_KEY is not set. Put it in .env" >&2
    exit 1
fi
if [ -z "${DB_HOST:-}" ] || [ -z "${DB_PORT:-}" ] || [ -z "${DB_NAME:-}" ] || [ -z "${DB_USER:-}" ]; then
    echo "❌ DB_HOST/DB_PORT/DB_NAME/DB_USER must be set in .env" >&2
    exit 1
fi
if [ -z "${DB_PASSWORD:-}" ]; then
    echo "❌ DB_PASSWORD is not set. Put it in .env" >&2
    exit 1
fi

# Optional integrations (warn only)
if [ -z "${TELEGRAM_BOT_TOKEN:-}" ]; then
    echo "ℹ️  TELEGRAM_BOT_TOKEN not set (Telegram notifications disabled)."
fi
if [ -z "${ESKIZ_EMAIL:-}" ] || [ -z "${ESKIZ_PASSWORD:-}" ]; then
    echo "ℹ️  ESKIZ credentials not set (SMS OTP may be disabled/fallback in DEBUG)."
fi
if [ -z "${GOOGLE_CLIENT_ID:-}" ] || [ -z "${GOOGLE_CLIENT_SECRET:-}" ]; then
    echo "ℹ️  Google OAuth not set (Google login disabled)."
fi

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
done
echo "✅ PostgreSQL is ready!"

# Wait for Redis
echo "⏳ Waiting for Redis..."
while ! nc -z redis 6379; do
    sleep 0.1
done
echo "✅ Redis is ready!"

# Run migrations
echo "🔄 Running database migrations..."
python3 manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python3 manage.py collectstatic --noinput --clear

# Create cache table if needed
echo "🗄️  Setting up cache..."
python3 manage.py createcachetable || true

# Create superuser if it doesn't exist (only in development)
if [ "$DEBUG" = "True" ]; then
    echo "👤 Creating superuser (development only)..."
    python3 manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@fikrly.uz', 'admin123')
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')
END
fi

echo "✅ Initialization complete!"
echo "🚀 Starting Gunicorn..."

# Execute the main command
exec "$@"
