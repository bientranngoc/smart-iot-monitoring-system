"""
Smart Building sensor models - ZoneSensor and ZoneCamera
"""

from django.db import models
from .building import Zone
from .base import Device


class ZoneSensor(models.Model):
    """Sensors trong mỗi zone"""
    SENSOR_TYPE_CHOICES = [
        ('TEMPERATURE', 'Temperature'),
        ('HUMIDITY', 'Humidity'),
        ('CO2', 'CO2 Level'),
        ('LIGHT', 'Light Level'),
        ('MOTION', 'Motion Detector'),
        ('DOOR', 'Door Sensor'),
    ]
    
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='sensors')
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPE_CHOICES)
    location_description = models.CharField(max_length=200)
    
    latest_reading = models.FloatField(null=True, blank=True)
    latest_reading_time = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['zone', 'device']
    
    def __str__(self):
        return f"{self.zone.name} - {self.sensor_type} ({self.device.id})"


class ZoneCamera(models.Model):
    """Camera cho mỗi zone"""
    CAMERA_TYPE_CHOICES = [
        ('SECURITY', 'Security Camera'),
        ('MONITORING', 'Environment Monitoring'),
        ('ENTRANCE', 'Entrance Camera'),
        ('PARKING', 'Parking Camera'),
    ]
    
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='cameras')
    name = models.CharField(max_length=200)
    camera_type = models.CharField(max_length=20, choices=CAMERA_TYPE_CHOICES)
    
    # Camera connection
    rtsp_url = models.CharField(max_length=500)
    mediamtx_path = models.CharField(max_length=100, unique=True)
    
    # Recording settings
    recording_enabled = models.BooleanField(default=True)
    retention_days = models.IntegerField(default=30)
    
    # Position
    position_description = models.CharField(max_length=200)
    
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.zone.name} - {self.name}"
    
    @property
    def hls_url(self):
        return f"http://localhost:8889/{self.mediamtx_path}/index.m3u8"
    
    @property
    def webrtc_url(self):
        return f"http://localhost:8889/{self.mediamtx_path}"
