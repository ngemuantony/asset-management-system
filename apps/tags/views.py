from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from .models import Tag
from .serializers import TagSerializer
from core.permissions import IsAdminUser, IsManagerUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.

class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tags
    """
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Get the list of tags with asset counts
        """
        if getattr(self, 'swagger_fake_view', False):  # for swagger schema generation
            return Tag.objects.none()
            
        return Tag.objects.all().annotate(
            total_assets=Count('assets')
        )

    @swagger_auto_schema(
        operation_description="List all tags with their asset counts",
        responses={
            200: openapi.Response(
                description="List of tags retrieved successfully",
                examples={
                    "application/json": [{
                        "id": 1,
                        "name": "Laptop",
                        "code": "TAG001",
                        "description": "Computing devices",
                        "color": "#FF0000",
                        "total_assets": 5
                    }]
                }
            )
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get details of a specific tag",
        responses={
            200: TagSerializer,
            404: "Tag not found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new tag",
        request_body=TagSerializer,
        responses={201: TagSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a tag",
        request_body=TagSerializer,
        responses={200: TagSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a tag",
        responses={204: "Tag deleted successfully"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get assets associated with a tag",
        responses={
            200: openapi.Response(
                description="List of assets retrieved successfully",
                examples={
                    "application/json": {
                        "count": 5,
                        "assets": ["Asset details..."]
                    }
                }
            )
        }
    )
    @action(detail=True, methods=['get'])
    def assets(self, request, pk=None):
        """Get assets associated with this tag"""
        tag = self.get_object()
        assets = tag.assets.all()
        return Response({
            'count': assets.count(),
            'assets': assets.values('id', 'name', 'asset_id', 'status')
        })
