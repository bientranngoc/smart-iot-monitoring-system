"""
Smart Building alert model - BuildingAlert
"""

from django.db import models
from django.contrib.auth.models import User as AuthUser
from .building import Zone
from .sensor import ZoneCamera


class BuildingAlert(models.Model):
    """Alerts cho Smart Building"""
    ALERT_TYPE_CHOICES = [
        ('TEMPERATURE', 'Temperature Alert'), # Cảnh báo nhiệt độ
        ('HUMIDITY', 'Humidity Alert'), # Cảnh báo độ ẩm
        ('SECURITY', 'Security Alert'), # Cảnh báo an ninh
        ('ENERGY', 'Energy Alert'), # Cảnh báo năng lượng
        ('HVAC', 'HVAC Malfunction'), # Cảnh báo hệ thống HVAC
        ('DOOR', 'Door Alert'), # Cảnh báo cửa
        ('MOTION', 'Motion Detected'), # Cảnh báo chuyển động
    ]
    
    SEVERITY_CHOICES = [
        ('INFO', 'Information'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
        ('EMERGENCY', 'Emergency'),
    ]
    
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    sensor_value = models.FloatField(null=True, blank=True)
    sensor_type = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(AuthUser, on_delete=models.SET_NULL, null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    # Camera recording
    camera = models.ForeignKey(ZoneCamera, on_delete=models.SET_NULL, null=True, blank=True)
    video_recording_path = models.CharField(max_length=500, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"[{self.severity}] {self.title}"
