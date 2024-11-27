from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Users'

    def ready(self):
        print("Loading users module")
        try:
            from . import signals  # Import signals
            print("User signals loaded successfully")
        except Exception as e:
            print(f"Error loading user signals: {e}")
