"""
Monitoring services module

Business logic layer for Smart Building operations:
- alert_service: Threshold checking and alert creation
- hvac_service: Automatic HVAC control
- camera_service: Camera recording triggers
- cache_service: Redis caching operations
"""

from .alert_service import check_building_thresholds
from .hvac_service import auto_control_hvac
from .camera_service import trigger_camera_recording
from .cache_service import (
    cache_latest_reading,
    get_latest_reading,
    get_all_latest_readings,
    clear_device_cache,
    get_redis_client
)

__all__ = [
    # Alert service
    'check_building_thresholds',
    
    # HVAC service
    'auto_control_hvac',
    
    # Camera service
    'trigger_camera_recording',
    
    # Cache service
    'cache_latest_reading',
    'get_latest_reading',
    'get_all_latest_readings',
    'clear_device_cache',
    'get_redis_client',
]
