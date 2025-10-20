# 🏢 Smart Building Implementation Guide

## 📋 Tổng quan dự án

Triển khai hệ thống **Smart Building / Tòa nhà thông minh** với các tính năng:
- 🌡️ HVAC Control (Điều hòa tự động)
- 💧 Air Quality Monitoring
- 📹 Security Cameras
- 💡 Smart Lighting
- ⚡ Energy Management

---

## 🎯 Phase 1: Chuẩn bị Database Models

### Step 1.1: Tạo Models cho Smart Building

```python
# monitoring/models.py - THÊM VÀO FILE HIỆN TẠI

from django.db import models
from django.contrib.auth.models import User

class Building(models.Model):
    """Tòa nhà"""
    name = models.CharField(max_length=200)
    address = models.TextField()
    floors = models.IntegerField()
    total_area = models.FloatField(help_text="Diện tích (m2)")
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
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
    device = models.ForeignKey('Device', on_delete=models.CASCADE)
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPE_CHOICES)
    location_description = models.CharField(max_length=200)
    
    latest_reading = models.FloatField(null=True, blank=True)
    latest_reading_time = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['zone', 'device']
    
    def __str__(self):
        return f"{self.zone.name} - {self.sensor_type} ({self.device.device_id})"


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
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
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
```

### Step 1.2: Tạo Migration

```bash
# Trong terminal PowerShell
docker exec -it iot-app python manage.py makemigrations
docker exec -it iot-app python manage.py migrate
```

---

## 🎯 Phase 2: Cập nhật Business Logic

### Step 2.1: Update Celery Tasks

