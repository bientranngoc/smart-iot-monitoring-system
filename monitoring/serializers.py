from rest_framework import serializers
from .models import User, Device

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