"""
Django admin registration for monitoring app models
"""

from django.contrib import admin
from monitoring.models import (
    # Base models
    User,
    Device,
    
    # Smart Building models
    Building,
    Zone,
    ZoneSensor,
    ZoneCamera,
    HVACControl,
    EnergyLog,
    BuildingAlert
)


# ============ BASE IOT MODELS ============

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'created_at']
    search_fields = ['username']
    ordering = ['-created_at']


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'user', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['name']
    ordering = ['-created_at']


# ============ SMART BUILDING MODELS ============

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'address', 'floors', 'total_area', 'manager', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'address']
    ordering = ['-created_at']


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'building', 'floor', 'zone_type', 'area', 'is_active']
    list_filter = ['building', 'floor', 'zone_type', 'is_active']
    search_fields = ['name']
    ordering = ['building', 'floor', 'name']


@admin.register(ZoneSensor)
class ZoneSensorAdmin(admin.ModelAdmin):
    list_display = ['id', 'zone', 'device', 'sensor_type', 'latest_reading', 'latest_reading_time', 'is_active']
    list_filter = ['zone', 'sensor_type', 'is_active']
    search_fields = ['location_description']
    ordering = ['zone', 'sensor_type']


@admin.register(ZoneCamera)
class ZoneCameraAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'zone', 'camera_type', 'mediamtx_path', 'is_active']
    list_filter = ['zone', 'camera_type', 'is_active']
    search_fields = ['name', 'mediamtx_path']
    ordering = ['zone', 'name']


@admin.register(HVACControl)
class HVACControlAdmin(admin.ModelAdmin):
    list_display = ['id', 'zone', 'mode', 'current_temperature', 'set_temperature', 'is_cooling', 'is_heating', 'fan_speed']
    list_filter = ['mode', 'is_cooling', 'is_heating']
    search_fields = ['zone__name']
    ordering = ['zone']


@admin.register(EnergyLog)
class EnergyLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'zone', 'timestamp', 'hvac_consumption', 'lighting_consumption', 'total_consumption', 'cost']
    list_filter = ['zone', 'timestamp']
    search_fields = ['zone__name']
    ordering = ['-timestamp']


@admin.register(BuildingAlert)
class BuildingAlertAdmin(admin.ModelAdmin):
    list_display = ['id', 'zone', 'alert_type', 'severity', 'title', 'acknowledged', 'created_at']
    list_filter = ['zone', 'alert_type', 'severity', 'acknowledged', 'created_at']
    search_fields = ['title', 'message']
    ordering = ['-created_at']
    
    actions = ['mark_as_acknowledged']
    
    def mark_as_acknowledged(self, request, queryset):
        """Admin action to acknowledge multiple alerts"""
        from django.utils import timezone
        queryset.update(
            acknowledged=True,
            acknowledged_by=request.user if request.user.is_authenticated else None,
            acknowledged_at=timezone.now()
        )
        self.message_user(request, f"{queryset.count()} alerts marked as acknowledged.")
    mark_as_acknowledged.short_description = "Mark selected alerts as acknowledged"
