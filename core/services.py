from django.db import transaction
from django.contrib.auth import get_user_model
from apps.users.models import UserProfile
import json
from django.core.exceptions import ValidationError

User = get_user_model()

class BaseService:
    """Base service class with performance optimizations"""
    
    @classmethod
    def bulk_create_with_profiles(cls, users_data, batch_size=100):
        """
        Bug: No validation before bulk creation
        Bottleneck: Single transaction for large datasets
        """
        try:
            # Validate data first
            errors = []
            for data in users_data:
                try:
                    cls.validate_user_data(data)
                except ValidationError as e:
                    errors.append(f"Error in data: {data.get('email')} - {str(e)}")
            
            if errors:
                raise ValidationError(errors)
                
            # Split into smaller transactions
            for i in range(0, len(users_data), batch_size):
                with transaction.atomic():
                    batch = users_data[i:i + batch_size]
                    # Process batch
                    cls._process_batch(batch)
                    
        except Exception as e:
            logger.error(f"Bulk creation failed: {str(e)}")
            raise
    
    @classmethod
    def bulk_update(cls, objects, fields, batch_size=100):
        return cls.model.objects.bulk_update(objects, fields, batch_size=batch_size)
    
    @classmethod
    def get_cached(cls, pk):
        cache_key = f"{cls.model.__name__}_{pk}"
        return CacheManager.get_or_set(cache_key, lambda: cls.model.objects.get(pk=pk))
    
    @classmethod
    def bulk_update_with_history(cls, objects, fields, batch_size=100):
        """Bulk update with history tracking"""
        with transaction.atomic():
            # Create history records
            history_records = [
                ModelHistory(
                    model_id=obj.id,
                    changes=json.dumps({field: getattr(obj, field) for field in fields})
                ) for obj in objects
            ]
            ModelHistory.objects.bulk_create(history_records)
            
            # Perform bulk update
            return cls.model.objects.bulk_update(objects, fields, batch_size=batch_size)

def cleanup_expired_sessions():
    """Clean up expired sessions periodically"""
    from django.contrib.sessions.models import Session
    from django.utils import timezone
    
    expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
    count = expired_sessions.count()
    expired_sessions.delete()
    
    logger.info(f"Cleaned up {count} expired sessions")
