from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile
from core.constants import ROLE_ADMIN
import uuid

User = get_user_model()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create/update UserProfile when User is created/updated
    """
    if created:
        # Create profile for new user
        employee_id = f'EMP{str(uuid.uuid4().hex[:6]).upper()}'
        
        # If user is a superuser, assign ADMIN role
        role = ROLE_ADMIN if instance.is_superuser else 'USER'
        
        UserProfile.objects.create(
            user=instance,
            role=role,
            employee_id=employee_id
        )
    else:
        # Update existing profile
        if hasattr(instance, 'profile'):
            # If user becomes superuser, update role to ADMIN
            if instance.is_superuser and instance.profile.role != ROLE_ADMIN:
                instance.profile.role = ROLE_ADMIN
                instance.profile.save() 