# Monitoring App - Smart Building IoT System

## 📁 Module Structure

The `monitoring/` app is organized using **Django best practices** with clear separation of concerns:

```
monitoring/
├── models/              # Data models (MySQL + MongoDB)
│   ├── base.py             # User, Device (legacy IoT)
│   ├── building.py         # Building, Zone
│   ├── sensor.py           # ZoneSensor, ZoneCamera
│   ├── control.py          # HVACControl, EnergyLog
│   ├── alert.py            # BuildingAlert
│   └── mongodb.py          # Reading, ReadingClient (pymongo)
│
├── serializers/         # REST API serializers
│   ├── base.py             # User, Device, Reading
│   ├── building.py         # Building, Zone
│   ├── sensor.py           # ZoneSensor, ZoneCamera
│   ├── control.py          # HVACControl
│   └── alert.py            # BuildingAlert
│
├── views/               # API ViewSets
│   ├── base.py             # UserViewSet, DeviceViewSet, ReadingViewSet
│   ├── building.py         # BuildingViewSet, ZoneViewSet
│   ├── alert.py            # BuildingAlertViewSet
│   └── control.py          # HVACControlViewSet
│
├── services/            # Business logic layer
│   ├── alert_service.py    # Threshold checking, alert creation
│   ├── hvac_service.py     # HVAC auto-control logic
│   ├── camera_service.py   # Camera recording triggers
│   └── cache_service.py    # Redis caching operations
│
├── streams/             # Real-time data streaming
│   ├── handlers.py         # Message processing callbacks
│   ├── mqtt_subscriber.py  # MQTT client (sensors -> MQTT)
│   ├── kafka_consumer.py   # Kafka consumer (MQTT -> Kafka -> DB)
│   ├── producers.py        # Kafka producer
│   └── runner.py           # Thread management
│
├── tasks/               # Celery async tasks
│   └── main.py             # MQTT/Kafka processing, payload handling
│
├── tests/               # Unit & integration tests
│   ├── unit/
│   └── integration/
│
├── migrations/          # Django database migrations
├── admin.py             # Django admin registration
├── apps.py              # App configuration
└── urls.py              # URL routing
```

---

## 🎯 Architecture Layers

### 1. **Data Layer** (`models/`)

**Purpose**: Define database schemas and data access patterns

- **MySQL Models** (via Django ORM):
  - `User`, `Device` - Base IoT entities
  - `Building`, `Zone` - Smart Building infrastructure
  - `ZoneSensor`, `ZoneCamera` - Sensor/camera devices
  - `HVACControl`, `EnergyLog` - Control systems
  - `BuildingAlert` - Alert management

- **MongoDB Models** (via pymongo):
  - `Reading` - Sensor reading dataclass
  - `ReadingClient` - MongoDB client wrapper

---

### 2. **API Layer** (`serializers/` + `views/`)

**Purpose**: REST API endpoints for frontend and external integrations

**Key ViewSets**:
- `BuildingViewSet` - CRUD + `/overview/` action
- `ZoneViewSet` - CRUD + `/status/`, `/by_floor/` actions
- `BuildingAlertViewSet` - CRUD + `/active/`, `/acknowledge/`, `/statistics/`
- `HVACControlViewSet` - CRUD + `/set_mode/`, `/set_temperature/`

---

### 3. **Business Logic Layer** (`services/`)

**Purpose**: Centralized business rules, reusable across views/tasks

**Services**:

#### `alert_service.py`
```python
from monitoring.services import check_building_thresholds

# Check sensor thresholds and create alerts
alerts_count = check_building_thresholds(
    zone_sensor=sensor,
    temperature=32.5,
    humidity=75.0
)
```

#### `hvac_service.py`
```python
from monitoring.services import auto_control_hvac

# Automatically control HVAC based on temperature
controlled = auto_control_hvac(zone)
# Returns True if HVAC was controlled, False otherwise
```

#### `camera_service.py`
```python
from monitoring.services import trigger_camera_recording

# Start camera recording when alert is created
triggered = trigger_camera_recording(zone, alert)
```

#### `cache_service.py`
```python
from monitoring.services import cache_latest_reading, get_latest_reading

# Cache sensor reading to Redis
cache_latest_reading(device_id=1, data={'temperature': 25.0}, ttl=60)

# Retrieve from cache
reading = get_latest_reading(device_id=1)
```

---

### 4. **Streaming Layer** (`streams/`)

**Purpose**: Real-time sensor data pipeline

**Data Flow**:
```
IoT Sensors
    ↓ (publish JSON)
MQTT Broker (iot-mosquitto:1883)
    ↓ (subscribe: sensors/data)
mqtt_subscriber.py → handlers.on_mqtt_message()
    ↓ send_to_kafka()
Kafka Broker (iot-kafka:9092, topic: raw-data)
    ↓ (consume)
kafka_consumer.py → handlers.on_kafka_message()
    ↓ tasks.handle_payload()
    ├─→ MySQL (Device, ZoneSensor updates)
    ├─→ MongoDB (Reading storage)
    ├─→ Redis (Latest reading cache)
    ├─→ OpenSearch (Indexing for search)
    ├─→ Alert Service (Threshold checking)
    └─→ HVAC Service (Auto-control)
```

**Configuration**:
- MQTT: `iot-mosquitto:1883`, topic `sensors/data`
- Kafka: `iot-kafka:9092`, topic `raw-data`, group `iot-group`

---

### 5. **Task Layer** (`tasks/`)

**Purpose**: Celery async tasks for background processing

**Main Task**: `handle_payload(payload: str)`

