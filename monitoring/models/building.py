"""
Smart Building models - Building and Zone
"""

from django.db import models
from django.contrib.auth.models import User as AuthUser


class Building(models.Model):
    """Tòa nhà"""
    name = models.CharField(max_length=200)
    address = models.TextField()
    floors = models.IntegerField()
    total_area = models.FloatField(help_text="Diện tích (m2)")
    manager = models.ForeignKey(AuthUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def total_zones(self):
        return self.zones.count()
    
    @property
    def active_alerts(self):
        from .alert import BuildingAlert
        return BuildingAlert.objects.filter(
            zone__building=self,
            acknowledged=False
        ).count()


class Zone(models.Model):
    """Khu vực trong tòa nhà (Lobby, Office, Server Room, etc.)"""
    ZONE_TYPE_CHOICES = [
        ('LOBBY', 'Lobby'),
        ('OFFICE', 'Office'),
        ('MEETING', 'Meeting Room'),
        ('SERVER', 'Server Room'),
        ('PARKING', 'Parking Lot'),
        ('CORRIDOR', 'Corridor'),
        ('EMERGENCY', 'Emergency Exit'),
        ('OTHER', 'Other'),
    ]
    
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='zones')
    name = models.CharField(max_length=200)
    floor = models.IntegerField()
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPE_CHOICES)
    area = models.FloatField(help_text="Diện tích (m2)")
    
    # Target environmental parameters
    target_temperature = models.FloatField(default=24.0)
    temp_min = models.FloatField(default=22.0)
    temp_max = models.FloatField(default=26.0)
    target_humidity = models.FloatField(default=60.0)
    humidity_min = models.FloatField(default=40.0)
    humidity_max = models.FloatField(default=70.0)
    
    # Operating hours
    operating_start = models.TimeField(default='08:00:00')
    operating_end = models.TimeField(default='18:00:00')
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['floor', 'name']
    
    def __str__(self):
        return f"{self.building.name} - Floor {self.floor} - {self.name}"
    
    @property
    def current_status(self):
        """Kiểm tra trạng thái hiện tại"""
        sensors = self.sensors.all() 
        if not sensors.exists(): 
            return 'NO_DATA'
        
        for sensor in sensors: 
            if sensor.latest_reading is None: # No readings yet
                continue
                
            if sensor.sensor_type == 'TEMPERATURE': # Kiểm tra nhiệt độ
                if sensor.latest_reading < self.temp_min or sensor.latest_reading > self.temp_max:
                    return 'ALERT'
            elif sensor.sensor_type == 'HUMIDITY': # Kiểm tra độ ẩm
                if sensor.latest_reading < self.humidity_min or sensor.latest_reading > self.humidity_max:
                    return 'WARNING'
        
        return 'NORMAL'
