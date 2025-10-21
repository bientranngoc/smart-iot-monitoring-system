"""
Monitoring views module

Organizes ViewSets by domain:
- base: User, Device, Reading (legacy IoT)
- building: Building, Zone (Smart Building)
- alert: BuildingAlert (Smart Building alerts)
- control: HVACControl (Smart Building HVAC)
"""

# Base views
from .base import (
    UserViewSet,
    DeviceViewSet,
    ReadingViewSet,
    latest_reading
)

# Smart Building views
from .building import (
    BuildingViewSet,
    ZoneViewSet
)

# Alert views
from .alert import BuildingAlertViewSet

# Control views
from .control import HVACControlViewSet

__all__ = [
    # Base
    'UserViewSet',
    'DeviceViewSet',
    'ReadingViewSet',
    'latest_reading',
    
    # Building
    'BuildingViewSet',
    'ZoneViewSet',
    
    # Alert
    'BuildingAlertViewSet',
    
    # Control
    'HVACControlViewSet',
]
