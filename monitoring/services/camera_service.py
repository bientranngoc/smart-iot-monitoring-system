"""
Camera service - Camera recording triggers
"""

import logging
from django.utils import timezone
from monitoring.models import Zone, BuildingAlert

logger = logging.getLogger(__name__)


def trigger_camera_recording(zone: Zone, alert: BuildingAlert) -> bool:
    """
    Trigger camera recording when alert is created
    
    Args:
        zone: The Zone where the alert occurred
        alert: The BuildingAlert instance
        
    Returns:
        True if recording was triggered, False otherwise
    """
    try:
        camera = zone.cameras.filter(is_active=True).first()
        if not camera:
            logger.debug("No active camera found for zone: %s", zone.name)
            return False
        
        recording_path = f"/recordings/{camera.mediamtx_path}/{alert.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        
        alert.camera = camera
        alert.video_recording_path = recording_path
        alert.save()
        
        logger.info("Camera recording marked: %s -> %s", camera.name, recording_path)
        return True
        
    except Exception as e:
        logger.error("Failed to trigger camera recording: %s", e)
        return False
