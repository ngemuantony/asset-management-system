from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .constants import STATUS_ACTIVE, STATUS_CHOICES
from django.utils import timezone

class BaseModel(models.Model):
    """
    Base model class that provides common fields and functionality.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE
    )
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
            models.Index(fields=['status'])
        ]

    def validate_unique(self, *args, **kwargs):
        super().validate_unique(*args, **kwargs)

    def clean(self):
        super().clean()

    def soft_delete(self, user=None):
        self.deleted_at = timezone.now()
        if hasattr(self, 'last_modified_by') and user:
            self.last_modified_by = user
        self.save()

class TrackableModel(BaseModel):
    """
    Model class for objects that need tracking.
    """
    last_modified_by = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_modifications'
    )
    notes = models.TextField(blank=True)
    version = models.IntegerField(default=1)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self.version += 1
        super().save(*args, **kwargs)

class AuditableModel(TrackableModel):
    """
    Model class for objects that need audit trail.
    """
    is_active = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    deactivated_by = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_deactivations'
    )

    class Meta:
        abstract = True
