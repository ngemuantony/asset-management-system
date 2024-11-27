from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import UserProfile
from core.constants import ROLE_ADMIN
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Ensure all superusers have ADMIN role'

    def handle(self, *args, **kwargs):
        superusers = User.objects.filter(is_superuser=True)
        updated = 0
        created = 0

        for user in superusers:
            if hasattr(user, 'profile'):
                if user.profile.role != ROLE_ADMIN:
                    user.profile.role = ROLE_ADMIN
                    user.profile.save()
                    updated += 1
            else:
                UserProfile.objects.create(
                    user=user,
                    role=ROLE_ADMIN,
                    employee_id=f'EMP{str(uuid.uuid4().hex[:6]).upper()}'
                )
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(superusers)} superusers:\n'
                f'- Created {created} new profiles\n'
                f'- Updated {updated} existing profiles'
            )
        ) 