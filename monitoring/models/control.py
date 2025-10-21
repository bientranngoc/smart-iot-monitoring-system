"""
Smart Building control models - HVACControl and EnergyLog
"""

from django.db import models
from .building import Zone


class HVACControl(models.Model):
    """HVAC Control System"""
    MODE_CHOICES = [
        ('AUTO', 'Automatic'),
        ('MANUAL', 'Manual'),
        ('SCHEDULE', 'Scheduled'),
        ('OFF', 'Off'),
    ]
    
    zone = models.OneToOneField(Zone, on_delete=models.CASCADE, related_name='hvac')
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='AUTO')
    
    # Current settings
    current_temperature = models.FloatField(null=True, blank=True)
    set_temperature = models.FloatField(default=24.0)
    fan_speed = models.IntegerField(default=50, help_text="0-100%")
    
    # Status
    is_cooling = models.BooleanField(default=False)
    is_heating = models.BooleanField(default=False)
    power_consumption = models.FloatField(default=0.0, help_text="kW")
    
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"HVAC - {self.zone.name}"


class EnergyLog(models.Model):
    """Energy consumption log"""
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    hvac_consumption = models.FloatField(default=0.0, help_text="kWh")
    lighting_consumption = models.FloatField(default=0.0, help_text="kWh")
    total_consumption = models.FloatField(default=0.0, help_text="kWh")
    
    cost = models.FloatField(default=0.0, help_text="VND")
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.zone.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')} - {self.total_consumption} kWh"