```python
# monitoring/tasks.py - CẬP NHẬT FUNCTION handle_payload

from .models import ZoneSensor, BuildingAlert, HVACControl
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone

@shared_task
def handle_payload(message):
    """Process MQTT message with Smart Building logic"""
    try:
        data = json.loads(message.value.decode("utf-8"))
        logger.info(f"Processing: {data}")
        
        device_id = data.get("device_id")
        temperature = data.get("temperature")
        humidity = data.get("humidity")
        timestamp_str = data.get("timestamp")
        
        # ... existing code for MySQL, MongoDB, Redis, OpenSearch ...
        
        # ============ SMART BUILDING LOGIC ============
        try:
            zone_sensor = ZoneSensor.objects.filter(
                device__device_id=device_id,
                is_active=True
            ).select_related('zone').first()
            
            if zone_sensor:
                # Update sensor reading
                if zone_sensor.sensor_type == 'TEMPERATURE':
                    zone_sensor.latest_reading = temperature
                elif zone_sensor.sensor_type == 'HUMIDITY':
                    zone_sensor.latest_reading = humidity
                
                zone_sensor.latest_reading_time = datetime.fromisoformat(timestamp_str)
                zone_sensor.save()
                
                # Check thresholds and create alerts
                check_building_thresholds(zone_sensor, temperature, humidity)
                
                # Auto-control HVAC
                auto_control_hvac(zone_sensor.zone)
                
        except Exception as e:
            logger.warning(f"Smart Building processing failed: {e}")
        
        return "OK"
        
    except Exception as e:
        logger.error(f"Error in handle_payload: {e}")
        return "ERROR"


def check_building_thresholds(zone_sensor, temperature, humidity):
    """Check if values exceed thresholds"""
    zone = zone_sensor.zone
    alerts_created = []
    
    # Check temperature
    if zone_sensor.sensor_type == 'TEMPERATURE':
        if temperature < zone.temp_min:
            alert = BuildingAlert.objects.create(
                zone=zone,
                alert_type='TEMPERATURE',
                severity='WARNING',
                title=f'🥶 Temperature Too Low',
                message=f'{zone.name}: {temperature}°C (Min: {zone.temp_min}°C)',
                sensor_value=temperature,
                sensor_type='TEMPERATURE'
            )
            alerts_created.append(alert)
            
        elif temperature > zone.temp_max:
            severity = 'CRITICAL' if temperature > zone.temp_max + 3 else 'WARNING'
            alert = BuildingAlert.objects.create(
                zone=zone,
                alert_type='TEMPERATURE',
                severity=severity,
                title=f'🔥 Temperature Too High',
                message=f'{zone.name}: {temperature}°C (Max: {zone.temp_max}°C)',
                sensor_value=temperature,
                sensor_type='TEMPERATURE'
            )
            alerts_created.append(alert)
    
    # Check humidity
    if zone_sensor.sensor_type == 'HUMIDITY':
        if humidity < zone.humidity_min or humidity > zone.humidity_max:
            alert = BuildingAlert.objects.create(
                zone=zone,
                alert_type='HUMIDITY',
                severity='WARNING',
                title=f'💧 Humidity Out of Range',
                message=f'{zone.name}: {humidity}% (Range: {zone.humidity_min}-{zone.humidity_max}%)',
                sensor_value=humidity,
                sensor_type='HUMIDITY'
            )
            alerts_created.append(alert)
    
    # Send WebSocket notifications
    for alert in alerts_created:
        send_building_alert(alert)
        
        # Start camera recording if available
        if zone.cameras.exists():
            camera = zone.cameras.first()
            trigger_camera_recording(camera, alert)


def auto_control_hvac(zone):
    """Automatic HVAC control based on temperature"""
    try:
        hvac = zone.hvac
        if hvac.mode != 'AUTO':
            return  # Only work in AUTO mode
        
        # Get current temperature
        temp_sensors = zone.sensors.filter(sensor_type='TEMPERATURE', is_active=True)
        if not temp_sensors.exists():
            return
        
        temps = [s.latest_reading for s in temp_sensors if s.latest_reading is not None]
        if not temps:
            return
        
        current_temp = sum(temps) / len(temps)
        hvac.current_temperature = current_temp
        
        # Control logic
        target = zone.target_temperature
        
        if current_temp > target + 1:
            # Too hot - turn on cooling
            hvac.is_cooling = True
            hvac.is_heating = False
            hvac.set_temperature = target
            hvac.fan_speed = min(100, int((current_temp - target) * 20))
            logger.info(f"HVAC {zone.name}: Cooling ON (Current: {current_temp}°C, Target: {target}°C)")
            
        elif current_temp < target - 1:
            # Too cold - turn on heating
            hvac.is_cooling = False
            hvac.is_heating = True
            hvac.set_temperature = target
            hvac.fan_speed = min(100, int((target - current_temp) * 20))
            logger.info(f"HVAC {zone.name}: Heating ON (Current: {current_temp}°C, Target: {target}°C)")
            
        else:
            # Temperature OK - standby
            hvac.is_cooling = False
            hvac.is_heating = False
            hvac.fan_speed = 30  # Low fan speed
            logger.info(f"HVAC {zone.name}: Standby (Current: {current_temp}°C)")
        
        hvac.save()
        
        # Send WebSocket update
        send_hvac_update(hvac)
        
    except HVACControl.DoesNotExist:
        logger.warning(f"No HVAC system found for zone: {zone.name}")
    except Exception as e:
        logger.error(f"HVAC control error: {e}")


def send_building_alert(alert):
    """Send alert via WebSocket"""
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        "building_alerts",
        {
            "type": "alert_message",
            "message": {
                "id": alert.id,
                "zone_id": alert.zone.id,
                "zone_name": alert.zone.name,
                "floor": alert.zone.floor,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "title": alert.title,
                "message": alert.message,
                "sensor_value": alert.sensor_value,
                "timestamp": alert.created_at.isoformat(),
            }
        }
    )


def send_hvac_update(hvac):
    """Send HVAC status update via WebSocket"""
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        "hvac_updates",
        {
            "type": "hvac_message",
            "message": {
                "zone_id": hvac.zone.id,
                "zone_name": hvac.zone.name,
                "current_temperature": hvac.current_temperature,
                "set_temperature": hvac.set_temperature,
                "is_cooling": hvac.is_cooling,
                "is_heating": hvac.is_heating,
                "fan_speed": hvac.fan_speed,
                "mode": hvac.mode,
                "timestamp": timezone.now().isoformat(),
            }
        }
    )


def trigger_camera_recording(camera, alert):
    """Trigger camera recording for alert"""
    try:
        recording_path = f"/recordings/{camera.mediamtx_path}/{alert.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        
        alert.camera = camera
        alert.video_recording_path = recording_path
        alert.save()
        
        logger.info(f"Camera recording triggered: {camera.name} -> {recording_path}")
        
    except Exception as e:
        logger.error(f"Failed to trigger camera recording: {e}")
```

---

## 🎯 Phase 3: REST API Endpoints

### Step 3.1: Serializers

