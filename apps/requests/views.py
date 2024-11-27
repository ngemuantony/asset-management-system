from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdmin, IsManager, IsRequesterOrApprover
from .models import AssetRequest, RequestType
from .serializers import (
    AssetRequestSerializer,
    RequestTypeSerializer,
    RequestApprovalSerializer
)
from .services import RequestService

# Create your views here.

class RequestTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing request types
    
    list:
    Return a list of all request types.
    
    create:
    Create a new request type.
    
    retrieve:
    Return the given request type.
    
    update:
    Update the given request type.
    
    destroy:
    Delete the given request type.
    """
    queryset = RequestType.objects.all()
    serializer_class = RequestTypeSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # for swagger schema generation
            return RequestType.objects.none()
        return RequestType.objects.filter(is_active=True)

class AssetRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing asset requests
    
    list:
    Return a list of all asset requests accessible by the user.
    
    create:
    Create a new asset request.
    
    retrieve:
    Return the given asset request.
    
    update:
    Update the given asset request.
    
    destroy:
    Delete the given asset request.
    """
    serializer_class = AssetRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # for swagger schema generation
            return AssetRequest.objects.none()
            
        user = self.request.user
        if not hasattr(user, 'profile'):  # Handle anonymous or invalid users
            return AssetRequest.objects.none()
            
        if user.profile.role == 'ADMIN':
            return AssetRequest.objects.all()
        elif user.profile.role == 'MANAGER':
            return AssetRequest.objects.filter(
                approvals__approver=user
            ) | AssetRequest.objects.filter(
                requester__profile__department=user.profile.department
            )
        return AssetRequest.objects.filter(requester=user)

    def perform_create(self, serializer):
        RequestService.create_request(
            serializer.validated_data,
            self.request.user
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an asset request"""
        try:
            approval = RequestService.process_approval(
                pk,
                request.user,
                'APPROVED',
                request.data.get('comments')
            )
            return Response(
                RequestApprovalSerializer(approval).data
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject an asset request"""
        try:
            approval = RequestService.process_approval(
                pk,
                request.user,
                'REJECTED',
                request.data.get('comments')
            )
            return Response(
                RequestApprovalSerializer(approval).data
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an asset request"""
        try:
            cancelled_request = RequestService.cancel_request(
                pk,
                request.user
            )
            return Response(
                AssetRequestSerializer(cancelled_request).data
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
