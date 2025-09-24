from django.apps import AppConfig


class FrontendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'frontend'

    def ready(self):
        # Wire signals
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Avoid crashing on import-time issues in checks/migrations
            pass
