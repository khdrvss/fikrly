#!/bin/bash
# Docker entrypoint script for Fikrly Django application

set -e

echo "🐳 Starting Fikrly Django application..."

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
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create cache table if needed
echo "🗄️  Setting up cache..."
python manage.py createcachetable || true

# Create superuser if it doesn't exist (only in development)
if [ "$DEBUG" = "True" ]; then
    echo "👤 Creating superuser (development only)..."
    python manage.py shell << END
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
