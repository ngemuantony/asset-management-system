from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RequestTypeViewSet, AssetRequestViewSet

app_name = 'requests'

router = DefaultRouter()
router.register(r'types', RequestTypeViewSet, basename='request-type')
router.register(r'', AssetRequestViewSet, basename='request')

urlpatterns = [
    path('', include(router.urls)),
]
