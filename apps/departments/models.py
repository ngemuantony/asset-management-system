from django.db import models
from core.models import AuditableModel
from core.utils import generate_unique_id
from django.core.exceptions import ValidationError

class Department(AuditableModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=10, unique=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='sub_departments'
    )

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_id(prefix='DEPT')
        super().save(*args, **kwargs)

    @property
    def member_count(self):
        return self.department_users.filter(is_active=True).count()

    def clean(self):
        if self.parent and self.parent == self:
            raise ValidationError("Department cannot be its own parent")
        if self.parent and self.is_ancestor(self.parent):
            raise ValidationError("Circular dependency detected")

    def is_ancestor(self, department):
        if not department.parent:
            return False
        if department.parent == self:
            return True
        return self.is_ancestor(department.parent)

    def cache_tree(self):
        """Cache this department's tree structure"""
        from core.cache_utils import cache_department_tree
        cache_department_tree([self])

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['parent']),
            models.Index(fields=['created_at', 'status']),
        ]
