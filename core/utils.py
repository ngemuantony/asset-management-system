import uuid
from django.utils import timezone
from django.core.cache import cache
from .constants import CACHE_TIMEOUT
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import string
import random

def generate_qr_code(data):
    """
    Generate QR code from data
    
    Args:
        data (str): Data to encode in QR code
        
    Returns:
        ContentFile: QR code image as a ContentFile
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert PIL image to ContentFile
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return ContentFile(buffer.getvalue())

def generate_unique_id(prefix='', length=6):
    """
    Generate a unique ID with optional prefix
    
    Args:
        prefix (str): Prefix for the ID
        length (int): Length of random part
        
    Returns:
        str: Generated unique ID
    """
    chars = string.ascii_uppercase + string.digits
    random_str = ''.join(random.choices(chars, k=length))
    return f"{prefix}{random_str}" if prefix else random_str

def get_file_path(instance, filename):
    """
    Generate unique file path for uploads
    
    Args:
        instance: Model instance
        filename (str): Original filename
        
    Returns:
        str: Unique file path
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"uploads/{instance.__class__.__name__.lower()}/{filename}"

def format_currency(amount):
    """
    Format amount as currency
    
    Args:
        amount (Decimal): Amount to format
        
    Returns:
        str: Formatted currency string
    """
    if amount is None:
        return "0.00"
    return "{:,.2f}".format(amount)

def generate_pdf(template_file, data):
    """
    Generate PDF from template and data
    
    Args:
        template_file (File): Template file
        data (dict): Data to render in template
        
    Returns:
        ContentFile: Generated PDF as ContentFile
    """
    # TODO: Implement PDF generation
    # This is a placeholder that should be implemented based on your PDF generation needs
    # You might want to use libraries like reportlab, WeasyPrint, or xhtml2pdf
    pass

def generate_excel(data, format='EXCEL'):
    """
    Generate Excel/CSV file from data
    
    Args:
        data (dict): Data to include in file
        format (str): 'EXCEL' or 'CSV'
        
    Returns:
        ContentFile: Generated file as ContentFile
    """
    # TODO: Implement Excel/CSV generation
    # This is a placeholder that should be implemented based on your needs
    # You might want to use libraries like openpyxl or csv
    pass

def cache_key_generator(model_name, object_id):
    """Generate a cache key for an object."""
    return f"{model_name.lower()}_{object_id}"

class CacheManager:
    """Manager for handling cache operations."""
    
    @staticmethod
    def get_or_set(key, callback, timeout=CACHE_TIMEOUT):
        """Get value from cache or set it if not present."""
        value = cache.get(key)
        if value is None:
            value = callback()
            cache.set(key, value, timeout)
        return value

    @staticmethod
    def invalidate(key):
        """Remove a key from cache."""
        cache.delete(key)

    @staticmethod
    def get_or_set_with_version(key, callback, timeout=CACHE_TIMEOUT):
        """Version-aware caching"""
        cache_key = f"{key}_v{get_cache_version()}"
        return CacheManager.get_or_set(cache_key, callback, timeout)

    @staticmethod
    def invalidate_patterns(pattern):
        """Invalidate all keys matching pattern"""
        keys = cache.keys(f"*{pattern}*")
        cache.delete_many(keys)

def get_current_user(request):
    """Get the current authenticated user."""
    return request.user if request.user.is_authenticated else None

def update_model_status(instance, status, user=None):
    """Update model status with tracking."""
    instance.status = status
    instance.updated_at = timezone.now()
    if user and hasattr(instance, 'last_modified_by'):
        instance.last_modified_by = user
    instance.save()
    return instance

def send_notification(notification_type, recipient, context):
    """
    Send notifications to users
    Args:
        notification_type (str): Type of notification
        recipient (User): User to receive notification
        context (dict): Context data for notification
    """
    # TODO: Implement actual notification sending logic
    # This is a placeholder that just prints the notification
    print(f"Sending {notification_type} notification to {recipient}")
    print(f"Context: {context}")
    
    # In future, implement actual notification sending:
    # - Email notifications
    # - In-app notifications
    # - Push notifications
    # etc.
    return True
