# Migration from djongo to pymongo - Summary

## Overview
Successfully migrated the IoT Monitoring System from using djongo (Django-MongoDB ORM) to native pymongo with Django REST Framework ViewSets.

## Files Changed

### 1. `monitoring/models.py`
**Before**: Used djongo models (`models.Model` with MongoDB)
```python
class Reading(models.Model):
    device_id = models.IntegerField()
    temperature = models.FloatField()
    # ... used djongo ORM
```

**After**: Pure Django ORM for MySQL + pymongo client for MongoDB
```python
# MySQL models (unchanged)
class User(models.Model): ...
class Device(models.Model): ...

# MongoDB dataclass and client
@dataclass
class Reading:
    device_id: int
    temperature: float
    humidity: float
    timestamp: datetime

class ReadingClient:
    """Direct pymongo client for MongoDB operations"""
    def _connect(self): ...
    def insert_reading(self): ...
    def find_readings(self): ...
```

**Key features**:
- Unique compound index: `(device_id, timestamp)`
- Automatic duplicate prevention
- Direct pymongo queries (no ORM overhead)

---

### 2. `monitoring/views.py`
**Before**: Simple function-based view with djongo ORM
```python
@api_view(['GET'])
def latest_reading(request, device_id):
    reading = Reading.objects.using('mongodb').filter(...)
```

**After**: DRF ViewSets with pymongo ReadingClient
```python
class UserViewSet(viewsets.ModelViewSet):
    """CRUD operations for Users (MySQL)"""
    
class DeviceViewSet(viewsets.ModelViewSet):
    """CRUD operations for Devices (MySQL)"""
    
    @action(detail=True)
    def readings(self, request, pk=None):
        """Get readings from MongoDB via pymongo"""
        client = ReadingClient()
        readings = client.find_readings(...)
    
    @action(detail=True)
    def latest(self, request, pk=None):
        """Get latest from Redis cache"""

class ReadingViewSet(viewsets.ViewSet):
    """MongoDB operations via pymongo"""
    
    def list(self, request):
        """List readings with filters"""
    
    @action(detail=False)
    def latest_all(self, request):
        """Get all latest readings from Redis"""
    
    @action(detail=False)
    def stats(self, request):
        """Get MongoDB statistics"""
```

**Key features**:
- RESTful API endpoints
- MySQL queries via Django ORM
- MongoDB queries via pymongo ReadingClient
- Redis cache queries for performance

---

### 3. `monitoring/serializers.py`
**Before**: Simple serializer
```python
class ReadingSerializer(serializers.Serializer):
    device_id = serializers.IntegerField()
    ...
```

**After**: Comprehensive serializers for all models
```python
class UserSerializer(serializers.ModelSerializer):
    """Serializer for MySQL User model"""
    class Meta:
        model = User
        fields = '__all__'

class DeviceSerializer(serializers.ModelSerializer):
    """Serializer for MySQL Device model"""
    class Meta:
        model = Device
        fields = '__all__'

class ReadingSerializer(serializers.Serializer):
    """Serializer for MongoDB Reading dataclass"""
    device_id = serializers.IntegerField()
    temperature = serializers.FloatField()
    humidity = serializers.FloatField()
    timestamp = serializers.DateTimeField()

class LatestReadingSerializer(serializers.Serializer):
    """Serializer for Redis cached data with status"""
    device_id = serializers.IntegerField()
    temperature = serializers.FloatField()
    humidity = serializers.FloatField()
    timestamp = serializers.DateTimeField()
    status = serializers.CharField(required=False)
```

---

### 4. `monitoring/urls.py` (NEW)
Created URL configuration for the monitoring app with DRF router:
```python
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'readings', ReadingViewSet, basename='reading')
```

---

### 5. `smart_iot/urls.py`
**Before**: Direct view import
```python
from monitoring.views import latest_reading
urlpatterns = [
    path('api/latest/<int:device_id>/', latest_reading),
]
```

**After**: Include monitoring app URLs
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('monitoring.urls')),
]
```

---

## New API Endpoints

### Users (MySQL)
- `GET /api/users/` - List all users
- `POST /api/users/` - Create user
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user

### Devices (MySQL)
- `GET /api/devices/` - List all devices
- `POST /api/devices/` - Create device
- `GET /api/devices/{id}/` - Get device details
- `PUT /api/devices/{id}/` - Update device
- `DELETE /api/devices/{id}/` - Delete device
- `GET /api/devices/{id}/readings/` - Get device readings (MongoDB)
- `GET /api/devices/{id}/latest/` - Get latest reading (Redis)

### Readings (MongoDB via pymongo)
- `GET /api/readings/` - List readings with filters
- `GET /api/readings/latest_all/` - Get all latest readings (Redis)
- `GET /api/readings/stats/` - Get statistics (MongoDB)

### Legacy
- `GET /api/latest/{device_id}/` - Legacy endpoint (backward compatibility)

---

## Benefits of Migration

### 1. Performance
- ✅ Direct pymongo queries (no ORM translation)
- ✅ Redis caching layer for latest readings
- ✅ Optimized MongoDB queries with indexes

### 2. Reliability
- ✅ No more djongo dependency issues
- ✅ Automatic duplicate prevention via unique index
- ✅ Better error handling

### 3. Scalability
- ✅ Separation of concerns (MySQL metadata, MongoDB time-series, Redis cache)
- ✅ RESTful API with DRF ViewSets
- ✅ Flexible query parameters

### 4. Maintainability
- ✅ Clean architecture with dataclasses
- ✅ Comprehensive serializers
- ✅ Well-documented API endpoints

---

## Data Flow

```
IoT Device
    ↓ MQTT
