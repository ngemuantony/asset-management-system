from django.db import models
from core.models import AuditableModel
from core.utils import generate_unique_id
from core.constants import ASSET_STATUS_CHOICES, ASSET_STATUS_AVAILABLE
from django.core.validators import MinValueValidator
from decimal import Decimal
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

ASSET_REQUEST_STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('APPROVED', 'Approved'),
    ('DECLINED', 'Declined'),
]

class Asset(AuditableModel):
    """
    Asset model for managing organization assets
    """
    asset_id = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.PROTECT,
        related_name='assets'
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        related_name='asset_set'
    )
    assigned_to = models.ForeignKey(
        'users.UserProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_assets'
    )
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    asset_status = models.CharField(
        max_length=20,
        choices=ASSET_STATUS_CHOICES,
        default=ASSET_STATUS_AVAILABLE
    )
    manufacturer = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=50, blank=True)
    serial_number = models.CharField(max_length=50, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    maintenance_schedule = models.DateField(null=True, blank=True)
    last_maintenance = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    tags = models.ManyToManyField('tags.Tag', blank=True)
    qr_code = models.ImageField(upload_to='asset_qr_codes/', blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=ASSET_STATUS_CHOICES,
        default=ASSET_STATUS_AVAILABLE
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['asset_id']),
            models.Index(fields=['asset_status']),
            models.Index(fields=['category']),
            models.Index(fields=['department']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f"{self.asset_id} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.asset_id:
            self.asset_id = generate_unique_id(prefix='AST')
        
        # Generate QR code if it doesn't exist
        if not self.qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(f'Asset ID: {self.asset_id}\nName: {self.name}')
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            
            filename = f'asset_qr_{self.asset_id}.png'
            filebuffer = InMemoryUploadedFile(
                buffer,
                None,
                filename,
                'image/png',
                buffer.tell(),
                None
            )
            self.qr_code.save(filename, filebuffer, save=False)
        
        super().save(*args, **kwargs)

    @property
    def current_value(self):
        """Calculate depreciated value"""
        # Implement depreciation calculation logic
        return self.purchase_price

class AssetMaintenance(AuditableModel):
    """Model for tracking asset maintenance records"""
    MAINTENANCE_TYPES = [
        ('PREVENTIVE', 'Preventive Maintenance'),
        ('CORRECTIVE', 'Corrective Maintenance'),
        ('INSPECTION', 'Inspection'),
        ('CALIBRATION', 'Calibration'),
        ('OTHER', 'Other'),
    ]

    asset = models.ForeignKey(
        'Asset',
        on_delete=models.CASCADE,
        related_name='maintenance_records'
    )
    maintenance_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )
    maintenance_type = models.CharField(
        max_length=20,
        choices=MAINTENANCE_TYPES,
        default='PREVENTIVE'
    )
    maintenance_date = models.DateTimeField()
    description = models.TextField()
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    performed_by = models.ForeignKey(
        'users.UserProfile',
        on_delete=models.SET_NULL,
        null=True,
        related_name='maintenance_performed'
    )
    next_maintenance_date = models.DateField(null=True, blank=True)
    attachments = models.FileField(
        upload_to='maintenance_docs/',
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.maintenance_id:
            self.maintenance_id = generate_unique_id(prefix='MNT')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.maintenance_id} - {self.asset.name}"

    class Meta:
        ordering = ['-maintenance_date']
        indexes = [
            models.Index(fields=['maintenance_date']),
            models.Index(fields=['maintenance_type']),
            models.Index(fields=['maintenance_id']),
        ]

class AssetAssignment(AuditableModel):
    """
    Track asset assignments history
    """
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='assignment_history'
    )
    assigned_to = models.ForeignKey(
        'users.UserProfile',
        on_delete=models.SET_NULL,
        null=True,
        related_name='asset_assignments'
    )
    assigned_by = models.ForeignKey(
        'users.UserProfile',
        on_delete=models.SET_NULL,
        null=True,
        related_name='asset_assignments_made'
    )
    assigned_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    expected_return_date = models.DateField(null=True, blank=True)
    assignment_notes = models.TextField(blank=True)
    return_notes = models.TextField(blank=True)
    return_condition = models.TextField(blank=True)

    class Meta:
        ordering = ['-assigned_date']

class AssetRequest(AuditableModel):
    """
    Model for asset request management
    """
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='requests'
    )
    requested_by = models.ForeignKey(
        'users.UserProfile',
        on_delete=models.CASCADE,
        related_name='asset_requests'
    )
    approved_by = models.ForeignKey(
        'users.UserProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_approvals'
    )
    request_status = models.CharField(
        max_length=20,
        choices=ASSET_REQUEST_STATUS_CHOICES,
        default='PENDING'
    )
    request_date = models.DateTimeField(auto_now_add=True)
    response_date = models.DateTimeField(null=True, blank=True)
    expected_return_date = models.DateField()
    purpose = models.TextField()
    response_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-request_date']
