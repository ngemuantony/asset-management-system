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

    class Meta:
        abstract = True
```

## Authentication Models

### CustomUser
```python
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30)
    login_count = models.IntegerField(default=0)
    last_login_ip = models.GenericIPAddressField(null=True)
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True)
    password_changed_at = models.DateTimeField(null=True)
    force_password_change = models.BooleanField(default=False)
```

### UserProfile
```python
class UserProfile(AuditableModel):
    user = models.OneToOneField(CustomUser)
    role = models.CharField(choices=ROLE_CHOICES)
    department = models.ForeignKey('Department')
    employee_id = models.CharField(unique=True)
    phone_number = models.CharField(null=True)
    status = models.CharField(choices=STATUS_CHOICES)
    profile_image = models.ImageField(upload_to='profile_images/')
    bio = models.TextField(blank=True)
    skills = models.JSONField(default=dict)
    preferences = models.JSONField(default=dict)
```

### UserActivityLog
```python
class UserActivityLog(AuditableModel):
    user = models.ForeignKey(CustomUser)
    action = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField()
    action_details = models.JSONField()
    status = models.CharField()
    timestamp = models.DateTimeField()
    session_id = models.CharField(null=True)
    request_method = models.CharField(max_length=10)
    request_path = models.CharField()
    response_status = models.IntegerField()
```

## Asset Management Models

### Asset
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
    manufacturer = models.CharField()
    model_number = models.CharField()
    serial_number = models.CharField(unique=True)
    supplier = models.ForeignKey('Supplier')
    warranty_info = models.JSONField()
    depreciation_rate = models.DecimalField()
    expected_lifetime = models.IntegerField()
    disposal_date = models.DateField(null=True)
    disposal_method = models.CharField(null=True)
    disposal_value = models.DecimalField(null=True)
```

### Category
```python
class Category(AuditableModel):
    name = models.CharField(unique=True)
    code = models.CharField(unique=True)
    description = models.TextField()
    parent = models.ForeignKey('self', null=True)
    attributes = models.JSONField()
    icon = models.CharField()
    color_code = models.CharField()
    default_lifetime = models.IntegerField()
    default_depreciation = models.DecimalField()
    maintenance_frequency = models.IntegerField()
    required_approvals = models.IntegerField()
```

### Tag
```python
class Tag(AuditableModel):
    name = models.CharField(unique=True)
    description = models.TextField()
    color = models.CharField()
    code = models.CharField(unique=True)
    icon = models.CharField()
    type = models.CharField()
    priority = models.IntegerField()
    metadata = models.JSONField()
```

### AssetMaintenance
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
    parts_used = models.JSONField()
    labor_hours = models.DecimalField()
    next_maintenance = models.DateField()
    maintenance_provider = models.CharField()
    warranty_claim = models.BooleanField()
    resolution = models.TextField()
    status = models.CharField()
```

### AssetAssignment
```python
class AssetAssignment(AuditableModel):
    asset = models.ForeignKey(Asset)
    assigned_to = models.ForeignKey(CustomUser)
    assigned_by = models.ForeignKey(CustomUser)
    assigned_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True)
    assignment_type = models.CharField()
    notes = models.TextField()
    condition_before = models.TextField()
    condition_after = models.TextField()
    acknowledgment = models.BooleanField()
    return_condition = models.CharField()
    return_notes = models.TextField()
```

## Request Management Models

### RequestType
```python
class RequestType(AuditableModel):
    name = models.CharField(unique=True)
    code = models.CharField(unique=True)
    description = models.TextField()
    requires_approval = models.BooleanField()
    approval_levels = models.PositiveIntegerField()
    form_template = models.JSONField()
    workflow = models.JSONField()
    sla_hours = models.IntegerField()
    category = models.CharField()
    notification_template = models.TextField()
```

### AssetRequest
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
    form_data = models.JSONField()
    workflow_state = models.CharField()
    sla_breach = models.BooleanField()
    resolution_time = models.DurationField()
    satisfaction_rating = models.IntegerField()
```

### RequestApproval
```python
class RequestApproval(AuditableModel):
    request = models.ForeignKey(AssetRequest)
    approver = models.ForeignKey(CustomUser)
    approval_level = models.PositiveIntegerField()
    status = models.CharField(choices=REQUEST_STATUS_CHOICES)
    comments = models.TextField()
    approval_date = models.DateTimeField(null=True)
    delegation = models.ForeignKey(CustomUser, null=True)
    reminder_sent = models.BooleanField()
    last_reminder = models.DateTimeField()
    approval_token = models.CharField()
```

## Report Models

### ReportTemplate
```python
class ReportTemplate(AuditableModel):
    name = models.CharField()
    template_type = models.CharField()
    template_file = models.FileField()
    template_config = models.JSONField()
    parameters = models.JSONField()
    filters = models.JSONField()
    sorting = models.JSONField()
    grouping = models.JSONField()
    charts = models.JSONField()
    access_roles = models.JSONField()
```

### Report
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
    schedule_config = models.JSONField()
    recipients = models.JSONField()
    last_sent = models.DateTimeField()
    error_log = models.TextField()
```

## Department Model

### Department
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
    budget = models.DecimalField()
    cost_center = models.CharField()
    asset_limit = models.IntegerField()
    approval_chain = models.JSONField()
```

## Model Relationships

### User Relationships
- User -> UserProfile (One-to-One)
- User -> Department (Many-to-One)
- User -> AssetRequests (One-to-Many)
- User -> AssetAssignments (One-to-Many)
- User -> RequestApprovals (One-to-Many)
- User -> Reports (One-to-Many)
- User -> Departments (One-to-Many, as manager)

### Asset Relationships
- Asset -> Category (Many-to-One)
- Asset -> Department (Many-to-One)
- Asset -> Tags (Many-to-Many)
- Asset -> Maintenance Records (One-to-Many)
- Asset -> Assignments (One-to-Many)
- Asset -> Requests (One-to-Many)
- Asset -> Reports (Many-to-Many)

### Request Relationships
- AssetRequest -> RequestType (Many-to-One)
- AssetRequest -> Asset (Many-to-One)
- AssetRequest -> Approvals (One-to-Many)
- AssetRequest -> User (Many-to-One)
- AssetRequest -> Department (Many-to-One)

### Department Relationships
- Department -> Parent Department (Many-to-One)
- Department -> Manager (Many-to-One)
- Department -> Assets (One-to-Many)
- Department -> Users (One-to-Many)
- Department -> Requests (One-to-Many)
- Department -> Reports (One-to-Many)

## Model Methods and Properties

### Common Methods
- `__str__`: String representation
- `save()`: Custom save logic
- `clean()`: Validation logic
- `delete()`: Soft delete implementation
- `restore()`: Restore soft-deleted items

### Computed Properties
- Asset value calculation
- Depreciation calculation
- Request status computation
- Approval chain validation
- SLA breach checking
- Budget utilization
- Asset utilization rates

## Model Signals

### User Signals
- Profile creation
- Activity logging
- Password change notification
- Role change notification

### Asset Signals
- Status change notification
- Maintenance scheduling
- Assignment notifications
- Value updates
- QR code generation

### Request Signals
- Approval notifications
- SLA monitoring
- Status updates
- Assignment processing

### Report Signals
- Generation completion
- Distribution triggers
- Error notifications
- Schedule processing 