from django.apps import AppConfig


class RequestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.requests'
    verbose_name = 'Asset Requests'

    def ready(self):
        print("Loading requests module")
        try:
            from . import signals  # Import signals
            print("Request signals loaded successfully")
        except Exception as e:
            print(f"Error loading request signals: {e}")
