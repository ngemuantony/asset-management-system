"""
URL configuration for config project.

"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Create API info for Swagger documentation
api_info = openapi.Info(
    title="SPH Asset Management API",
    default_version='v1',
    description="API documentation for SPH Asset Management System",
    terms_of_service="https://www.google.com/policies/terms/",
    contact=openapi.Contact(email="contact@example.com"),
    license=openapi.License(name="BSD License"),
)

# Create schema view for Swagger/ReDoc
schema_view = get_schema_view(
    api_info,
    public=True,
    permission_classes=[permissions.AllowAny],
    patterns=[
        path('api/auth/', include('apps.authentication.urls')),
        path('api/users/', include('apps.users.urls')),
        path('api/departments/', include('apps.departments.urls')),
        path('api/assets/', include('apps.assets.urls')),
        path('api/requests/', include('apps.requests.urls', namespace='requests')),
        path('api/reports/', include('apps.reports.urls', namespace='reports')),
        path('api/categories/', include('apps.categories.urls')),
        path('api/tags/', include('apps.tags.urls')),
    ],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/auth/', include('apps.authentication.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/departments/', include('apps.departments.urls')),
    path('api/assets/', include('apps.assets.urls')),
    path('api/requests/', include('apps.requests.urls', namespace='requests')),
    path('api/reports/', include('apps.reports.urls', namespace='reports')),
    path('api/categories/', include('apps.categories.urls')),
    path('api/tags/', include('apps.tags.urls')),
    
    # Swagger URLs (only in debug mode)
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Add debug toolbar URLs in debug mode
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
