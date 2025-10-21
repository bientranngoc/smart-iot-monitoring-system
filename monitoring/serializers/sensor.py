"""
Smart Building sensor serializers - ZoneSensor and ZoneCamera
"""

from rest_framework import serializers
from monitoring.models import ZoneSensor, ZoneCamera


class ZoneSensorSerializer(serializers.ModelSerializer):
    """Serializer for ZoneSensor model"""
    sensor_type_display = serializers.CharField(source='get_sensor_type_display', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = ZoneSensor
        fields = '__all__'


class ZoneCameraSerializer(serializers.ModelSerializer):
    """Serializer for ZoneCamera model"""
    hls_url = serializers.CharField(read_only=True)
    webrtc_url = serializers.CharField(read_only=True)
    camera_type_display = serializers.CharField(source='get_camera_type_display', read_only=True)
    
    class Meta:
        model = ZoneCamera
        fields = '__all__'
