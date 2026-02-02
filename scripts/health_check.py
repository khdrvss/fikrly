import os
import sys
import logging
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def check_db_connection():
    try:
        db_conn = connections['default']
        db_conn.cursor()
        logger.info("✅ Database connection successful.")
        return True
    except OperationalError as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected database error: {e}")
        return False

def check_redis():
    if 'django_redis' not in settings.INSTALLED_APPS and 'django_redis.cache.RedisCache' not in str(settings.CACHES):
         # It might be in CACHES only
         pass

    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 30)
        val = cache.get('health_check')
        if val == 'ok':
            logger.info("✅ Cache (Redis/Locmem) connection successful.")
            return True
        else:
            logger.error("❌ Cache check failed: value mismatch.")
            return False
    except Exception as e:
        logger.error(f"❌ Cache connection failed: {e}")
        return False

def run_health_checks():
    # Setup Django
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
        import django
        django.setup()
    except Exception as e:
        logger.error(f"❌ Failed to setup Django environment: {e}")
        return

    logger.info("Starting System Health Check...")
    
    # 1. Check Debug Status
    if settings.DEBUG:
        logger.warning("⚠️  DEBUG is True. Ensure this is a development environment.")
    else:
        logger.info("✅ DEBUG is False (Production safe).")

    # 2. Check Database
    db_ok = check_db_connection()

    # 3. Check Cache
    check_redis()

    # 4. Check Migrations (simple check if we can query models)
    if db_ok:
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            count = User.objects.count()
            logger.info(f"✅ Models accessible. User count: {count}")
        except Exception as e:
            logger.error(f"❌ Model access failed (Pending migrations?): {e}")

if __name__ == "__main__":
    run_health_checks()
