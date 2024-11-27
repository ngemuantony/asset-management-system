from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AssetRequest, RequestApproval
from django.utils import timezone
from core.utils import send_notification

@receiver(post_save, sender=RequestApproval)
def handle_request_approval(sender, instance, created, **kwargs):
    """Handle post-save actions for request approvals"""
    if not created and instance.status in ['APPROVED', 'REJECTED']:
        request = instance.request
        
        # Check if this was the final approval needed
        pending_approvals = request.approvals.filter(status='PENDING').count()
        
        if pending_approvals == 0:
            if all(approval.status == 'APPROVED' for approval in request.approvals.all()):
                request.status = 'APPROVED'
                request.completion_date = timezone.now()
            else:
                request.status = 'REJECTED'
            
            request.save()
            
            # Send notification
            notification_type = 'request_approved' if request.status == 'APPROVED' else 'request_rejected'
            send_notification(
                notification_type,
                request.requester,
                {'request': request}
            )

@receiver(post_save, sender=AssetRequest)
def handle_request_creation(sender, instance, created, **kwargs):
    """Handle post-save actions for asset requests"""
    if created:
        # Notify relevant managers/admins
        managers = instance.requester.profile.department.department_users.filter(
            profile__role='MANAGER'
        )
        
        for manager in managers:
            send_notification(
                'new_request_for_approval',
                manager,
                {'request': instance}
            ) 