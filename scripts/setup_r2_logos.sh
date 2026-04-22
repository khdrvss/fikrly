#!/bin/bash
# Setup script for R2 logo migration
# Run this to install dependencies and prepare environment

echo "=== R2 Logo Migration Setup ==="
echo ""

# Check if running in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source ../.venv/bin/activate
fi

# Install required packages
echo "Installing boto3, Pillow, requests..."
pip install boto3 Pillow requests -q

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Add these to your .env file:"
echo ""
cat r2_credentials.txt | grep -v "^#" | grep -v "^$"
echo ""
echo "Then run the migration:"
echo "  python manage.py migrate_logos_to_r2 --dry-run    # Preview"
echo "  python manage.py migrate_logos_to_r2              # Execute"
echo ""
