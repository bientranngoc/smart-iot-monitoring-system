from rest_framework import serializers
from .models import User, Device
from .models import Building, Zone, ZoneSensor, ZoneCamera, HVACControl, BuildingAlert

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (MySQL)"""
    class Meta:
        model = User
        fields = ['id', 'username', 'created_at']
        read_only_fields = ['id', 'created_at']

class DeviceSerializer(serializers.ModelSerializer):
    """Serializer for Device model (MySQL)"""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Device
        fields = ['id', 'name', 'user', 'user_id', 'created_at']
        read_only_fields = ['id', 'created_at']

class ReadingSerializer(serializers.Serializer):
    """Serializer for Reading dataclass (MongoDB via pymongo)
    
    This is a plain Serializer (not ModelSerializer) because Reading
    is stored in MongoDB using pymongo, not Django ORM.
    """
    device_id = serializers.IntegerField()
    temperature = serializers.FloatField()
    humidity = serializers.FloatField()
    timestamp = serializers.DateTimeField()
    
    # Optional: Add _id field for MongoDB documents
    id = serializers.CharField(source='_id', read_only=True, required=False)

class LatestReadingSerializer(serializers.Serializer):
    """Serializer for latest readings from Redis cache"""
    device_id = serializers.IntegerField()
    temperature = serializers.FloatField()
    humidity = serializers.FloatField()
    timestamp = serializers.DateTimeField()
    status = serializers.CharField(default='online')  # online/offline based on TTL


# ============ SMART BUILDING SERIALIZERS ============

class BuildingSerializer(serializers.ModelSerializer):
    """Serializer for Building model"""
    total_zones = serializers.IntegerField(read_only=True)
    active_alerts = serializers.IntegerField(read_only=True)
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Building
        fields = '__all__'


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


class ZoneDetailSerializer(serializers.ModelSerializer):
    """Detailed Zone serializer with related objects"""
    sensors = ZoneSensorSerializer(many=True, read_only=True)
    cameras = ZoneCameraSerializer(many=True, read_only=True)
    hvac = HVACControlSerializer(read_only=True)
    current_status = serializers.CharField(read_only=True)
    zone_type_display = serializers.CharField(source='get_zone_type_display', read_only=True)
    building_name = serializers.CharField(source='building.name', read_only=True)
    
    class Meta:
        model = Zone
        fields = '__all__'


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