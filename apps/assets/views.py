from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import Asset, AssetMaintenance, AssetAssignment, AssetRequest
from .serializers import (
    AssetSerializer, 
    AssetCreateUpdateSerializer,
    AssetMaintenanceSerializer,
    AssetAssignmentSerializer,
    AssetRequestSerializer
)
from core.permissions import IsAdminUser, IsManagerUser
from core.utils import generate_qr_code

class AssetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing assets
    """
    queryset = Asset.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AssetCreateUpdateSerializer
        return AssetSerializer

    def get_queryset(self):
        queryset = Asset.objects.all()
        
        # Filter by status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(asset_status=status)
            
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
            
        # Filter by department
        department = self.request.query_params.get('department', None)
        if department:
            queryset = queryset.filter(department_id=department)
            
        # Search by name or asset_id
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(asset_id__icontains=search)
            )
            
        return queryset

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign asset to user"""
        asset = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {"error": "User ID is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            assignment = AssetAssignment.objects.create(
                asset=asset,
                assigned_to_id=user_id,
                assigned_by=request.user.profile,
                expected_return_date=request.data.get('expected_return_date')
            )
            
            asset.assigned_to_id = user_id
            asset.asset_status = 'ASSIGNED'
            asset.save()
            
            return Response(
                AssetAssignmentSerializer(assignment).data,
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def return_asset(self, request, pk=None):
        """Return an assigned asset"""
        asset = self.get_object()
        
        if not asset.assigned_to:
            return Response(
                {"error": "Asset is not assigned"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Update latest assignment
            assignment = asset.assignment_history.latest('assigned_date')
            assignment.return_date = timezone.now()
            assignment.return_notes = request.data.get('return_notes', '')
            assignment.return_condition = request.data.get('return_condition', '')
            assignment.save()
            
            # Update asset status
            asset.assigned_to = None
            asset.asset_status = 'AVAILABLE'
            asset.save()
            
            return Response(
                AssetAssignmentSerializer(assignment).data
            )
        except AssetAssignment.DoesNotExist:
            return Response(
                {"error": "No assignment found"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def maintenance(self, request, pk=None):
        """Record asset maintenance"""
        asset = self.get_object()
        
        serializer = AssetMaintenanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                asset=asset,
                performed_by=request.user.profile
            )
            
            # Update asset status and maintenance date
            asset.asset_status = 'AVAILABLE'
            asset.last_maintenance = serializer.validated_data['maintenance_date']
            asset.save()
            
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['get'])
    def qr_code(self, request, pk=None):
        """Generate QR code for asset"""
        asset = self.get_object()
        
        if not asset.qr_code:
            try:
                qr_code = generate_qr_code(
                    f'Asset ID: {asset.asset_id}\nName: {asset.name}'
                )
                asset.qr_code.save(
                    f'asset_qr_{asset.asset_id}.png',
                    qr_code,
                    save=True
                )
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        return Response({
            "qr_code_url": request.build_absolute_uri(asset.qr_code.url)
        })