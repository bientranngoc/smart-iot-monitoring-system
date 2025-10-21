"""
Smart Building alert serializers - BuildingAlert
"""

from rest_framework import serializers
from monitoring.models import BuildingAlert


class BuildingAlertSerializer(serializers.ModelSerializer):
    """Serializer for BuildingAlert model"""
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    building_name = serializers.CharField(source='zone.building.name', read_only=True)
    floor = serializers.IntegerField(source='zone.floor', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    camera_name = serializers.CharField(source='camera.name', read_only=True, allow_null=True)
    acknowledged_by_username = serializers.CharField(source='acknowledged_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = BuildingAlert
        fields = '__all__'
