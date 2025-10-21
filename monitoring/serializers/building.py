"""
Smart Building serializers - Building and Zone
"""

from rest_framework import serializers
from monitoring.models import Building, Zone


class BuildingSerializer(serializers.ModelSerializer):
    """Serializer for Building model"""
    total_zones = serializers.IntegerField(read_only=True)
    active_alerts = serializers.IntegerField(read_only=True)
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Building
        fields = '__all__'


class ZoneSerializer(serializers.ModelSerializer):
    """Basic Zone serializer"""
    zone_type_display = serializers.CharField(source='get_zone_type_display', read_only=True)
    building_name = serializers.CharField(source='building.name', read_only=True)
    current_status = serializers.CharField(read_only=True)
    
    class Meta:
        model = Zone
        fields = '__all__'


class ZoneDetailSerializer(serializers.ModelSerializer):
    """Detailed Zone serializer with related objects (defined in __init__.py to avoid circular imports)"""
    zone_type_display = serializers.CharField(source='get_zone_type_display', read_only=True)
    building_name = serializers.CharField(source='building.name', read_only=True)
    current_status = serializers.CharField(read_only=True)
    
    class Meta:
        model = Zone
        fields = '__all__'