```python
# monitoring/serializers.py - THÊM VÀO

from rest_framework import serializers
from .models import Building, Zone, ZoneSensor, ZoneCamera, HVACControl, BuildingAlert

class BuildingSerializer(serializers.ModelSerializer):
    total_zones = serializers.IntegerField(read_only=True)
    active_alerts = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Building
        fields = '__all__'


class ZoneSensorSerializer(serializers.ModelSerializer):
    sensor_type_display = serializers.CharField(source='get_sensor_type_display', read_only=True)
    
    class Meta:
        model = ZoneSensor
        fields = '__all__'


class ZoneCameraSerializer(serializers.ModelSerializer):
    hls_url = serializers.CharField(read_only=True)
    webrtc_url = serializers.CharField(read_only=True)
    camera_type_display = serializers.CharField(source='get_camera_type_display', read_only=True)
    
    class Meta:
        model = ZoneCamera
        fields = '__all__'


class HVACControlSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    mode_display = serializers.CharField(source='get_mode_display', read_only=True)
    
    class Meta:
        model = HVACControl
        fields = '__all__'


class ZoneDetailSerializer(serializers.ModelSerializer):
    sensors = ZoneSensorSerializer(many=True, read_only=True)
    cameras = ZoneCameraSerializer(many=True, read_only=True)
    hvac = HVACControlSerializer(read_only=True)
    current_status = serializers.CharField(read_only=True)
    zone_type_display = serializers.CharField(source='get_zone_type_display', read_only=True)
    
    class Meta:
        model = Zone
        fields = '__all__'


class BuildingAlertSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    floor = serializers.IntegerField(source='zone.floor', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = BuildingAlert
        fields = '__all__'
```

### Step 3.2: ViewSets

