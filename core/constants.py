# Status Constants
STATUS_ACTIVE = 'ACTIVE'
STATUS_INACTIVE = 'INACTIVE'
STATUS_PENDING = 'PENDING'
STATUS_ARCHIVED = 'ARCHIVED'
STATUS_DELETED = 'DELETED'

STATUS_CHOICES = [
    (STATUS_ACTIVE, 'Active'),
    (STATUS_INACTIVE, 'Inactive'),
    (STATUS_PENDING, 'Pending'),
    (STATUS_ARCHIVED, 'Archived'),
    (STATUS_DELETED, 'Deleted'),
]

# Role Constants
ROLE_ADMIN = 'ADMIN'
ROLE_MANAGER = 'MANAGER'
ROLE_STAFF = 'STAFF'
ROLE_USER = 'USER'
ROLE_TECHNICIAN = 'TECHNICIAN'

ROLE_CHOICES = [
    (ROLE_ADMIN, 'Administrator'),
    (ROLE_MANAGER, 'Department Manager'),
    (ROLE_STAFF, 'Staff Member'),
    (ROLE_USER, 'Regular User'),
    (ROLE_TECHNICIAN, 'Technician'),
]

# Cache Settings
CACHE_TIMEOUT = 60 * 15  # 15 minutes
CACHE_KEY_PREFIX = 'sph_asset_'

# Pagination Settings
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# File Upload Settings
ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'application/pdf']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Asset Status Constants
ASSET_STATUS_AVAILABLE = 'AVAILABLE'
ASSET_STATUS_ASSIGNED = 'ASSIGNED'
ASSET_STATUS_MAINTENANCE = 'MAINTENANCE'
ASSET_STATUS_RETIRED = 'RETIRED'

ASSET_STATUS_CHOICES = [
    (ASSET_STATUS_AVAILABLE, 'Available'),
    (ASSET_STATUS_ASSIGNED, 'Assigned'),
    (ASSET_STATUS_MAINTENANCE, 'Under Maintenance'),
    (ASSET_STATUS_RETIRED, 'Retired'),
]

# Request Status Constants
REQUEST_STATUS_PENDING = 'PENDING'
REQUEST_STATUS_APPROVED = 'APPROVED'
REQUEST_STATUS_REJECTED = 'REJECTED'
REQUEST_STATUS_CANCELLED = 'CANCELLED'
REQUEST_STATUS_COMPLETED = 'COMPLETED'

REQUEST_STATUS_CHOICES = [
    (REQUEST_STATUS_PENDING, 'Pending'),
    (REQUEST_STATUS_APPROVED, 'Approved'),
    (REQUEST_STATUS_REJECTED, 'Rejected'),
    (REQUEST_STATUS_CANCELLED, 'Cancelled'),
    (REQUEST_STATUS_COMPLETED, 'Completed'),
]

REQUEST_PRIORITY_LOW = 'LOW'
REQUEST_PRIORITY_MEDIUM = 'MEDIUM'
REQUEST_PRIORITY_HIGH = 'HIGH'
REQUEST_PRIORITY_URGENT = 'URGENT'

REQUEST_PRIORITY_CHOICES = [
    (REQUEST_PRIORITY_LOW, 'Low'),
    (REQUEST_PRIORITY_MEDIUM, 'Medium'),
    (REQUEST_PRIORITY_HIGH, 'High'),
    (REQUEST_PRIORITY_URGENT, 'Urgent'),
]

# Error Messages
ERROR_MESSAGES = {
    'INVALID_CREDENTIALS': 'Invalid credentials provided.',
    'USER_INACTIVE': 'User account is inactive.',
    'PERMISSION_DENIED': 'You do not have permission to perform this action.',
    'OBJECT_NOT_FOUND': 'Requested object not found.',
    'INVALID_REQUEST': 'Invalid request data provided.',
}

# Success Messages
SUCCESS_MESSAGES = {
    'CREATED': 'Object created successfully.',
    'UPDATED': 'Object updated successfully.',
    'DELETED': 'Object deleted successfully.',
    'STATUS_CHANGED': 'Status changed successfully.',
} 