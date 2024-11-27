from django.db import models
from core.models import AuditableModel
from core.utils import generate_unique_id
from core.constants import STATUS_CHOICES, STATUS_ACTIVE

class Tag(AuditableModel):
    """
    Tag model for flexible asset categorization
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#000000")  # Hex color code
    code = models.CharField(max_length=10, unique=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE
    )

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_id(prefix='TAG')
        super().save(*args, **kwargs)

    @property
    def asset_count(self):
        """Get number of assets with this tag"""
        return self.asset_tags.count()
