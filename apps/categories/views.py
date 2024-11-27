from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Category
from .serializers import CategorySerializer, CategoryDetailSerializer
from core.permissions import IsAdminUser, IsManagerUser
from rest_framework.decorators import action
from rest_framework.response import Response

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser|IsManagerUser]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        return CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.all()
        # Filter root categories (no parent)
        if self.action == 'list' and self.request.query_params.get('root', False):
            queryset = queryset.filter(parent=None)
        return queryset

    @action(detail=True)
    def subcategories(self, request, pk=None):
        """Get all subcategories of a category"""
        category = self.get_object()
        subcategories = category.subcategories.all()
        serializer = self.get_serializer(subcategories, many=True)
        return Response(serializer.data)
