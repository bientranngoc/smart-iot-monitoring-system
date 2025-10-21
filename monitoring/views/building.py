"""
Smart Building views - Building and Zone ViewSets
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from monitoring.models import Building, Zone
from monitoring.serializers import (
    BuildingSerializer,
    ZoneDetailSerializer,
    ZoneCameraSerializer
)


class BuildingViewSet(viewsets.ModelViewSet):
    """ViewSet for Building management"""
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    
    @action(detail=True, methods=['get'])
    def overview(self, request, pk=None):
        """Get building overview with all zones status"""
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
                'zone_type_display': zone.get_zone_type_display(),
                'status': zone.current_status,
                'temperature': avg_temp,
                'humidity': avg_humid,
                'target_temperature': zone.target_temperature,
                'temp_range': [zone.temp_min, zone.temp_max],
                'cameras': [
                    {
                        'id': c.id,
                        'name': c.name,
                        'hls_url': c.hls_url,
                        'webrtc_url': c.webrtc_url
                    }
                    for c in zone.cameras.filter(is_active=True)
                ],
                'has_hvac': hasattr(zone, 'hvac')
            })
        
        return Response({
            'building': BuildingSerializer(building).data,
            'zones': zone_data,
            'total_zones': len(zone_data),
            'active_alerts': building.active_alerts
        })


class ZoneViewSet(viewsets.ModelViewSet):
    """ViewSet for Zone management"""
    queryset = Zone.objects.all()
    serializer_class = ZoneDetailSerializer
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get real-time zone status with sensors and HVAC"""
        zone = self.get_object()
        
        sensors_data = []
        for sensor in zone.sensors.filter(is_active=True):
            unit = ''
            if sensor.sensor_type == 'TEMPERATURE':
                unit = '°C'
            elif sensor.sensor_type == 'HUMIDITY':
                unit = '%'
            elif sensor.sensor_type == 'CO2':
                unit = 'ppm'
            elif sensor.sensor_type == 'LIGHT':
                unit = 'lux'
            
            sensors_data.append({
                'id': sensor.id,
                'type': sensor.sensor_type,
                'type_display': sensor.get_sensor_type_display(),
                'location': sensor.location_description,
                'value': sensor.latest_reading,
                'timestamp': sensor.latest_reading_time,
                'unit': unit,
                'device_id': sensor.device.id
            })
        
        # HVAC status
        hvac_data = None
        if hasattr(zone, 'hvac'):
            hvac = zone.hvac
            hvac_data = {
                'id': hvac.id,
                'mode': hvac.mode,
                'mode_display': hvac.get_mode_display(),
                'current_temp': hvac.current_temperature,
                'set_temp': hvac.set_temperature,
                'is_cooling': hvac.is_cooling,
                'is_heating': hvac.is_heating,
                'fan_speed': hvac.fan_speed,
                'status': 'Cooling' if hvac.is_cooling else 'Heating' if hvac.is_heating else 'Standby',
                'last_updated': hvac.last_updated
            }
        
        # Camera data
        cameras_data = ZoneCameraSerializer(zone.cameras.filter(is_active=True), many=True).data
        
        return Response({
            'zone': {
                'id': zone.id,
                'name': zone.name,
                'floor': zone.floor,
                'zone_type': zone.zone_type,
                'zone_type_display': zone.get_zone_type_display(),
                'status': zone.current_status,
                'target_temperature': zone.target_temperature,
                'temp_range': [zone.temp_min, zone.temp_max]
            },
            'sensors': sensors_data,
            'hvac': hvac_data,
            'cameras': cameras_data
        })
    
    @action(detail=False, methods=['get'])
    def by_floor(self, request):
        """Get zones grouped by floor"""
        building_id = request.query_params.get('building')
        if not building_id:
            return Response(
                {'error': 'building parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
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
                'zone_type_display': zone.get_zone_type_display(),
                'status': zone.current_status,
                'sensor_count': zone.sensors.filter(is_active=True).count(),
                'camera_count': zone.cameras.filter(is_active=True).count(),
                'has_hvac': hasattr(zone, 'hvac')
            })
        
        return Response(floors_data)
