from django.db import models
from django.conf import settings
from django.contrib.auth.models import User as AuthUser
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import datetime

from pymongo import MongoClient
from pymongo.errors import PyMongoError

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'  

class Device(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'devices'


# ============ SMART BUILDING MODELS ============

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
            if sensor.latest_reading is None:
                continue
                
            if sensor.sensor_type == 'TEMPERATURE':
                if sensor.latest_reading < self.temp_min or sensor.latest_reading > self.temp_max:
                    return 'ALERT'
            elif sensor.sensor_type == 'HUMIDITY':
                if sensor.latest_reading < self.humidity_min or sensor.latest_reading > self.humidity_max:
                    return 'WARNING'
        
        return 'NORMAL'


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


class BuildingAlert(models.Model):
    """Alerts cho Smart Building"""
    ALERT_TYPE_CHOICES = [
        ('TEMPERATURE', 'Temperature Alert'),
        ('HUMIDITY', 'Humidity Alert'),
        ('SECURITY', 'Security Alert'),
        ('ENERGY', 'Energy Alert'),
        ('HVAC', 'HVAC Malfunction'),
        ('DOOR', 'Door Alert'),
        ('MOTION', 'Motion Detected'),
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

@dataclass
class Reading:
    device_id: int
    temperature: float
    humidity: float
    timestamp: datetime.datetime

    def to_dict(self) -> Dict[str, Any]:
        # Let pymongo handle datetime objects directly
        return asdict(self)


class ReadingClient:
    def __init__(self, uri: Optional[str] = None, db_name: Optional[str] = None, collection_name: str = "readings"):
        self.uri = uri or getattr(settings, "MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = db_name or getattr(settings, "MONGODB_DB_NAME", "iot")
        self.collection_name = collection_name
        self._client: Optional[MongoClient] = None
        self._collection = None

    def _connect(self):
        if self._client is None:
            self._client = MongoClient(self.uri)
            self._collection = self._client[self.db_name][self.collection_name]
            # Create unique compound index to prevent duplicates
            try:
                self._collection.create_index(
                    [("device_id", 1), ("timestamp", 1)],
                    unique=True,
                    background=True
                )
            except Exception:
                pass  # Index already exists

    def insert_reading(self, reading: Reading) -> Optional[str]:
        try:
            self._connect()
            doc = reading.to_dict()
            res = self._collection.insert_one(doc)
            return str(res.inserted_id)
        except PyMongoError as e:
            import logging
            # DuplicateKeyError is expected for duplicate readings, just log debug
            if 'duplicate key error' in str(e).lower():
                logging.debug(f"Duplicate reading ignored: device_id={reading.device_id}, timestamp={reading.timestamp}")
                return None
            logging.error(f"PyMongoError in insert_reading: {e}")
            return None
        except Exception as e:
            import logging
            logging.error(f"Unexpected error in insert_reading: {e}")
            return None

    def find_readings(self, device_id: int, limit: int = 100, since: Optional[datetime.datetime] = None) -> List[Dict[str, Any]]:
        self._connect()
        query: Dict[str, Any] = {"device_id": device_id}
        if since is not None:
            query["timestamp"] = {"$gte": since}
        cursor = self._collection.find(query).sort("timestamp", -1).limit(limit)
        return list(cursor)