```python
# monitoring/views.py - THÊM VÀO

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Building, Zone, BuildingAlert, HVACControl
from .serializers import (
    BuildingSerializer, ZoneDetailSerializer, 
    BuildingAlertSerializer, HVACControlSerializer
)

class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    
    @action(detail=True, methods=['get'])
    def overview(self, request, pk=None):
        """Get building overview with all zones"""
        building = self.get_object()
        zones = building.zones.all()
        
        zone_data = []
        for zone in zones:
            # Get average temperature
            temp_sensors = zone.sensors.filter(sensor_type='TEMPERATURE', is_active=True)
            temps = [s.latest_reading for s in temp_sensors if s.latest_reading is not None]
            avg_temp = round(sum(temps) / len(temps), 1) if temps else None
            
            # Get average humidity
            humid_sensors = zone.sensors.filter(sensor_type='HUMIDITY', is_active=True)
            humids = [s.latest_reading for s in humid_sensors if s.latest_reading is not None]
            avg_humid = round(sum(humids) / len(humids), 1) if humids else None
            
            zone_data.append({
                'id': zone.id,
                'name': zone.name,
                'floor': zone.floor,
                'zone_type': zone.zone_type,
                'status': zone.current_status,
                'temperature': avg_temp,
                'humidity': avg_humid,
                'cameras': [{'id': c.id, 'name': c.name, 'hls_url': c.hls_url} for c in zone.cameras.filter(is_active=True)],
                'has_hvac': hasattr(zone, 'hvac')
            })
        
        return Response({
            'building': BuildingSerializer(building).data,
            'zones': zone_data,
            'total_zones': len(zone_data),
            'active_alerts': building.active_alerts
        })


class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneDetailSerializer
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get real-time zone status"""
        zone = self.get_object()
        
        sensors_data = []
        for sensor in zone.sensors.filter(is_active=True):
            sensors_data.append({
                'id': sensor.id,
                'type': sensor.sensor_type,
                'location': sensor.location_description,
                'value': sensor.latest_reading,
                'timestamp': sensor.latest_reading_time,
                'unit': '°C' if sensor.sensor_type == 'TEMPERATURE' else '%' if sensor.sensor_type == 'HUMIDITY' else ''
            })
        
        # HVAC status
        hvac_data = None
        if hasattr(zone, 'hvac'):
            hvac = zone.hvac
            hvac_data = {
                'mode': hvac.mode,
                'current_temp': hvac.current_temperature,
                'set_temp': hvac.set_temperature,
                'is_cooling': hvac.is_cooling,
                'is_heating': hvac.is_heating,
                'fan_speed': hvac.fan_speed
            }
        
        return Response({
            'zone': {
                'id': zone.id,
                'name': zone.name,
                'floor': zone.floor,
                'status': zone.current_status
            },
            'sensors': sensors_data,
            'hvac': hvac_data,
            'cameras': ZoneCameraSerializer(zone.cameras.filter(is_active=True), many=True).data
        })
    
    @action(detail=False, methods=['get'])
    def by_floor(self, request):
        """Get zones grouped by floor"""
        building_id = request.query_params.get('building')
        if not building_id:
            return Response({'error': 'building parameter required'}, status=400)
        
        zones = Zone.objects.filter(building_id=building_id).order_by('floor', 'name')
        
        # Group by floor
        floors_data = {}
        for zone in zones:
            floor = zone.floor
            if floor not in floors_data:
                floors_data[floor] = []
            
            floors_data[floor].append({
                'id': zone.id,
                'name': zone.name,
                'zone_type': zone.zone_type,
                'status': zone.current_status,
                'sensor_count': zone.sensors.filter(is_active=True).count(),
                'camera_count': zone.cameras.filter(is_active=True).count()
            })
        
        return Response(floors_data)


class BuildingAlertViewSet(viewsets.ModelViewSet):
    queryset = BuildingAlert.objects.all()
    serializer_class = BuildingAlertSerializer
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active (unacknowledged) alerts"""
        building_id = request.query_params.get('building')
        
        alerts = BuildingAlert.objects.filter(acknowledged=False)
        if building_id:
            alerts = alerts.filter(zone__building_id=building_id)
        
        alerts = alerts.select_related('zone', 'camera').order_by('-created_at')
        
        return Response(BuildingAlertSerializer(alerts, many=True).data)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        alert.acknowledged = True
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        return Response({'status': 'acknowledged'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Alert statistics"""
        building_id = request.query_params.get('building')
        
        alerts = BuildingAlert.objects.all()
        if building_id:
            alerts = alerts.filter(zone__building_id=building_id)
        
        # Last 24 hours
        from django.utils import timezone
        from datetime import timedelta
        last_24h = timezone.now() - timedelta(hours=24)
        
        stats = {
            'total': alerts.count(),
            'last_24h': alerts.filter(created_at__gte=last_24h).count(),
            'unacknowledged': alerts.filter(acknowledged=False).count(),
            'by_severity': {
                'CRITICAL': alerts.filter(severity='CRITICAL').count(),
                'WARNING': alerts.filter(severity='WARNING').count(),
                'INFO': alerts.filter(severity='INFO').count(),
            },
            'by_type': {}
        }
        
        # Count by alert type
        for alert_type, _ in BuildingAlert.ALERT_TYPE_CHOICES:
            stats['by_type'][alert_type] = alerts.filter(alert_type=alert_type).count()
        
        return Response(stats)


class HVACControlViewSet(viewsets.ModelViewSet):
    queryset = HVACControl.objects.all()
    serializer_class = HVACControlSerializer
    
    @action(detail=True, methods=['post'])
    def set_mode(self, request, pk=None):
        """Change HVAC mode"""
        hvac = self.get_object()
        mode = request.data.get('mode')
        
        if mode not in ['AUTO', 'MANUAL', 'SCHEDULE', 'OFF']:
            return Response({'error': 'Invalid mode'}, status=400)
        
        hvac.mode = mode
        hvac.save()
        
        return Response(HVACControlSerializer(hvac).data)
    
    @action(detail=True, methods=['post'])
    def set_temperature(self, request, pk=None):
        """Set target temperature (MANUAL mode only)"""
        hvac = self.get_object()
        
        if hvac.mode != 'MANUAL':
            return Response({'error': 'Can only set temperature in MANUAL mode'}, status=400)
        
        temperature = request.data.get('temperature')
        if not temperature:
            return Response({'error': 'temperature required'}, status=400)
        
        hvac.set_temperature = float(temperature)
        hvac.save()
        
        return Response(HVACControlSerializer(hvac).data)
```

### Step 3.3: URLs

```python
# monitoring/urls.py (hoặc smart_iot/urls.py)

from rest_framework.routers import DefaultRouter
from monitoring.views import (
    BuildingViewSet, ZoneViewSet, 
    BuildingAlertViewSet, HVACControlViewSet
)

router = DefaultRouter()
# ... existing routes ...
router.register(r'buildings', BuildingViewSet)
router.register(r'zones', ZoneViewSet)
router.register(r'building-alerts', BuildingAlertViewSet)
router.register(r'hvac-controls', HVACControlViewSet)

urlpatterns = [
    # ... existing patterns ...
] + router.urls
```

