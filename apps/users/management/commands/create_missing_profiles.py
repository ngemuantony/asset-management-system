from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import UserProfile
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Create missing user profiles for existing users'

    def handle(self, *args, **kwargs):
        users_without_profiles = User.objects.filter(profile__isnull=True)
        created_count = 0

        for user in users_without_profiles:
            UserProfile.objects.create(
                user=user,
                role='USER',
                employee_id=f'EMP{str(uuid.uuid4().hex[:6]).upper()}'
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} missing user profiles'
            )
        ) 