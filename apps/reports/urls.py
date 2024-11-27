from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MetricsViewSet, ReportViewSet

app_name = 'reports'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'metrics', MetricsViewSet, basename='metrics')
router.register(r'reports', ReportViewSet, basename='reports')

# Define URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Explicit metric endpoints for better documentation
    path('metrics/dashboard/', 
         MetricsViewSet.as_view({'get': 'dashboard'}), 
         name='metrics-dashboard'),
    
    path('metrics/asset-overview/', 
         MetricsViewSet.as_view({'get': 'asset_overview'}), 
         name='metrics-asset-overview'),
    
    path('metrics/department-usage/', 
         MetricsViewSet.as_view({'get': 'department_metrics'}), 
         name='metrics-department-usage'),
    
    path('metrics/trends/', 
         MetricsViewSet.as_view({'get': 'trending_metrics'}), 
         name='metrics-trends'),
    
    path('metrics/categories/', 
         MetricsViewSet.as_view({'get': 'category_metrics'}), 
         name='metrics-categories'),
    
    path('metrics/lifecycle/', 
         MetricsViewSet.as_view({'get': 'asset_lifecycle'}), 
         name='metrics-lifecycle'),
]
