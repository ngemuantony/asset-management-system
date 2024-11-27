from django.db import models
from core.models import AuditableModel
from core.utils import generate_unique_id

class Category(AuditableModel):
    """
    Category model for asset categorization
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=10, unique=True, blank=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subcategories'
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_id(prefix='CAT')
        super().save(*args, **kwargs)

    @property
    def asset_count(self):
        """Get total number of assets in this category"""
        return self.assets.count()
