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