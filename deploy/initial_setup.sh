#!/bin/bash
# Initial VPS setup script for Fikrly
# Run this ONCE on a fresh Ubuntu 22.04/24.04 VPS
# Usage: sudo bash deploy/initial_setup.sh

set -e

echo "🔧 Fikrly VPS Initial Setup"
echo "=============================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (sudo)"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install required packages
echo "📦 Installing dependencies..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    nginx \
    redis-server \
    git \
    curl \
    ufw \
    fail2ban \
    certbot \
    python3-certbot-nginx \
    supervisor

# Configure PostgreSQL
echo "🗄️  Configuring PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE fikrly_production;" || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER fikrly_user WITH PASSWORD 'CHANGE_THIS_PASSWORD';" || echo "User already exists"
sudo -u postgres psql -c "ALTER ROLE fikrly_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE fikrly_user SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE fikrly_user SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fikrly_production TO fikrly_user;"
sudo -u postgres psql -c "ALTER DATABASE fikrly_production OWNER TO fikrly_user;"

# Configure Redis
echo "🔴 Configuring Redis..."
systemctl enable redis-server
systemctl start redis-server

# Configure Firewall
echo "🔥 Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
echo "y" | ufw enable

# Configure Fail2ban
echo "🛡️  Configuring Fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban

# Create project directory
echo "📁 Creating project directory..."
mkdir -p /var/www/fikrly
mkdir -p /var/log/fikrly
chown -R www-data:www-data /var/www/fikrly
chown -R www-data:www-data /var/log/fikrly

# Create deployer user (optional but recommended)
echo "👤 Creating deployer user..."
useradd -m -s /bin/bash deployer || echo "User already exists"
usermod -aG www-data deployer
usermod -aG sudo deployer

echo ""
echo "✅ Initial setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Clone your repository to /var/www/fikrly"
echo "2. Create virtual environment: python3 -m venv /var/www/fikrly/venv"
echo "3. Copy .env.production.example to .env and fill in values"
echo "4. Install dependencies: source venv/bin/activate && pip install -r requirements.txt"
echo "5. Run migrations: python manage.py migrate"
echo "6. Collect static files: python manage.py collectstatic"
echo "7. Create superuser: python manage.py createsuperuser"
echo "8. Copy deploy/gunicorn.service to /etc/systemd/system/"
echo "9. Copy deploy/nginx.conf to /etc/nginx/sites-available/fikrly"
echo "10. Get SSL certificate: sudo certbot --nginx -d fikrly.uz -d www.fikrly.uz"
echo ""
echo "⚠️  IMPORTANT: Change PostgreSQL password in the database and .env file!"
