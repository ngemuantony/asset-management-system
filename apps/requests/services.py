from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import AssetRequest, RequestApproval
from apps.assets.models import Asset
from core.utils import send_notification

class RequestService:
    """
    Service class for handling asset request operations
    """
    
    @staticmethod
    @transaction.atomic
    def create_request(data, user):
        """Create a new asset request"""
        request = AssetRequest.objects.create(
            requester=user,
            **data
        )
        
        # Create approval records if required
        if request.request_type.requires_approval:
            for level in range(1, request.request_type.approval_levels + 1):
                RequestApproval.objects.create(
                    request=request,
                    approval_level=level
                )
        
        # Send notifications
        send_notification(
            'request_created',
            request.requester,
            {'request': request}
        )
        
        return request

    @staticmethod
    @transaction.atomic
    def process_approval(request_id, approver, status, comments=None):
        """Process an approval for an asset request"""
        request = AssetRequest.objects.get(id=request_id)
        approval = request.approvals.filter(
            approver__isnull=True,
            status='PENDING'
        ).order_by('approval_level').first()
        
        if not approval:
            raise ValidationError("No pending approvals found")
            
        approval.approver = approver
        approval.status = status
        approval.comments = comments
        approval.approval_date = timezone.now()
        approval.save()
        
        # Check if this was the final approval
        if status == 'APPROVED' and not request.approvals.filter(
            status='PENDING'
        ).exists():
            request.status = 'APPROVED'
            request.save()
            
            # Handle asset assignment if applicable
            if request.asset:
                Asset.objects.filter(id=request.asset.id).update(
                    assigned_to=request.requester
                )
        
        # Send notifications
        send_notification(
            'request_approved' if status == 'APPROVED' else 'request_rejected',
            request.requester,
            {'request': request, 'approval': approval}
        )
        
        return approval

    @staticmethod
    def cancel_request(request_id, user):
        """Cancel an asset request"""
        request = AssetRequest.objects.get(id=request_id)
        
        if request.requester != user and not user.profile.is_admin:
            raise ValidationError("Unauthorized to cancel this request")
            
        if request.status not in ['PENDING', 'APPROVED']:
            raise ValidationError("Cannot cancel request in current status")
            
        request.status = 'CANCELLED'
        request.save()
        
        # Send notifications
        send_notification(
            'request_cancelled',
            request.requester,
            {'request': request}
        )
        
        return request 