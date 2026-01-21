#!/bin/bash
# Deployment script for Fikrly production
# Usage: ./deploy/deploy.sh

set -e  # Exit on error

echo "🚀 Starting Fikrly deployment..."

# Configuration
PROJECT_DIR="/var/www/fikrly"
VENV_DIR="$PROJECT_DIR/venv"
USER="www-data"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}❌ Do not run as root. Run as deployer user.${NC}"
    exit 1
fi

# Navigate to project directory
cd $PROJECT_DIR

echo -e "${YELLOW}📦 Pulling latest code...${NC}"
git pull origin main

echo -e "${YELLOW}🐍 Activating virtual environment...${NC}"
source $VENV_DIR/bin/activate

echo -e "${YELLOW}📚 Installing dependencies...${NC}"
pip install -r requirements.txt --quiet

echo -e "${YELLOW}🗄️  Running migrations...${NC}"
python manage.py migrate --noinput

echo -e "${YELLOW}📁 Collecting static files...${NC}"
python manage.py collectstatic --noinput --clear

echo -e "${YELLOW}🧹 Cleaning old sessions...${NC}"
python manage.py clearsessions

echo -e "${YELLOW}🗑️  Cleaning expired exports...${NC}"
python manage.py clean_expired_exports

echo -e "${YELLOW}🔍 Running system checks...${NC}"
python manage.py check --deploy

echo -e "${YELLOW}🔄 Restarting Gunicorn...${NC}"
sudo systemctl restart gunicorn

echo -e "${YELLOW}🔄 Reloading Nginx...${NC}"
sudo systemctl reload nginx

echo -e "${YELLOW}✅ Checking service status...${NC}"
sudo systemctl is-active --quiet gunicorn && echo -e "${GREEN}✓ Gunicorn is running${NC}" || echo -e "${RED}✗ Gunicorn failed${NC}"
sudo systemctl is-active --quiet nginx && echo -e "${GREEN}✓ Nginx is running${NC}" || echo -e "${RED}✗ Nginx failed${NC}"

echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""
echo -e "📊 Service status:"
sudo systemctl status gunicorn --no-pager -l | head -n 5
echo ""
echo -e "🌐 Visit: https://fikrly.uz/health/"
