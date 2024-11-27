# Data Models Documentation

## Core Models

### AuditableModel (Abstract Base)
Base model providing audit fields for all models:
```python
class AuditableModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    version = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    deactivated_by = models.ForeignKey(User, null=True)
    last_modified_by = models.ForeignKey(User, null=True)
```

## Authentication Models

### CustomUser
Extends Django's AbstractUser:
```python
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30)
    login_count = models.IntegerField(default=0)
    last_login_ip = models.GenericIPAddressField(null=True)
```

### UserProfile
User profile with role-based access:
```python
class UserProfile(AuditableModel):
    user = models.OneToOneField(CustomUser)
    role = models.CharField(choices=ROLE_CHOICES)
    department = models.ForeignKey('Department')
    employee_id = models.CharField(unique=True)
    phone_number = models.CharField(null=True)
    status = models.CharField(choices=STATUS_CHOICES)
```

### UserActivityLog
Tracks user activities:
```python
class UserActivityLog(AuditableModel):
    user = models.ForeignKey(CustomUser)
    action = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField()
    action_details = models.JSONField()
    status = models.CharField()
    timestamp = models.DateTimeField()
```

## Asset Management Models

### Asset
Main asset model:
```python
class Asset(AuditableModel):
    name = models.CharField()
    asset_id = models.CharField(unique=True)
    category = models.ForeignKey('Category')
    department = models.ForeignKey('Department')
    status = models.CharField(choices=ASSET_STATUS_CHOICES)
    purchase_date = models.DateField()
    purchase_price = models.DecimalField()
    current_value = models.DecimalField()
    location = models.CharField()
    description = models.TextField()
    specifications = models.JSONField()
    warranty_expiry = models.DateField(null=True)
    maintenance_schedule = models.JSONField()
    qr_code = models.ImageField()
    tags = models.ManyToManyField('Tag')
```

### Category
Asset categorization:
```python
class Category(AuditableModel):
    name = models.CharField(unique=True)
    code = models.CharField(unique=True)
    description = models.TextField()
    parent = models.ForeignKey('self', null=True)
    attributes = models.JSONField()
```

### Tag
Flexible asset tagging:
```python
class Tag(AuditableModel):
    name = models.CharField(unique=True)
    description = models.TextField()
    color = models.CharField()
    code = models.CharField(unique=True)
```

### AssetMaintenance
Maintenance records:
```python
class AssetMaintenance(AuditableModel):
    asset = models.ForeignKey(Asset)
    maintenance_type = models.CharField()
    scheduled_date = models.DateField()
    performed_date = models.DateField()
    cost = models.DecimalField()
    performed_by = models.ForeignKey(CustomUser)
    notes = models.TextField()
    attachments = models.FileField()
```

### AssetAssignment
Asset assignment tracking:
```python
class AssetAssignment(AuditableModel):
    asset = models.ForeignKey(Asset)
    assigned_to = models.ForeignKey(CustomUser)
    assigned_by = models.ForeignKey(CustomUser)
    assigned_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True)
    assignment_type = models.CharField()
    notes = models.TextField()
```

## Request Management Models

### RequestType
Types of asset requests:
```python
class RequestType(AuditableModel):
    name = models.CharField(unique=True)
    code = models.CharField(unique=True)
    description = models.TextField()
    requires_approval = models.BooleanField()
    approval_levels = models.PositiveIntegerField()
```

### AssetRequest
Asset request workflow:
```python
class AssetRequest(AuditableModel):
    request_id = models.CharField(unique=True)
    request_type = models.ForeignKey(RequestType)
    requester = models.ForeignKey(CustomUser)
    asset = models.ForeignKey(Asset, null=True)
    title = models.CharField()
    description = models.TextField()
    priority = models.CharField(choices=REQUEST_PRIORITY_CHOICES)
    status = models.CharField(choices=REQUEST_STATUS_CHOICES)
    desired_date = models.DateField()
    completion_date = models.DateTimeField(null=True)
    attachments = models.FileField()
```

### RequestApproval
Request approval workflow:
```python
class RequestApproval(AuditableModel):
    request = models.ForeignKey(AssetRequest)
    approver = models.ForeignKey(CustomUser)
    approval_level = models.PositiveIntegerField()
    status = models.CharField(choices=REQUEST_STATUS_CHOICES)
    comments = models.TextField()
    approval_date = models.DateTimeField(null=True)
```

## Report Models

### ReportTemplate
Report templates:
```python
class ReportTemplate(AuditableModel):
    name = models.CharField()
    template_type = models.CharField()
    template_file = models.FileField()
    template_config = models.JSONField()
```

### Report
Generated reports:
```python
class Report(AuditableModel):
    name = models.CharField()
    template = models.ForeignKey(ReportTemplate)
    format = models.CharField()
    parameters = models.JSONField()
    generated_file = models.FileField()
    generated_by = models.ForeignKey(CustomUser)
    generation_time = models.DateTimeField()
    scheduled = models.BooleanField()
```

## Department Model

### Department
Organizational structure:
```python
class Department(AuditableModel):
    name = models.CharField(unique=True)
    code = models.CharField(unique=True)
    description = models.TextField()
    parent = models.ForeignKey('self', null=True)
    manager = models.ForeignKey(CustomUser, null=True)
    location = models.CharField()
    contact_email = models.EmailField()
    contact_phone = models.CharField()
```

## Model Relationships

1. **User Relationships**
   - User -> UserProfile (One-to-One)
   - User -> Department (Many-to-One)
   - User -> AssetRequests (One-to-Many)
   - User -> AssetAssignments (One-to-Many)

2. **Asset Relationships**
   - Asset -> Category (Many-to-One)
   - Asset -> Department (Many-to-One)
   - Asset -> Tags (Many-to-Many)
   - Asset -> Maintenance Records (One-to-Many)
   - Asset -> Assignments (One-to-Many)

3. **Request Relationships**
   - AssetRequest -> RequestType (Many-to-One)
   - AssetRequest -> Asset (Many-to-One)
   - AssetRequest -> Approvals (One-to-Many)
   - AssetRequest -> User (Many-to-One)

4. **Department Relationships**
   - Department -> Parent Department (Many-to-One)
   - Department -> Manager (Many-to-One)
   - Department -> Assets (One-to-Many)
   - Department -> Users (One-to-Many)

## Database Indexes

Each model includes appropriate indexes for:
- Primary keys (automatic)
- Foreign keys (automatic)
- Unique fields
- Frequently queried fields
- Search fields
- Ordering fields

## Model Methods

Each model includes standard methods:
- `__str__`: String representation
- `save()`: Custom save logic
- `clean()`: Validation logic
- Property methods for computed fields
- Helper methods for common operations

## Model Signals

Signal handlers are implemented for:
- User profile creation
- Asset status changes
- Request workflow updates
- Audit trail logging
- Cache invalidation