Mosquitto Broker
    ↓ MQTT Consumer
Kafka (raw-data topic)
    ↓ Kafka Consumer
handle_payload()
    ├→ MySQL (User, Device)
    ├→ MongoDB (Reading) - pymongo
    └→ Redis (cache:latest) - 60s TTL
         ↓
    API Endpoints
         ├→ /api/users/ (MySQL)
         ├→ /api/devices/ (MySQL)
         ├→ /api/devices/{id}/readings/ (MongoDB via pymongo)
         ├→ /api/devices/{id}/latest/ (Redis)
         └→ /api/readings/* (MongoDB/Redis)
```

---

## Testing

### 1. Start Django Server
```powershell
# In Docker
docker exec -it iot-app python manage.py runserver 0.0.0.0:8000

# Or locally
python manage.py runserver
```

### 2. Run Test Script
```powershell
python scripts/test_api.py
```

### 3. Manual Testing
```powershell
# List devices
curl http://localhost:8000/api/devices/

# Get device readings
curl http://localhost:8000/api/devices/1/readings/?limit=10

# Get latest for all devices
curl http://localhost:8000/api/readings/latest_all/

# Get statistics
curl http://localhost:8000/api/readings/stats/
```

---

## Migration Checklist

- ✅ Replaced djongo models with pymongo ReadingClient
- ✅ Updated views.py with DRF ViewSets
- ✅ Created comprehensive serializers
- ✅ Created monitoring/urls.py with router
- ✅ Updated smart_iot/urls.py to include monitoring URLs
- ✅ Added Redis caching layer
- ✅ Implemented unique index for deduplication
- ✅ Created API documentation
- ✅ Created test scripts
- ⏳ Test API endpoints (run scripts/test_api.py)
- ⏳ Deploy to production

---

## Next Steps

1. **Test the API endpoints**:
   ```powershell
   python scripts/test_api.py
   ```

2. **Run the full pipeline**:
   ```powershell
   # Terminal 1: Start Celery workers
   docker exec -it iot-app celery -A smart_iot worker -l INFO
   
   # Terminal 2: Publish test data
   docker exec -it iot-app python scripts/publish.py
   
   # Terminal 3: Test API
   python scripts/test_api.py
   ```

3. **Monitor the logs**:
   ```powershell
   docker logs -f iot-app
   ```

4. **Check data in databases**:
   ```powershell
   # MySQL
   docker exec -it iot-mysql mysql -u root -p -e "USE iot; SELECT * FROM devices;"
   
   # MongoDB
   docker exec -it iot-mongodb mongosh -u root -p root --eval "db.readings.find().limit(5)"
   
   # Redis
   docker exec -it iot-redis redis-cli KEYS "latest:*"
   ```

---

## Troubleshooting

### Issue: Import errors in views.py
**Solution**: These are just Pylance warnings. The packages exist in the Docker container.

### Issue: No data in API responses
**Solution**: 
1. Make sure Celery workers are running
2. Publish some test data: `python scripts/publish.py`
3. Wait a few seconds for processing
4. Check MongoDB: `python scripts/test_mongodb.py`

### Issue: 404 on /api/devices/{id}/latest/
**Solution**: 
- This means no recent data in Redis (device offline)
- Redis TTL is 60 seconds - data expires quickly
- Publish new data to refresh the cache

### Issue: API returns empty list
**Solution**:
1. Check if data exists in databases
2. Run diagnostic scripts: `test_db_write.py`, `test_mongodb.py`, `test_redis.py`
3. Verify full pipeline is running

---

## Documentation Files

- `API_DOCUMENTATION.md` - Complete API endpoint documentation
- `PYMONGO_MIGRATION.md` - This file (migration summary)
- `HOW_TO_RUN.md` - How to run the system
- `REDIS_CACHING.md` - Redis caching implementation
- `FIX_MONGODB.md` - MongoDB setup and troubleshooting
- `FIX_DUPLICATES.md` - Duplicate handling
- `DEBUG_STEPS.md` - General debugging guide

---

## Conclusion

The migration from djongo to pymongo is **COMPLETE**. The system now has:

1. ✅ Pure pymongo for MongoDB (no djongo dependency)
2. ✅ RESTful API with DRF ViewSets
3. ✅ Redis caching for performance
4. ✅ Automatic duplicate prevention
5. ✅ Comprehensive API documentation
6. ✅ Test scripts for validation

**Ready to test and deploy!** 🚀
