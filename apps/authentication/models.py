from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import BaseModel
from core.utils import generate_unique_id
from django.utils import timezone
from core.constants import STATUS_ACTIVE, STATUS_CHOICES

class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    email = models.EmailField(unique=True, max_length=50, db_index=True)
    firstName = models.CharField(max_length=30, db_index=True)
    lastName = models.CharField(max_length=30, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE
    )

    class Meta:
        indexes = [
            models.Index(fields=['username', 'email']),
            models.Index(fields=['firstName', 'lastName']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
            models.Index(fields=['status']),
        ]

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = generate_unique_id(prefix='USR')
        super().save(*args, **kwargs)

    def update_last_login(self):
        self.last_login_at = timezone.now()
        self.save(update_fields=['last_login_at'])

    def increment_failed_attempts(self):
        self.failed_login_attempts += 1
        self.save(update_fields=['failed_login_attempts'])

    def reset_failed_attempts(self):
        self.failed_login_attempts = 0
        self.save(update_fields=['failed_login_attempts'])

    def __str__(self):
        return f"{self.firstName} {self.lastName} ({self.username})"
