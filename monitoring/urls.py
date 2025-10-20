"""
URL configuration for monitoring app API endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, 
    DeviceViewSet, 
    ReadingViewSet, 
    latest_reading,
    # Smart Building ViewSets
    BuildingViewSet,
    ZoneViewSet,
    BuildingAlertViewSet,
    HVACControlViewSet
)

# Create a router and register ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'readings', ReadingViewSet, basename='reading')

# Smart Building routes
router.register(r'buildings', BuildingViewSet, basename='building')
router.register(r'zones', ZoneViewSet, basename='zone')
router.register(r'building-alerts', BuildingAlertViewSet, basename='building-alert')
router.register(r'hvac-controls', HVACControlViewSet, basename='hvac-control')

urlpatterns = [
    # ViewSet URLs (via router)
    path('', include(router.urls)),
    
    # Legacy endpoint (for backward compatibility)
    path('latest/<int:device_id>/', latest_reading, name='latest-reading'),
]
