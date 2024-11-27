from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from .models import Department
from .serializers import DepartmentSerializer
from core.permissions import IsAdminUser, IsManagerUser
from core.cache_utils import cache_department_tree
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Prefetch
from apps.users.models import UserProfile

# Create your views here.

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminUser|IsManagerUser]

    def get_queryset(self):
        """Optimized queryset with select_related and prefetch_related"""
        queryset = Department.objects.select_related('parent')\
            .prefetch_related(
                Prefetch('sub_departments', queryset=Department.objects.select_related('parent')),
                Prefetch('department_users', queryset=UserProfile.objects.select_related('user')),
                'asset_set'
            ).annotate(
                user_count=Count('department_users', distinct=True),
                asset_count=Count('asset_set', distinct=True)
            )
        
        # Add pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Optimized stats retrieval"""
        cache_key = f'department_stats_{pk}'
        stats = cache.get(cache_key)
        
        if not stats:
            department = self.get_object()
            stats = {
                'total_users': department.department_users.count(),
                'total_assets': department.asset_set.count(),
                'active_users': department.department_users.filter(
                    is_active=True
                ).count(),
                'last_updated': timezone.now().isoformat()
            }
            cache.set(cache_key, stats, timeout=300)  # Cache for 5 minutes
        
        return Response(stats)

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """
        Get users in department.
        """
        department = self.get_object()
        users = department.department_users.all()
        from apps.users.serializers import UserProfileSerializer
        serializer = UserProfileSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def assets(self, request, pk=None):
        """
        Get assets in department.
        """
        department = self.get_object()
        assets = department.asset_set.all()
        from apps.assets.serializers import AssetSerializer
        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Cache department tree when listing
        cache_department_tree(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
