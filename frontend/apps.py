from django.apps import AppConfig


class FrontendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'frontend'

    def ready(self):
        # Placeholder for signals if needed later
        return super().ready()
