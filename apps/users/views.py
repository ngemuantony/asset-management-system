from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import UserProfile, UserActivityLog
from .serializers import UserSerializer, UserProfileSerializer, UserActivityLogSerializer
from core.permissions import IsAdmin, IsManager
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for managing users"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # for swagger schema generation
            return User.objects.none()
            
        user = self.request.user
        if user.profile.is_admin:
            return User.objects.all().order_by('username')
        elif user.profile.is_manager:
            return User.objects.filter(
                profile__department=user.profile.department
            ).order_by('username')
        return User.objects.filter(id=user.id)

    def get_permissions(self):
        """Set custom permissions for different actions"""
        if self.action in ['create', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdmin]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsAdmin|IsManager]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        """Handle PUT/PATCH requests"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        print(f"Update request data: {request.data}")  # Debug log
        print(f"Partial update: {partial}")  # Debug log
        
        # Only admins can update certain fields
        if not request.user.profile.is_admin:
            restricted_fields = ['is_active', 'is_staff', 'is_superuser']
            for field in restricted_fields:
                if field in request.data:
                    return Response(
                        {"error": f"Only admins can update {field}"},
                        status=status.HTTP_403_FORBIDDEN
                    )

        # For PATCH requests, only update provided fields
        if partial:
            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=True
            )
        else:
            # For PUT requests, require all fields
            serializer = self.get_serializer(
                instance,
                data=request.data
            )

        serializer.is_valid(raise_exception=True)
        print(f"Validated data: {serializer.validated_data}")  # Debug log
        
        self.perform_update(serializer)
        print(f"Updated instance: {serializer.data}")  # Debug log

        return Response(serializer.data)

    def perform_update(self, serializer):
        """Custom update to handle user updates"""
        user = self.request.user
        instance = serializer.instance

        # Allow admins to update any user
        if user.profile.is_admin:
            serializer.save()
            return

        # Allow managers to update users in their department
        if user.profile.is_manager and instance.profile.department == user.profile.department:
            # Prevent managers from changing certain fields
            restricted_fields = ['is_active', 'is_staff', 'is_superuser']
            for field in restricted_fields:
                if field in serializer.validated_data:
                    raise PermissionError(f"Only admins can update {field}")
            serializer.save()
            return

        # Users can only update their own data
        if instance == user:
            # Prevent users from changing restricted fields
            restricted_fields = ['is_active', 'is_staff', 'is_superuser']
            for field in restricted_fields:
                if field in serializer.validated_data:
                    raise PermissionError(f"You cannot update {field}")
            serializer.save()
            return

        raise PermissionError("You don't have permission to update this user")

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Get or update current user's details"""
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        # For PUT/PATCH
        partial = request.method == 'PATCH'
        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a user"""
        if not request.user.profile.is_admin:
            return Response(
                {"error": "Only admins can activate users"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        user.is_active = True
        user.save()
        
        return Response(self.get_serializer(user).data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a user"""
        if not request.user.profile.is_admin:
            return Response(
                {"error": "Only admins can deactivate users"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        user.is_active = False
        user.save()
        
        return Response(self.get_serializer(user).data)

class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user profiles"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.is_admin:
            return UserProfile.objects.all()
        elif user.profile.is_manager:
            return UserProfile.objects.filter(
                department=user.profile.department
            )
        return UserProfile.objects.filter(user=user)

    def get_permissions(self):
        """Set custom permissions for different actions"""
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated]  # Allow all authenticated users to update
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        """Handle PUT/PATCH requests"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        print(f"Update request data: {request.data}")  # Debug log
        
        # Handle phone number specifically
        if 'phone_number' in request.data:
            phone = request.data.get('phone_number')
            if phone is not None:
                # Clean phone number - remove any non-digit characters
                request.data['phone_number'] = str(''.join(filter(str.isdigit, str(phone))))
                print(f"Cleaned phone number: {request.data['phone_number']}")  # Debug log

        # Only allow role updates for admins
        if 'role' in request.data and not request.user.profile.is_admin:
            return Response(
                {"error": "Only admins can update roles"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        print(f"Validated data: {serializer.validated_data}")  # Debug log
        
        self.perform_update(serializer)
        print(f"Updated instance phone: {instance.phone_number}")  # Debug log

        # Force refresh from database
        instance.refresh_from_db()
        print(f"Refreshed instance phone: {instance.phone_number}")  # Debug log

        return Response(self.get_serializer(instance).data)

    def perform_update(self, serializer):
        """Custom update to handle role changes"""
        user = self.request.user
        instance = serializer.instance

        # Users can update their own profile
        if instance.user == user:
            # Prevent users from changing their own role
            if 'role' in serializer.validated_data and not user.profile.is_admin:
                raise PermissionError("You cannot change your own role")
            serializer.save()
            return

        # Allow admins to update any profile
        if user.profile.is_admin:
            serializer.save()
            return

        # Allow managers to update users in their department
        if user.profile.is_manager and instance.department == user.profile.department:
            # Prevent managers from changing roles
            if 'role' in serializer.validated_data:
                raise PermissionError("Only admins can change user roles")
            serializer.save()
            return

        raise PermissionError("You don't have permission to update this user")

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Get or update current user's profile"""
        profile = request.user.profile
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)

        # For PUT/PATCH
        serializer = self.get_serializer(
            profile,
            data=request.data,
            partial=request.method == 'PATCH',
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_phone(self, request, pk=None):
        """Dedicated endpoint for updating phone number"""
        profile = self.get_object()
        phone = request.data.get('phone_number')

        if phone is not None:
            # Clean and validate phone number
            phone = str(''.join(filter(str.isdigit, str(phone))))
            if len(phone) < 9 or len(phone) > 15:
                return Response(
                    {'error': 'Phone number must be between 9 and 15 digits'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            profile.phone_number = phone
            profile.save()
            
            # Force refresh from database
            profile.refresh_from_db()

        serializer = self.get_serializer(profile)
        return Response(serializer.data)

class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing user activity logs"""
    serializer_class = UserActivityLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin|IsManager]
    
    def get_queryset(self):
        user = self.request.user
        queryset = UserActivityLog.objects.all()

        if user.profile.is_manager:
            queryset = queryset.filter(
                user__profile__department=user.profile.department
            )

        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(
                timestamp__range=[start_date, end_date]
            )

        return queryset

    @action(detail=False)
    def statistics(self, request):
        """Get activity statistics"""
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        queryset = self.get_queryset().filter(
            timestamp__gte=start_date
        )
        
        stats = {
            'total_activities': queryset.count(),
            'by_action': queryset.values('action')\
                .annotate(count=Count('id')),
            'by_user': queryset.values('user__username')\
                .annotate(count=Count('id'))\
                .order_by('-count')[:5],
            'by_status': queryset.values('status')\
                .annotate(count=Count('id'))
        }
        
        return Response(stats)
