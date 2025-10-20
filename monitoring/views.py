"""
API Views for IoT Monitoring System

Provides REST API endpoints for:
- Users (MySQL)
- Devices (MySQL)
- Readings (MongoDB via pymongo)
- Latest Readings (Redis cache)
"""

import json
import redis
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime

from .models import User, Device, ReadingClient
from .serializers import (
    UserSerializer,
    DeviceSerializer,
    ReadingSerializer,
    LatestReadingSerializer
)

# Redis client
REDIS_HOST = 'iot-redis'
REDIS_PORT = 6379
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User management (MySQL)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    """ViewSet for Device management (MySQL)"""
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    
    @action(detail=True, methods=['get'])
    def readings(self, request, pk=None):
        """Get readings for a specific device from MongoDB"""
        device = self.get_object()
        limit = int(request.query_params.get('limit', 100))
        since_str = request.query_params.get('since')
        
        since = None
        if since_str:
            since = parse_datetime(since_str)
        
        client = ReadingClient()
        readings = client.find_readings(
            device_id=device.id,
            limit=limit,
            since=since
        )
        
        serializer = ReadingSerializer(readings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def latest(self, request, pk=None):
        """Get latest reading from Redis cache"""
        device = self.get_object()
        cache_key = f"latest:device{device.id}"
        
        cached_data = redis_client.get(cache_key)
        if cached_data:
            data = json.loads(cached_data)
            data['status'] = 'online'
            serializer = LatestReadingSerializer(data)
            return Response(serializer.data)
        else:
            return Response(
                {'detail': 'No recent data (device offline)'},
                status=status.HTTP_404_NOT_FOUND
            )


class ReadingViewSet(viewsets.ViewSet):
    """ViewSet for Reading operations (MongoDB via pymongo)"""
    
    def list(self, request):
        """Get recent readings from MongoDB"""
        device_id = request.query_params.get('device_id')
        limit = int(request.query_params.get('limit', 100))
        since_str = request.query_params.get('since')
        
        since = None
        if since_str:
            since = parse_datetime(since_str)
        
        client = ReadingClient()
        
        if device_id:
            readings = client.find_readings(
                device_id=int(device_id),
                limit=limit,
                since=since
            )
        else:
            # Get readings for all devices
            devices = Device.objects.all()
            readings = []
            per_device_limit = max(limit // devices.count(), 10) if devices.exists() else limit
            
            for device in devices:
                device_readings = client.find_readings(
                    device_id=device.id,
                    limit=per_device_limit,
                    since=since
                )
                readings.extend(device_readings)
            
            readings.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            readings = readings[:limit]
        
        serializer = ReadingSerializer(readings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest_all(self, request):
        """Get latest readings for all devices from Redis cache"""
        results = []
        
        for key in redis_client.scan_iter("latest:device*"):
            cached_data = redis_client.get(key)
            if cached_data:
                data = json.loads(cached_data)
                ttl = redis_client.ttl(key)
                data['status'] = 'online' if ttl > 0 else 'offline'
                results.append(data)
        
        results.sort(key=lambda x: x.get('device_id', 0))
        
        serializer = LatestReadingSerializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about readings"""
        client = ReadingClient()
        client._connect()
        
        total_count = client._collection.count_documents({})
        
        pipeline = [
            {"$group": {"_id": "$device_id", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        by_device = list(client._collection.aggregate(pipeline))
        
        active_devices = []
        for key in redis_client.scan_iter("latest:device*"):
            device_id = key.split('device')[1]
            active_devices.append(int(device_id))
        
        return Response({
            'total_readings': total_count,
            'readings_by_device': by_device,
            'active_devices': sorted(active_devices),
            'active_count': len(active_devices)
        })
    
    @action(detail=False, methods=['get'])
    def aggregations(self, request):
        """
        Get statistical aggregations using OpenSearch
        
        Query parameters:
        - device_id: Filter by specific device (optional)
        - range: Time range (1h, 24h, 7d)
        
        Returns temperature and humidity statistics (avg, min, max, count)
        
        Example:
        - /api/readings/aggregations/
        - /api/readings/aggregations/?device_id=1
        - /api/readings/aggregations/?range=24h
        """
        try:
            from opensearchpy import OpenSearch
            from datetime import datetime, timedelta
            
            os_client = OpenSearch(
                hosts=[{'host': 'opensearch', 'port': 9200}],
                use_ssl=False,
                verify_certs=False
            )
            
            # Build query filter
            query = {"bool": {"must": []}}
            
            # Device filter
            device_id = request.query_params.get('device_id')
            if device_id:
                query["bool"]["must"].append({
                    "term": {"device_id": int(device_id)}
                })
            
            # Time range filter
            range_param = request.query_params.get('range')
            if range_param:
                now = datetime.utcnow()
                if range_param == '1h':
                    since = now - timedelta(hours=1)
                elif range_param == '24h':
                    since = now - timedelta(hours=24)
                elif range_param == '7d':
                    since = now - timedelta(days=7)
                else:
                    since = None
                
                if since:
                    query["bool"]["must"].append({
                        "range": {"timestamp": {"gte": since.isoformat()}}
                    })
            
            # Build aggregations
            aggs = {
                "temperature_stats": {
                    "stats": {"field": "temperature"}
                },
                "humidity_stats": {
                    "stats": {"field": "humidity"}
                },
                "by_device": {
                    "terms": {
                        "field": "device_id",
                        "size": 100
                    },
                    "aggs": {
                        "temp_avg": {"avg": {"field": "temperature"}},
                        "humidity_avg": {"avg": {"field": "humidity"}}
                    }
                },
                "temperature_histogram": {
                    "histogram": {
                        "field": "temperature",
                        "interval": 5
                    }
                }
            }
            
            # Execute search with aggregations
            result = os_client.search(
                index='sensor-readings',
                body={
                    "query": query if query["bool"]["must"] else {"match_all": {}},
                    "size": 0,  # We only want aggregations, not documents
                    "aggs": aggs
                }
            )
            
            # Format response
            temp_stats = result['aggregations']['temperature_stats']
            humidity_stats = result['aggregations']['humidity_stats']
            by_device = result['aggregations']['by_device']['buckets']
            temp_histogram = result['aggregations']['temperature_histogram']['buckets']
            
            return Response({
                'total_documents': result['hits']['total']['value'],
                'temperature': {
                    'avg': round(temp_stats['avg'], 2) if temp_stats['count'] > 0 else None,
                    'min': temp_stats['min'] if temp_stats['count'] > 0 else None,
                    'max': temp_stats['max'] if temp_stats['count'] > 0 else None,
                    'count': temp_stats['count']
                },
                'humidity': {
                    'avg': round(humidity_stats['avg'], 2) if humidity_stats['count'] > 0 else None,
                    'min': humidity_stats['min'] if humidity_stats['count'] > 0 else None,
                    'max': humidity_stats['max'] if humidity_stats['count'] > 0 else None,
                    'count': humidity_stats['count']
                },
                'by_device': [
                    {
                        'device_id': bucket['key'],
                        'count': bucket['doc_count'],
                        'avg_temperature': round(bucket['temp_avg']['value'], 2) if bucket['temp_avg']['value'] else None,
                        'avg_humidity': round(bucket['humidity_avg']['value'], 2) if bucket['humidity_avg']['value'] else None
                    }
                    for bucket in by_device
                ],
                'temperature_distribution': [
                    {
                        'range': f"{bucket['key']}-{bucket['key']+5}°C",
                        'count': bucket['doc_count']
                    }
                    for bucket in temp_histogram if bucket['doc_count'] > 0
                ],
                'query_time_ms': result['took']
            })
            
        except Exception as e:
            return Response(
                {'error': f'OpenSearch error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search readings using OpenSearch
        
        Query parameters:
        - q: Search query (e.g., "temperature:>25" or "humidity:<60")
        - device_id: Filter by device ID
        - from_date: Start date (ISO format)
        - to_date: End date (ISO format)
        - limit: Max results (default 100)
        
        Examples:
        - /api/readings/search/?q=temperature:>25
        - /api/readings/search/?device_id=1&from_date=2025-10-20T00:00:00Z
        """
        try:
            from opensearchpy import OpenSearch
            from datetime import datetime, timedelta
            
            os_client = OpenSearch(
                hosts=[{'host': 'opensearch', 'port': 9200}],
                use_ssl=False,
                verify_certs=False
            )
            
            # Build query
            query = {"bool": {"must": []}}
            
            # Parse query parameter
            q = request.query_params.get('q', '')
            if q:
                if ':' in q:
                    field, value = q.split(':', 1)
                    if value.startswith('>'):
                        query["bool"]["must"].append({
                            "range": {field: {"gt": float(value[1:])}}
                        })
                    elif value.startswith('<'):
                        query["bool"]["must"].append({
                            "range": {field: {"lt": float(value[1:])}}
                        })
                    elif value.startswith('='):
                        query["bool"]["must"].append({
                            "term": {field: float(value[1:])}
                        })
                else:
                    # Full-text search
                    query["bool"]["must"].append({
                        "multi_match": {
                            "query": q,
                            "fields": ["temperature", "humidity"]
                        }
                    })
            
            # Device filter
            device_id = request.query_params.get('device_id')
            if device_id:
                query["bool"]["must"].append({
                    "term": {"device_id": int(device_id)}
                })
            
            # Date range filter
            from_date = request.query_params.get('from_date')
            to_date = request.query_params.get('to_date')
            if from_date or to_date:
                date_range = {}
                if from_date:
                    date_range['gte'] = from_date
                if to_date:
                    date_range['lte'] = to_date
                query["bool"]["must"].append({
                    "range": {"timestamp": date_range}
                })
            
            # Time range shortcuts
            range_param = request.query_params.get('range')
            if range_param:
                now = datetime.utcnow()
                if range_param == '1h':
                    since = now - timedelta(hours=1)
                elif range_param == '24h':
                    since = now - timedelta(hours=24)
                elif range_param == '7d':
                    since = now - timedelta(days=7)
                else:
                    since = None
                
                if since:
                    query["bool"]["must"].append({
                        "range": {"timestamp": {"gte": since.isoformat()}}
                    })
            
            limit = int(request.query_params.get('limit', 100))
            
            # Execute search
            result = os_client.search(
                index='sensor-readings',
                body={
                    "query": query if query["bool"]["must"] else {"match_all": {}},
                    "size": limit,
                    "sort": [{"timestamp": {"order": "desc"}}]
                }
            )
            
            # Format results
            readings = []
            for hit in result['hits']['hits']:
                readings.append(hit['_source'])
            
            return Response({
                'total': result['hits']['total']['value'],
                'results': readings,
                'took_ms': result['took']
            })
            
        except Exception as e:
            return Response(
                {'error': f'OpenSearch error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Legacy function-based view (for backward compatibility)
@api_view(['GET'])
def latest_reading(request, device_id):
    """Get latest reading for a device (legacy endpoint)"""
    cache_key = f"latest:device{device_id}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        data = json.loads(cached_data)
        serializer = ReadingSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Fallback to MongoDB
    try:
        client = ReadingClient()
        readings = client.find_readings(device_id=int(device_id), limit=1)
        
        if readings:
            serializer = ReadingSerializer(readings[0])
            # Update cache
            cache_value = json.dumps(serializer.data, default=str)
            redis_client.set(cache_key, cache_value, ex=60)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No data found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============ SMART BUILDING VIEWSETS ============

from .models import Building, Zone, BuildingAlert, HVACControl
from .serializers import (
    BuildingSerializer,
    ZoneDetailSerializer,
    BuildingAlertSerializer,
    HVACControlSerializer
)
from django.utils import timezone


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
        from .serializers import ZoneCameraSerializer
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


class BuildingAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for BuildingAlert management"""
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
        
        serializer = BuildingAlertSerializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        
        # Check if user is authenticated
        if request.user.is_authenticated:
            alert.acknowledged_by = request.user
        
        alert.acknowledged = True
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        return Response({
            'status': 'acknowledged',
            'alert_id': alert.id,
            'acknowledged_at': alert.acknowledged_at
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Alert statistics"""
        building_id = request.query_params.get('building')
        
        alerts = BuildingAlert.objects.all()
        if building_id:
            alerts = alerts.filter(zone__building_id=building_id)
        
        # Last 24 hours
        from datetime import timedelta
        last_24h = timezone.now() - timedelta(hours=24)
        
        stats = {
            'total': alerts.count(),
            'last_24h': alerts.filter(created_at__gte=last_24h).count(),
            'unacknowledged': alerts.filter(acknowledged=False).count(),
            'by_severity': {
                'EMERGENCY': alerts.filter(severity='EMERGENCY').count(),
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
    """ViewSet for HVAC Control management"""
    queryset = HVACControl.objects.all()
    serializer_class = HVACControlSerializer
    
    @action(detail=True, methods=['post'])
    def set_mode(self, request, pk=None):
        """Change HVAC mode"""
        hvac = self.get_object()
        mode = request.data.get('mode')
        
        if mode not in ['AUTO', 'MANUAL', 'SCHEDULE', 'OFF']:
            return Response(
                {'error': 'Invalid mode. Valid options: AUTO, MANUAL, SCHEDULE, OFF'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        hvac.mode = mode
        hvac.save()
        
        return Response({
            'status': 'success',
            'hvac_id': hvac.id,
            'zone': hvac.zone.name,
            'mode': hvac.mode,
            'message': f'HVAC mode changed to {mode}'
        })
    
    @action(detail=True, methods=['post'])
    def set_temperature(self, request, pk=None):
        """Set target temperature (MANUAL mode only)"""
        hvac = self.get_object()
        
        if hvac.mode != 'MANUAL':
            return Response(
                {'error': f'Can only set temperature in MANUAL mode (current: {hvac.mode})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        temperature = request.data.get('temperature')
        if not temperature:
            return Response(
                {'error': 'temperature parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            temp_value = float(temperature)
            if temp_value < 16 or temp_value > 32:
                return Response(
                    {'error': 'Temperature must be between 16°C and 32°C'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            hvac.set_temperature = temp_value
            hvac.save()
            
            return Response({
                'status': 'success',
                'hvac_id': hvac.id,
                'zone': hvac.zone.name,
                'set_temperature': hvac.set_temperature,
                'message': f'Target temperature set to {temp_value}°C'
            })
            
        except ValueError:
            return Response(
                {'error': 'Invalid temperature value'},
                status=status.HTTP_400_BAD_REQUEST
            )