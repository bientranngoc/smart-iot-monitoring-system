# API Endpoints Documentation

## Overview
The IoT Monitoring System now uses Django REST Framework with ViewSets for a RESTful API. All endpoints use pymongo (not djongo) to query MongoDB.

## Architecture
- **MySQL**: Users and Devices metadata
- **MongoDB**: Time-series sensor readings (via pymongo ReadingClient)
- **Redis**: In-memory cache for latest readings (60s TTL)

## API Endpoints

### Base URL
All endpoints are prefixed with `/api/`

---

### 1. Users (MySQL)

**List all users**
```
GET /api/users/
```
Response:
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

**Get user details**
```
GET /api/users/{id}/
```

**Create user**
```
POST /api/users/
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com"
}
```

**Update user**
```
PUT /api/users/{id}/
PATCH /api/users/{id}/
```

**Delete user**
```
DELETE /api/users/{id}/
```

---

### 2. Devices (MySQL)

**List all devices**
```
GET /api/devices/
```
Response:
```json
[
  {
    "id": 1,
    "device_name": "Temperature Sensor 1",
    "user": 1,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

**Get device details**
```
GET /api/devices/{id}/
```

**Create device**
```
POST /api/devices/
Content-Type: application/json

{
  "device_name": "New Sensor",
  "user": 1
}
```

**Get readings for a specific device** (MongoDB)
```
GET /api/devices/{id}/readings/?limit=100&since=2024-01-01T00:00:00Z
```
Query parameters:
- `limit`: Number of readings to return (default: 100)
- `since`: ISO datetime to filter readings after this time (optional)

Response:
```json
[
  {
    "device_id": 1,
    "temperature": 25.5,
    "humidity": 60.3,
    "timestamp": "2024-01-01T12:30:00Z"
  }
]
```

**Get latest reading for a device** (Redis cache)
```
GET /api/devices/{id}/latest/
```
Response:
```json
{
  "device_id": 1,
  "temperature": 25.5,
  "humidity": 60.3,
  "timestamp": "2024-01-01T12:30:00Z",
  "status": "online"
}
```
Returns 404 if no recent data (device offline).

---

### 3. Readings (MongoDB via pymongo)

**List readings**
```
GET /api/readings/?device_id=1&limit=100&since=2024-01-01T00:00:00Z
```
Query parameters:
- `device_id`: Filter by device ID (optional, if omitted returns readings for all devices)
- `limit`: Number of readings to return (default: 100)
- `since`: ISO datetime to filter readings after this time (optional)

Response:
```json
[
  {
    "device_id": 1,
    "temperature": 25.5,
    "humidity": 60.3,
    "timestamp": "2024-01-01T12:30:00Z"
  }
]
```

**Get latest readings for ALL devices** (Redis cache)
```
GET /api/readings/latest_all/
```
Response:
```json
[
  {
    "device_id": 1,
    "temperature": 25.5,
    "humidity": 60.3,
    "timestamp": "2024-01-01T12:30:00Z",
    "status": "online"
  },
  {
    "device_id": 2,
    "temperature": 22.1,
    "humidity": 55.8,
    "timestamp": "2024-01-01T12:29:45Z",
    "status": "online"
  }
]
```

**Get statistics** (MongoDB)
```
GET /api/readings/stats/
```
Response:
```json
{
  "total_readings": 12500,
  "readings_by_device": [
    {"_id": 1, "count": 5000},
    {"_id": 2, "count": 7500}
  ],
  "active_devices": [1, 2],
  "active_count": 2
}
```

---

### 4. Legacy Endpoint (Backward Compatibility)

**Get latest reading for a device**
```
GET /api/latest/{device_id}/
```
This endpoint is kept for backward compatibility. It tries Redis first, then falls back to MongoDB.

---

## Testing the API

### Using curl (PowerShell)

**List all devices:**
```powershell
curl http://localhost:8000/api/devices/
```

**Get device readings:**
```powershell
curl http://localhost:8000/api/devices/1/readings/?limit=10
```

**Get latest reading:**
```powershell
curl http://localhost:8000/api/devices/1/latest/
```

**Get all latest readings:**
```powershell
curl http://localhost:8000/api/readings/latest_all/
```

**Get statistics:**
```powershell
curl http://localhost:8000/api/readings/stats/
```

**Create a new device:**
```powershell
curl -X POST http://localhost:8000/api/devices/ `
  -H "Content-Type: application/json" `
  -d '{\"device_name\": \"Test Sensor\", \"user\": 1}'
```

### Using Python requests

```python
import requests

BASE_URL = "http://localhost:8000/api"

# List devices
response = requests.get(f"{BASE_URL}/devices/")
print(response.json())

# Get device readings
response = requests.get(f"{BASE_URL}/devices/1/readings/", params={"limit": 10})
print(response.json())

# Get latest for all devices
response = requests.get(f"{BASE_URL}/readings/latest_all/")
print(response.json())

# Get statistics
response = requests.get(f"{BASE_URL}/readings/stats/")
print(response.json())
```

---

## Key Changes from djongo

### Before (djongo):
```python
# Old code using djongo ORM
reading = Reading.objects.using('mongodb').filter(device_id=device_id).order_by('-timestamp').first()
```

### After (pymongo):
```python
# New code using pymongo ReadingClient
client = ReadingClient()
readings = client.find_readings(device_id=device_id, limit=1)
reading = readings[0] if readings else None
```

### Benefits:
1. ✅ Direct pymongo queries - no ORM overhead
2. ✅ Better control over MongoDB operations
3. ✅ Automatic duplicate prevention with unique index
4. ✅ Redis caching layer for latest readings
5. ✅ RESTful API with DRF ViewSets
6. ✅ No more djongo dependency issues

---

## Data Flow

1. **MQTT Publish** → Mosquitto broker
2. **MQTT Consumer** → Kafka topic (raw-data)
3. **Kafka Consumer** → `handle_payload()` function:
   - Creates/updates User in MySQL
   - Creates/updates Device in MySQL
   - Inserts Reading to MongoDB (deduplicated by unique index)
   - Caches latest reading to Redis (60s TTL)
4. **API Endpoints** → Query MySQL/MongoDB/Redis and return data

---

## Notes

- All MongoDB queries use the `ReadingClient` class from `monitoring/models.py`
- Redis cache keys follow the pattern: `latest:device{device_id}`
- MongoDB has a unique compound index: `(device_id, timestamp)` to prevent duplicates
- ViewSets provide automatic CRUD operations for MySQL models
- Custom actions provide MongoDB and Redis query capabilities