Processes sensor readings through:
1. JSON parsing
2. User/Device creation (MySQL)
3. Reading storage (MongoDB)
4. Cache update (Redis)
5. Search indexing (OpenSearch)
6. Zone sensor update (MySQL)
7. Threshold checking → Alerts
8. HVAC auto-control

**Celery Tasks**:
```python
from monitoring.tasks import ping, mqtt_subscribe_task, kafka_consumer_task

# Health check
result = ping.delay()

# Manually start streams (normally auto-started by worker_ready signal)
mqtt_subscribe_task.delay()
kafka_consumer_task.delay()
```

---

## 🔧 Usage Examples

### Creating a Smart Building Zone

```python
from monitoring.models import Building, Zone, Device, ZoneSensor

# Create building
building = Building.objects.create(
    name="ABC Tower",
    address="123 Smart St",
    floors=10,
    total_area=5000.0
)

# Create zone
zone = Zone.objects.create(
    building=building,
    name="Lobby",
    floor=1,
    zone_type='LOBBY',
    area=200.0,
    temp_min=22.0,
    temp_max=26.0
)

# Add temperature sensor
device = Device.objects.create(name="TempSensor_001", user=user)
sensor = ZoneSensor.objects.create(
    zone=zone,
    device=device,
    sensor_type='TEMPERATURE',
    location_description="Lobby ceiling"
)
```

### Sending Sensor Data via MQTT

```bash
# Publish temperature reading
mosquitto_pub -h localhost -p 1883 -t sensors/data -m '{
  "device_id": 1,
  "temperature": 28.5,
  "humidity": 65.0,
  "timestamp": "2025-10-21T10:30:00Z"
}'
```

**Processing Flow**:
1. MQTT subscriber receives message
2. Forwards to Kafka topic `raw-data`
3. Kafka consumer processes message
4. `handle_payload()` updates databases
5. Zone sensor reading updated
6. If temp > 26°C → Alert created
7. HVAC auto-control triggered (if in AUTO mode)

### Querying via REST API

```python
import requests

# Get building overview
response = requests.get('http://localhost:8000/api/buildings/1/overview/')
data = response.json()

print(f"Building: {data['building']['name']}")
print(f"Active Alerts: {data['active_alerts']}")
for zone in data['zones']:
    print(f"  Zone {zone['name']}: {zone['temperature']}°C - Status: {zone['status']}")

# Get active alerts
alerts = requests.get('http://localhost:8000/api/building-alerts/active/').json()
for alert in alerts:
    print(f"[{alert['severity']}] {alert['title']} - {alert['zone_name']}")

# Acknowledge alert
requests.post(f'http://localhost:8000/api/building-alerts/{alert_id}/acknowledge/')
```

---

## 🧪 Testing

### Run Tests

```bash
# All tests
docker exec iot-app python manage.py test monitoring

# Specific test file
docker exec iot-app python manage.py test monitoring.tests.unit.test_services

# With coverage
docker exec iot-app coverage run --source='monitoring' manage.py test monitoring
docker exec iot-app coverage report
```

### Manual Testing

```bash
# 1. Start containers
docker-compose up -d

# 2. Check Django
docker exec iot-app python manage.py check

# 3. Test MQTT pipeline
python scripts/test_alerts.py

# 4. View logs
docker logs iot-celery -f

# 5. Check Redis cache
docker exec iot-redis redis-cli KEYS "latest:*"
docker exec iot-redis redis-cli GET "latest:device1"

# 6. Query MongoDB
docker exec iot-mongodb mongosh iot --eval "db.readings.find().limit(10)"

# 7. Check Kafka topics
docker exec iot-kafka kafka-topics --list --bootstrap-server localhost:9092
docker exec iot-kafka kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic raw-data --from-beginning --max-messages 10
```

---

## 📊 Database Models Reference

### Building Models

| Model | Fields | Purpose |
|-------|--------|---------|
| `Building` | name, address, floors, total_area, manager | Top-level building entity |
| `Zone` | building, name, floor, zone_type, temp_min/max | Monitored area (Lobby, Office, etc.) |

### Sensor Models

| Model | Fields | Purpose |
|-------|--------|---------|
| `ZoneSensor` | zone, device, sensor_type, latest_reading | Temperature, humidity, CO2, etc. sensors |
| `ZoneCamera` | zone, name, rtsp_url, mediamtx_path | Security/monitoring cameras |

### Control Models

| Model | Fields | Purpose |
|-------|--------|---------|
| `HVACControl` | zone, mode, set_temperature, is_cooling/heating | HVAC system control |
| `EnergyLog` | zone, hvac_consumption, lighting_consumption | Energy tracking |

### Alert Models

| Model | Fields | Purpose |
|-------|--------|---------|
| `BuildingAlert` | zone, alert_type, severity, message, acknowledged | Temperature/humidity/security alerts |

---

## 🆘 Troubleshooting

### Celery not processing messages
```bash
# Check Celery worker logs
docker logs iot-celery -f

# Restart Celery worker
docker-compose restart celery

# Check if streams started
docker exec iot-celery ps aux | grep python
```

### MQTT messages not reaching Kafka
```bash
# Test MQTT connection
mosquitto_sub -h localhost -p 1883 -t sensors/data

# Check Kafka topics
docker exec iot-kafka kafka-topics --list --bootstrap-server localhost:9092

# View Kafka consumer lag
docker exec iot-kafka kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group iot-group --describe
```

---

## 📚 Additional Resources

- [Django Best Practices](https://docs.djangoproject.com/en/4.2/misc/design-philosophies/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Confluent Kafka Python](https://docs.confluent.io/kafka-clients/python/current/overview.html)
- [Paho MQTT Python](https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php)

---

**Last Updated**: October 21, 2025  
**Version**: 2.0.0 (Refactored Structure)
