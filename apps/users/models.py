from django.db import models
from django.contrib.auth import get_user_model
from core.models import AuditableModel
from core.constants import ROLE_CHOICES, ROLE_USER, STATUS_CHOICES, STATUS_ACTIVE
from django.core.exceptions import ValidationError

User = get_user_model()

class UserProfile(AuditableModel):
    """User profile model with role-based access control"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_USER
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='department_users'
    )
    employee_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE
    )

    class Meta:
        ordering = ['user__username']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['employee_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def clean(self):
        """Validate profile data"""
        if self.role == 'MANAGER' and not self.department:
            raise ValidationError("Managers must be assigned to a department")

    @property
    def is_admin(self):
        return self.role == 'ADMIN'

    @property
    def is_manager(self):
        return self.role == 'MANAGER'

    @property
    def is_staff(self):
        return self.role == 'STAFF'

    @property
    def can_approve_requests(self):
        return self.role in ['ADMIN', 'MANAGER']

    def can_manage_department(self, department):
        """Check if user can manage a department"""
        if self.is_admin:
            return True
        return self.is_manager and self.department == department

    def can_manage_user(self, user):
        """Check if user can manage another user"""
        if self.is_admin:
            return True
        if self.is_manager:
            return user.profile.department == self.department
        return False

    def save(self, *args, **kwargs):
        # Format phone number before saving
        if self.phone_number:
            # Remove any non-digit characters and ensure it's a string
            self.phone_number = str(''.join(filter(str.isdigit, str(self.phone_number))))
        super().save(*args, **kwargs)

class UserActivityLog(AuditableModel):
    """Log user activities"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    action = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.CharField(max_length=255, null=True)
    action_details = models.JSONField(default=dict)
    status = models.CharField(max_length=20, default='SUCCESS')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"