---

## 🎯 Phase 4: Tạo Sample Data

```python
# scripts/create_smart_building_data.py

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_iot.settings')
django.setup()

from monitoring.models import (
    Building, Zone, ZoneSensor, ZoneCamera, 
    HVACControl, Device, User
)

def create_sample_building():
    """Tạo sample data cho Smart Building"""
    
    # Get or create manager
    manager = User.objects.filter(username='admin').first()
    
    # Create building
    building = Building.objects.create(
        name='ABC Office Tower',
        address='123 Nguyen Hue, Q1, TPHCM',
        floors=10,
        total_area=5000.0,
        manager=manager
    )
    print(f"✅ Created building: {building.name}")
    
    # Create zones for Floor 1
    lobby = Zone.objects.create(
        building=building,
        name='Main Lobby',
        floor=1,
        zone_type='LOBBY',
        area=200.0,
        target_temperature=24.0,
        temp_min=22.0,
        temp_max=26.0
    )
    
    server_room = Zone.objects.create(
        building=building,
        name='Server Room',
        floor=1,
        zone_type='SERVER',
        area=50.0,
        target_temperature=20.0,
        temp_min=18.0,
        temp_max=22.0
    )
    
    parking = Zone.objects.create(
        building=building,
        name='Parking Lot',
        floor=0,
        zone_type='PARKING',
        area=500.0,
        target_temperature=30.0,
        temp_min=25.0,
        temp_max=35.0
    )
    
    print(f"✅ Created {Zone.objects.count()} zones")
    
    # Create sensors
    device1 = Device.objects.get(device_id=101)
    device2 = Device.objects.get(device_id=102)
    device3 = Device.objects.get(device_id=103)
    
    ZoneSensor.objects.create(
        zone=lobby,
        device=device1,
        sensor_type='TEMPERATURE',
        location_description='Lobby Center'
    )
    
    ZoneSensor.objects.create(
        zone=server_room,
        device=device2,
        sensor_type='TEMPERATURE',
        location_description='Server Rack Area'
    )
    
    ZoneSensor.objects.create(
        zone=parking,
        device=device3,
        sensor_type='TEMPERATURE',
        location_description='Parking Entrance'
    )
    
    print(f"✅ Created {ZoneSensor.objects.count()} sensors")
    
    # Create cameras
    ZoneCamera.objects.create(
        zone=lobby,
        name='Lobby Main Camera',
        camera_type='ENTRANCE',
        rtsp_url='rtsp://admin:password@192.168.1.101:554/stream1',
        mediamtx_path='lobby_main',
        position_description='Above main entrance'
    )
    
    ZoneCamera.objects.create(
        zone=server_room,
        name='Server Room Camera',
        camera_type='SECURITY',
        rtsp_url='rtsp://admin:password@192.168.1.102:554/stream1',
        mediamtx_path='server_room',
        position_description='Corner view of server racks'
    )
    
    ZoneCamera.objects.create(
        zone=parking,
        name='Parking Lot Camera',
        camera_type='PARKING',
        rtsp_url='rtsp://admin:password@192.168.1.103:554/stream1',
        mediamtx_path='parking_lot',
        position_description='Entrance gate'
    )
    
    print(f"✅ Created {ZoneCamera.objects.count()} cameras")
    
    # Create HVAC controls
    HVACControl.objects.create(
        zone=lobby,
        mode='AUTO',
        set_temperature=24.0
    )
    
    HVACControl.objects.create(
        zone=server_room,
        mode='AUTO',
        set_temperature=20.0
    )
    
    print(f"✅ Created {HVACControl.objects.count()} HVAC systems")
    
    print("\n🎉 Smart Building sample data created successfully!")
    print(f"Building: {building.name}")
    print(f"Zones: {building.total_zones}")
    print("Ready to test!")

if __name__ == '__main__':
    create_sample_building()
```

Chạy script:
```bash
docker exec -it iot-app python scripts/create_smart_building_data.py
```

---

## 🎯 Phase 5: React Frontend Components

Tôi sẽ tạo riêng file cho từng component Smart Building...

**Tiếp theo tôi sẽ tạo:**
1. SmartBuildingDashboard.jsx
2. BuildingOverview.jsx
3. ZoneCard.jsx
4. HVACControl.jsx
5. BuildingAlerts.jsx

Bạn có muốn tôi tiếp tục tạo frontend components không? 🚀
