from django.core.management.base import BaseCommand
from django.db import connections
from django.core.cache import cache
from django.conf import settings
import sys

class Command(BaseCommand):
    help = 'Run system health checks'

    def handle(self, *args, **kwargs):
        self.stdout.write('Running system health checks...')
        
        # Check database connections
        self.check_database()
        
        # Check cache
        self.check_cache()
        
        # Check installed apps
        self.check_apps()
        
        self.stdout.write(self.style.SUCCESS('All checks passed!'))

    def check_database(self):
        self.stdout.write('Checking database connection... ', ending='')
        try:
            connections['default'].cursor()
            self.stdout.write(self.style.SUCCESS('OK'))
        except Exception as e:
            self.stdout.write(self.style.ERROR('FAILED'))
            self.stdout.write(self.style.ERROR(str(e)))
            sys.exit(1)

    def check_cache(self):
        self.stdout.write('Checking cache connection... ', ending='')
        try:
            cache.set('healthcheck', 'ok', 1)
            if cache.get('healthcheck') == 'ok':
                self.stdout.write(self.style.SUCCESS('OK'))
            else:
                raise Exception('Cache test failed')
        except Exception as e:
            self.stdout.write(self.style.ERROR('FAILED'))
            self.stdout.write(self.style.ERROR(str(e)))
            sys.exit(1)

    def check_apps(self):
        self.stdout.write('Checking required apps... ', ending='')
        required_apps = [
            'rest_framework',
            'rest_framework_simplejwt',
            'corsheaders',
            'core',
            'apps.authentication',
            'apps.users',
            'apps.departments'
        ]
        missing_apps = [app for app in required_apps if app not in settings.INSTALLED_APPS]
        if missing_apps:
            self.stdout.write(self.style.ERROR('FAILED'))
            self.stdout.write(self.style.ERROR(f'Missing apps: {", ".join(missing_apps)}'))
            sys.exit(1)
        self.stdout.write(self.style.SUCCESS('OK')) 