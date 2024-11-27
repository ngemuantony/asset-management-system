from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from core.models import AuditableModel

class ReportTemplate(AuditableModel):
    """
    Template for generating various types of reports
    """
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=50)
    template_file = models.FileField(upload_to='report_templates/')
    template_config = models.JSONField(default=dict)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['template_type']),
        ]

    def __str__(self):
        return self.name

class Report(AuditableModel):
    """
    Generated report instance
    """
    name = models.CharField(max_length=255)
    template = models.ForeignKey(ReportTemplate, on_delete=models.PROTECT)
    format = models.CharField(max_length=20)
    parameters = models.JSONField(default=dict)
    generated_file = models.FileField(upload_to='reports/')
    generation_time = models.DateTimeField(default=timezone.now)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    scheduled = models.BooleanField(default=False)
    
    # Generic relation to allow reports on any model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-generation_time']
        indexes = [
            models.Index(fields=['generation_time']),
            models.Index(fields=['format']),
        ]

    def __str__(self):
        return f"{self.name} - {self.generation_time}"