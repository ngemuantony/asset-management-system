from django.db import models
from core.models import AuditableModel
from core.utils import generate_unique_id
from core.constants import (
    STATUS_CHOICES, STATUS_ACTIVE,
    REQUEST_STATUS_CHOICES, REQUEST_STATUS_PENDING,
    REQUEST_PRIORITY_CHOICES, REQUEST_PRIORITY_MEDIUM
)
from apps.assets.models import Asset
from django.conf import settings

class RequestType(AuditableModel):
    """
    Types of requests (e.g., New Asset, Transfer, Maintenance)
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, blank=True)
    description = models.TextField(blank=True)
    requires_approval = models.BooleanField(default=True)
    approval_levels = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_id(prefix='REQ')
        super().save(*args, **kwargs)

class AssetRequest(AuditableModel):
    """
    Asset request model for handling various types of asset-related requests
    """
    request_id = models.CharField(max_length=20, unique=True, blank=True)
    request_type = models.ForeignKey(RequestType, on_delete=models.PROTECT)
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='requested_assets'
    )
    asset = models.ForeignKey(
        Asset, 
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='asset_requests'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(
        max_length=10,
        choices=REQUEST_PRIORITY_CHOICES,
        default=REQUEST_PRIORITY_MEDIUM
    )
    status = models.CharField(
        max_length=20,
        choices=REQUEST_STATUS_CHOICES,
        default=REQUEST_STATUS_PENDING
    )
    desired_date = models.DateField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    attachments = models.FileField(
        upload_to='request_attachments/',
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_asset_requests'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_asset_requests'
    )
    deactivated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='deactivated_asset_requests'
    )
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='modified_asset_requests'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['request_id']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['desired_date']),
        ]

    def __str__(self):
        return f"{self.request_id} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.request_id:
            self.request_id = generate_unique_id(prefix='REQ')
        super().save(*args, **kwargs)

class RequestApproval(AuditableModel):
    """
    Tracks approval workflow for asset requests
    """
    request = models.ForeignKey(
        AssetRequest,
        on_delete=models.CASCADE,
        related_name='approvals'
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='request_approvals'
    )
    approval_level = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=REQUEST_STATUS_CHOICES,
        default=REQUEST_STATUS_PENDING
    )
    comments = models.TextField(blank=True)
    approval_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['approval_level', '-created_at']
        unique_together = ['request', 'approver', 'approval_level']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['approval_level']),
        ]

    def __str__(self):
        return f"Approval for {self.request.request_id} - Level {self.approval_level}"
