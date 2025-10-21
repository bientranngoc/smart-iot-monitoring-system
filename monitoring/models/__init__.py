"""
Monitoring app models module

This module organizes models into logical groups:
- base: User, Device (legacy IoT models)
- building: Building, Zone (Smart Building infrastructure)
- sensor: ZoneSensor, ZoneCamera (Smart Building sensors)
- control: HVACControl, EnergyLog (Smart Building controls)
- alert: BuildingAlert (Smart Building alerts)
- mongodb: Reading, ReadingClient (MongoDB integration)
"""

# Base IoT models
from .base import User, Device

# Smart Building models
from .building import Building, Zone
from .sensor import ZoneSensor, ZoneCamera
from .control import HVACControl, EnergyLog
from .alert import BuildingAlert

# MongoDB models
from .mongodb import Reading, ReadingClient

# Export all models
__all__ = [
    # Base
    'User',
    'Device',
    
    # Building
    'Building',
    'Zone',
    
    # Sensors
    'ZoneSensor',
    'ZoneCamera',
    
    # Control
    'HVACControl',
    'EnergyLog',
    
    # Alert
    'BuildingAlert',
    
    # MongoDB
    'Reading',
    'ReadingClient',
]
