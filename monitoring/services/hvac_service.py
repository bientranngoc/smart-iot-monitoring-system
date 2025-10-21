"""
HVAC service - Automatic HVAC control logic
"""

import logging
from monitoring.models import HVACControl, Zone

logger = logging.getLogger(__name__)


def auto_control_hvac(zone: Zone) -> bool:
    """
    Automatic HVAC control based on temperature
    
    Args:
        zone: The Zone instance to control HVAC for
        
    Returns:
        True if HVAC was controlled, False otherwise
    """
    try:
        hvac = zone.hvac
        if hvac.mode != 'AUTO':
            logger.debug("HVAC in %s not in AUTO mode (current: %s), skipping control", 
                         zone.name, hvac.mode)
            return False
        
        # Get current temperature from sensors
        temp_sensors = zone.sensors.filter(sensor_type='TEMPERATURE', is_active=True)
        if not temp_sensors.exists():
            logger.debug("No temperature sensors found for %s", zone.name)
            return False
        
        temps = [s.latest_reading for s in temp_sensors if s.latest_reading is not None]
        if not temps:
            logger.debug("No temperature readings available for %s", zone.name)
            return False
        
        current_temp = sum(temps) / len(temps)
        hvac.current_temperature = current_temp
        
        # Control logic
        target = zone.target_temperature
        previous_cooling = hvac.is_cooling
        previous_heating = hvac.is_heating
        
        if current_temp > target + 1:
            # Too hot - turn on cooling
            hvac.is_cooling = True
            hvac.is_heating = False
            hvac.set_temperature = target
            hvac.fan_speed = min(100, int((current_temp - target) * 20))
            if not previous_cooling:
                logger.info("HVAC %s: Cooling ON (Current: %.1f°C, Target: %.1f°C, Fan: %d%%)", 
                           zone.name, current_temp, target, hvac.fan_speed)
            
        elif current_temp < target - 1:
            # Too cold - turn on heating
            hvac.is_cooling = False
            hvac.is_heating = True
            hvac.set_temperature = target
            hvac.fan_speed = min(100, int((target - current_temp) * 20))
            if not previous_heating:
                logger.info("HVAC %s: Heating ON (Current: %.1f°C, Target: %.1f°C, Fan: %d%%)", 
                           zone.name, current_temp, target, hvac.fan_speed)
            
        else:
            # Temperature OK - standby
            if previous_cooling or previous_heating:
                logger.info("✓ HVAC %s: Standby (Current: %.1f°C, Target: %.1f°C)", 
                           zone.name, current_temp, target)
            hvac.is_cooling = False
            hvac.is_heating = False
            hvac.fan_speed = 30  # Low fan speed for circulation
        
        hvac.save()
        return True
        
    except HVACControl.DoesNotExist:
        logger.debug("No HVAC system found for zone: %s", zone.name)
        return False
    except Exception as e:
        logger.error("HVAC control error in %s: %s", zone.name, e)
        return False
