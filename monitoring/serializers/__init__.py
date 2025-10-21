"""
Monitoring app serializers module

Organizes serializers by domain:
- base: User, Device, Reading (legacy IoT)
- building: Building, Zone (Smart Building)
- sensor: ZoneSensor, ZoneCamera (Smart Building sensors)
- control: HVACControl (Smart Building controls)
- alert: BuildingAlert (Smart Building alerts)
"""

# Base serializers
from .base import (
    UserSerializer,
    DeviceSerializer,
    ReadingSerializer,
    LatestReadingSerializer
)

# Building serializers
from .building import (
    BuildingSerializer,
    ZoneSerializer,
    ZoneDetailSerializer
)

# Sensor serializers
from .sensor import (
    ZoneSensorSerializer,
    ZoneCameraSerializer
)

# Control serializers
from .control import HVACControlSerializer

# Alert serializers
from .alert import BuildingAlertSerializer

# Now add nested fields to ZoneDetailSerializer to avoid circular imports
ZoneDetailSerializer._declared_fields['sensors'] = ZoneSensorSerializer(many=True, read_only=True)
ZoneDetailSerializer._declared_fields['cameras'] = ZoneCameraSerializer(many=True, read_only=True)
ZoneDetailSerializer._declared_fields['hvac'] = HVACControlSerializer(read_only=True)

# Export all serializers
__all__ = [
    # Base
    'UserSerializer',
    'DeviceSerializer',
    'ReadingSerializer',
    'LatestReadingSerializer',
    
    # Building
    'BuildingSerializer',
    'ZoneSerializer',
    'ZoneDetailSerializer',
    
    # Sensor
    'ZoneSensorSerializer',
    'ZoneCameraSerializer',
    
    # Control
    'HVACControlSerializer',
    
    # Alert
    'BuildingAlertSerializer',
]
