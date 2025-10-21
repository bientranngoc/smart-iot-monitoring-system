"""
Smart Building control serializers - HVACControl
"""

from rest_framework import serializers
from monitoring.models import HVACControl


class HVACControlSerializer(serializers.ModelSerializer):
    """Serializer for HVACControl model"""
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    mode_display = serializers.CharField(source='get_mode_display', read_only=True)
    status = serializers.SerializerMethodField()
    
    def get_status(self, obj):
        """Return human-readable HVAC status"""
        if obj.is_cooling:
            return 'Cooling'
        elif obj.is_heating:
            return 'Heating'
        else:
            return 'Standby'
    
    class Meta:
        model = HVACControl
        fields = '__all__'
