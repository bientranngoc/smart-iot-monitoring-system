"""
Alert service - Smart Building threshold checking and alert creation
"""

import logging
from typing import List
from monitoring.models import BuildingAlert, ZoneSensor

logger = logging.getLogger(__name__)


def check_building_thresholds(zone_sensor: ZoneSensor, temperature: float = None, humidity: float = None) -> int:
    """
    Check if sensor values exceed zone thresholds and create alerts
    
    Args:
        zone_sensor: The ZoneSensor instance
        temperature: Current temperature reading (optional)
        humidity: Current humidity reading (optional)
        
    Returns:
        Number of alerts created
    """
    zone = zone_sensor.zone
    alerts_created = []
    
    # Check temperature thresholds
    if zone_sensor.sensor_type == 'TEMPERATURE' and temperature is not None:
        if temperature < zone.temp_min:
            alert = BuildingAlert.objects.create(
                zone=zone,
                alert_type='TEMPERATURE',
                severity='WARNING',
                title=f'Temperature Too Low',
                message=f'{zone.name}: {temperature}°C (Min: {zone.temp_min}°C)',
                sensor_value=temperature,
                sensor_type='TEMPERATURE'
            )
            alerts_created.append(alert)
            logger.warning("⚠️  ALERT: Temperature too low in %s: %s°C", zone.name, temperature)
            
        elif temperature > zone.temp_max:
            severity = 'CRITICAL' if temperature > zone.temp_max + 3 else 'WARNING'
            alert = BuildingAlert.objects.create(
                zone=zone,
                alert_type='TEMPERATURE',
                severity=severity,
                title=f'Temperature Too High',
                message=f'{zone.name}: {temperature}°C (Max: {zone.temp_max}°C)',
                sensor_value=temperature,
                sensor_type='TEMPERATURE'
            )
            alerts_created.append(alert)
            logger.warning("⚠️  ALERT: Temperature too high in %s: %s°C", zone.name, temperature)
    
    # Check humidity thresholds
    if zone_sensor.sensor_type == 'HUMIDITY' and humidity is not None:
        if humidity < zone.humidity_min or humidity > zone.humidity_max:
            alert = BuildingAlert.objects.create(
                zone=zone,
                alert_type='HUMIDITY',
                severity='WARNING',
                title=f'Humidity Out of Range',
                message=f'{zone.name}: {humidity}% (Range: {zone.humidity_min}-{zone.humidity_max}%)',
                sensor_value=humidity,
                sensor_type='HUMIDITY'
            )
            alerts_created.append(alert)
            logger.warning("⚠️  ALERT: Humidity out of range in %s: %s%%", zone.name, humidity)
    
    # Start camera recording if alerts created
    if alerts_created:
        from .camera_service import trigger_camera_recording
        for alert in alerts_created:
            trigger_camera_recording(zone, alert)
    
    return len(alerts_created)
