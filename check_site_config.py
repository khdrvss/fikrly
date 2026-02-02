import os
import sys
import logging
import django
from django.db.utils import OperationalError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_config():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    try:
        django.setup()
    except Exception as e:
        logger.error(f"Failed to setup Django: {e}")
        sys.exit(1)

    try:
        from django.contrib.sites.models import Site
        from allauth.socialaccount.models import SocialApp
        
        # Check Site
        try:
            site = Site.objects.get(pk=1)
            logger.info(f"Site Configuration: ID=1, Domain={site.domain}, Name={site.name}")
        except Site.DoesNotExist:
            logger.warning("Site ID 1 does not exist.")
        except OperationalError:
            logger.error("Database connection failed. Ensure the database is running and accessible.")
            return

        # Check Social Apps
        apps = SocialApp.objects.filter(provider='google')
        if not apps.exists():
            logger.info("No Google SocialApp found.")
        
        for app in apps:
            sites = [s.domain for s in app.sites.all()]
            logger.info(f"SocialApp found: Name='{app.name}', Client ID='{app.client_id[:10]}...', Sites={sites}")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    check_config()
