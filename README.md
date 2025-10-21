# 🏢 Smart IoT Monitoring System - Smart Building

A comprehensive smart building monitoring and management system with IoT sensors, real-time camera streaming, and automated HVAC control.

![Django](https://img.shields.io/badge/Django-4.2-green)
![React](https://img.shields.io/badge/React-18.2-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Table of Contents

- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Screenshots](#-screenshots)

---

## 🎯 Overview

**Smart IoT Monitoring System** is a comprehensive solution for smart building monitoring and management, including:

### ✨ Key Features

- 🌡️ **Real-time Monitoring**: Track temperature, humidity, CO2 levels, occupancy
- 📹 **Live Camera Streaming**: View live camera feeds via HLS from iPhone/smartphone
- 🚨 **Alert System**: Automatic alerts when safety thresholds are exceeded
- ❄️ **HVAC Control**: Smart climate control system automation
- 📊 **Dashboard**: Modern, responsive React interface
- 🔄 **Real-time Updates**: Auto-refresh every 30 seconds
- 📈 **Data Analytics**: Historical data storage and analysis

### 🏗️ Sample Building Structure (FPT Telecom)

- **Main Lobby** (Floor 1): Entry monitoring, environmental tracking
- **Server Room** (Floor 1): Strict temperature control (18-22°C)
- **Parking Lot** (Floor 0): Security and environmental monitoring
- **Office** (Floor 1): Optimal working conditions

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                      │
│  ┌─────────────────┐         ┌──────────────────┐               │
│  │  React Dashboard│◄────────┤  Live Camera HLS │               │
│  │  (Port 3001)    │         │  (MediaMTX:8889) │               │
│  └────────┬────────┘         └──────────────────┘               │
└───────────┼─────────────────────────────────────────────────────┘
            │
            │ REST API (Port 8000)
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │           Django REST Framework + Celery                  │  │
│  │         • BuildingViewSet    • ZoneViewSet                │  │
│  │         • SensorViewSet      • AlertViewSet               │  │
│  │         • HVACControlViewSet • CameraViewSet              │  │
│  └────────────────┬──────────────────────────────────────────┘  │
└───────────────────┼─────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────┐        ┌──────────────┐
│  MQTT Broker │        │    Kafka     │
│  (Mosquitto) │───────▶│  Streaming   │
│  Port 1883   │        │  Port 9092   │
└──────────────┘        └──────┬───────┘
        ▲                      │
        │                      ▼
┌──────────────┐        ┌──────────────┐
│ IoT Sensors  │        │   Celery     │
│ MQTT Publish │        │   Workers    │
└──────────────┘        └──────┬───────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                            │
│  ┌────────────┐  ┌────────────┐  ┌──────────┐  ┌──────────┐    │
│  │  MySQL     │  │ MongoDB    │  │  Redis   │  │OpenSearch│    │
│  │ (Relational│  │(Time-series│  │ (Cache)  │  │ (Search) │    │
│  │   Data)    │  │  Data)     │  │          │  │          │    │
│  └────────────┘  └────────────┘  └──────────┘  └──────────┘    │
└────────────────────────────────────────────────────────────────┘
```

### 🔄 Data Flow

1. **IoT Sensors** → MQTT Broker → Celery Worker
2. Celery Worker → Kafka Stream → Data Processing
3. Data Processing → MySQL (metadata) + MongoDB (time-series)
4. Celery Tasks → Check thresholds → Create alerts
5. HVAC Controller → Auto-adjust temperature
6. React Dashboard → Poll API → Display updates

---

## 🛠️ Technology Stack

### Backend
- **Django 4.2.7** - Web framework
- **Django REST Framework 3.14.0** - REST API
- **Celery 5.3.4** - Asynchronous task processing
- **MySQL 8.0** - Relational database
- **MongoDB 7.0** - Time-series data storage
- **Redis** - Cache & message broker
- **Kafka** - Event streaming
- **OpenSearch 2.8.0** - Search & analytics

### Frontend
- **React 18.2.0** - UI library
- **Vite 5.0.0** - Build tool
- **Axios 1.6.0** - HTTP client
- **HLS.js** - Video streaming
- **Tailwind CSS 3.3.0** - Styling
- **Lucide React** - Icons

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **MQTT (Mosquitto 2.0)** - IoT messaging
- **MediaMTX v1.15.2** - RTSP/RTMP → HLS streaming
- **OBS Studio** - Camera capture & streaming

### IoT Integration
- **iVCam** - Virtual webcam (iPhone → PC)
- **Paho MQTT** - MQTT client library

---

## 📦 Installation

### System Requirements

- Docker Desktop 20.x+
- Docker Compose 2.x+
- Node.js 18.x+ 
- Python 3.11+
- iPhone/Android with iVCam app
- OBS Studio 

### 1. Clone Repository

```bash
git clone https://github.com/bientranngoc/smart-iot-monitoring-system.git
cd smart-iot-monitoring-system
```

### 2. Configure Environment Variables

```bash
# Copy example .env file
cp .env.example .env

# Edit environment variables
nano .env
```

**Important variables:**
```env
# Database
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=smart_iot_db

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# Redis
REDIS_URL=redis://iot-redis:6379/0

# MediaMTX
MEDIAMTX_PORT=8889
```

### 3. Start Backend (Docker)

```bash
# Build and start all services
docker-compose up -d

# Check running containers
docker ps
```

**Running services:**
- `iot-app` (Django): http://localhost:8000
- `iot-mysql`: Port 3306
- `iot-mongodb`: Port 27017
- `iot-redis`: Port 6379
- `iot-mosquitto`: Port 1883, 9001
- `iot-kafka`: Port 9092
- `iot-celery`: Background worker
- `iot-mediamtx`: Port 8889, 1935
- `iot-opensearch`: Port 9200

### 4. Initialize Database

```bash
# Run migrations
docker exec -it iot-app python manage.py migrate

# Create superuser
docker exec -it iot-app python manage.py createsuperuser

# Load sample data (optional)
docker exec -it iot-app python manage.py loaddata fixtures/sample_building.json
```

### 5. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run at: http://localhost:3000

### 6. Setup Camera Streaming (Optional)

#### a. Install iVCam
1. Download **iVCam** app on iPhone/Android
2. Download **iVCam driver** on PC: https://www.e2esoft.com/ivcam/
3. Connect phone and PC to the same WiFi
4. Open iVCam app → Camera will appear on PC as webcam

#### b. Setup OBS Studio
1. Download OBS Studio: https://obsproject.com/
2. Open OBS → Add source → **Video Capture Device**
3. Select **e2eSoft iVCam** as device
4. Settings → Stream:
   - Service: Custom
   - Server: `rtmp://localhost:1935/lobby_main`
   - Stream Key: leave empty
5. Click **Start Streaming**

#### c. Verify stream
```bash
# View MediaMTX logs
docker logs iot-mediamtx --tail 20

# Test HLS stream
curl http://localhost:8889/lobby_main/index.m3u8
```

Stream URL: `http://localhost:8889/lobby_main/index.m3u8`

---

## 🚀 Usage

### 1. Access Dashboard

Open browser: **http://localhost:3000**

Dashboard displays:
- 📊 Stats cards: Average temperature, occupancy, CO2, energy usage
- 🏠 Zone cards: Real-time sensor data for each zone
- 🚨 Active alerts: List of unacknowledged alerts
- 📹 Live camera: Click "Show Live Camera" to view stream

### 2. Test with MQTT

#### Send sensor data manually:

```bash
# Run test script (publish multiple readings)
python scripts/test_alerts.py
```

Test script will:
- ✅ Publish normal sensor readings
- ⚠️ Trigger high temperature alerts (>28°C)
- 🔥 Trigger extreme temperature alerts (>32°C)
- 🌡️ Test multiple zones simultaneously
- ✅ Return to normal conditions

#### Publish single message:

```bash
# Install paho-mqtt
pip install paho-mqtt

# Run Python script
python scripts/publish.py
```

**Format message:**
```json
{
  "device_id": 1,
  "temperature": 25.5,
  "humidity": 55.0,
  "timestamp": "2025-10-21T08:00:00"
}
```

### 3. API Endpoints

#### Get all buildings
```bash
curl http://localhost:8000/api/buildings/
```

#### Get zone status with sensors
```bash
curl http://localhost:8000/api/zones/1/status/
```

#### Get active alerts
```bash
curl http://localhost:8000/api/building-alerts/
```

#### Get HVAC controls
```bash
curl http://localhost:8000/api/hvac-controls/
```

### 4. Admin Panel

Access Django Admin: **http://localhost:8000/admin**

Login with the superuser created during installation.

Manage:
- Buildings, Zones, Devices
- Sensors, Cameras, HVAC Controls
- Alerts, Energy Logs
- Users & Permissions

---

## 📚 API Documentation

### Building Endpoints

#### `GET /api/buildings/`
Get list of all buildings

**Response:**
```json
[
  {
    "id": 1,
    "name": "FPT Telecom",
    "address": "No. 336-340 Huynh Tan Phat, Tan Thuan Tay Ward, District 7, HCMC",
    "total_floors": 4,
    "total_zones": 4
  }
]
```

#### `GET /api/buildings/{id}/`
Get building details

---

### Zone Endpoints

#### `GET /api/zones/`
Get list of zones

**Response:**
```json
[
  {
    "id": 1,
    "name": "Main Lobby",
    "floor": 1,
    "zone_type": "LOBBY",
    "status": "NORMAL",
    "target_temperature": 24.0
  }
]
```

#### `GET /api/zones/{id}/status/`
Get real-time zone status (includes sensors, HVAC, cameras)

**Response:**
```json
{
  "zone": {
    "id": 1,
    "name": "Main Lobby",
    "floor": 1,
    "zone_type": "LOBBY",
    "status": "NORMAL"
  },
  "sensors": [
    {
      "id": 1,
      "type": "TEMPERATURE",
      "value": 23.0,
      "unit": "°C",
      "timestamp": "2025-10-21T08:00:00Z"
    }
  ],
  "hvac": {
    "id": 1,
    "mode": "AUTO",
    "current_temp": 23.0,
    "set_temp": 24.0,
    "is_cooling": false,
    "is_heating": false,
    "status": "Standby"
  },
  "cameras": [
    {
      "id": 1,
      "name": "Lobby Main Camera",
      "hls_url": "http://localhost:8889/lobby_main/index.m3u8",
      "is_active": true
    }
  ]
}
```

---

### Alert Endpoints

#### `GET /api/building-alerts/`
Get list of alerts

**Query Parameters:**
- `acknowledged` (boolean): Filter by acknowledged status

**Response:**
```json
[
  {
    "id": 1,
    "zone_name": "Server Room",
    "alert_type": "TEMPERATURE",
    "severity": "CRITICAL",
    "title": "Temperature Too High",
    "message": "Server Room: 30.0°C (Max: 22.0°C)",
    "sensor_value": 30.0,
    "created_at": "2025-10-21T08:00:00Z",
    "acknowledged": false
  }
]
```

#### `POST /api/building-alerts/{id}/acknowledge/`
Acknowledge alert as handled

---

### HVAC Control Endpoints

#### `GET /api/hvac-controls/`
Get list of HVAC controls

#### `PATCH /api/hvac-controls/{id}/`
Update HVAC settings

**Request Body:**
```json
{
  "mode": "AUTO",
  "set_temp": 24.0,
  "fan_speed": 60
}
```

---

## 🧪 Testing

### 1. Test MQTT Publishing

```bash
# Run comprehensive test suite
python scripts/test_alerts.py
```

**Test scenarios:**
- ✅ Normal conditions (no alerts)
- ⚠️ High temperature (28-32°C)
- 🔥 Extreme temperature (>32°C)
- 🌊 Multiple zones rapid-fire
- ✅ Recovery to normal

### 2. Test API Endpoints

```bash
# Test building list
curl http://localhost:8000/api/buildings/

# Test zone status
curl http://localhost:8000/api/zones/1/status/

# Test alerts
curl http://localhost:8000/api/building-alerts/
```

### 3. Check Logs

```bash
# Django app logs
docker logs iot-app --tail 100

# Celery worker logs
docker logs iot-celery --tail 100

# MediaMTX logs
docker logs iot-mediamtx --tail 50

# MQTT broker logs
docker logs iot-mosquitto --tail 50
```

### 4. Monitor Services

```bash
# Check all containers
docker ps

# Check resource usage
docker stats

# Check Kafka topics
docker exec -it iot-kafka kafka-topics --list --bootstrap-server localhost:9092
```

---

## 📸 Screenshots

### Dashboard Overview
![Dashboard](docs/screenshots/dashboard.png)
*Main dashboard showing 4 zones with real-time sensor data*

### Live Camera Stream
![Camera](docs/screenshots/camera-stream.png)
*HLS live streaming from iPhone camera via MediaMTX*

### Active Alerts
![Alerts](docs/screenshots/alerts.png)
*Critical temperature alerts with zone information*

### Zone Detail
![Zone](docs/screenshots/zone-detail.png)
*Individual zone card with HVAC status*

---

## 🔧 Troubleshooting

### Dashboard not displaying data

1. Check if backend is running:
```bash
curl http://localhost:8000/api/buildings/
```

2. Check CORS settings in `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3001",
]
```

### Camera stream not working

1. Check MediaMTX logs:
```bash
docker logs iot-mediamtx --tail 20
```

2. Verify OBS has started streaming

3. Test stream URL directly:
```bash
curl http://localhost:8889/lobby_main/index.m3u8
```

### MQTT messages not being processed

1. Check Celery worker:
```bash
docker logs iot-celery --tail 50
```

2. Check if Kafka is running:
```bash
docker ps | grep kafka
```

3. Restart Celery:
```bash
docker restart iot-celery
```

### Database connection errors

1. Check MySQL container:
```bash
docker logs iot-mysql --tail 20
```

2. Reset database:
```bash
docker-compose down -v
docker-compose up -d
docker exec -it iot-app python manage.py migrate
```

---

## 📁 Project Structure

```
smart-iot-monitoring-system/
├── docs/                      
├── frontend/                  
│   ├── public/               
│   ├── src/
│   │   ├── components/       
│   │   │   ├── LiveCameraView.jsx
│   │   │   └── ZoneCard.jsx
│   │   ├── pages/            
│   │   │   └── SmartBuildingDashboard.jsx
│   │   ├── services/         
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── infra/                     
│   └── mosquitto/
│       └── mosquitto.conf
├── monitoring/                
│   ├── migrations/
│   ├── admin.py              
│   ├── models.py             
│   ├── serializers.py        
│   ├── views.py              
│   ├── tasks.py               # Celery tasks
│   └── urls.py               
├── scripts/                  # Utility scripts
│   ├── consumer.py            # Kafka consumer
│   ├── mqtt_worker.py         # MQTT subscriber
│   ├── publish.py             # MQTT publisher
│   ├── test_alerts.py         # Alert testing
│   └── check_status.py        # Status checker
├── smart_iot/                # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py             # Celery config
│   └── wsgi.py
├── docker-compose.yml         
├── Dockerfile                 
├── requirements.txt           
├── manage.py                  
└── README.md                  
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Bien Tran Ngoc**
- GitHub: [@bientranngoc](https://github.com/bientranngoc)
- Email: bientran.dev@gmail.com

---

## 🙏 Acknowledgments

- Django & DRF community
- React & Vite developers
- MediaMTX for excellent RTSP/HLS streaming
- All open-source contributors

---

## 📮 Support

If you encounter issues or have questions:

1. 🐛 [Open an issue](https://github.com/bientranngoc/smart-iot-monitoring-system/issues)
2. 💬 [Discussions](https://github.com/bientranngoc/smart-iot-monitoring-system/discussions)
3. 📧 Email: bientran.dev@gmail.com

---

## 🗺️ Roadmap

### Phase 4 - Future Enhancements

- [ ] WebSocket support for real-time updates (no polling)
- [ ] Mobile app (React Native)
- [ ] AI-powered predictive maintenance
- [ ] Energy optimization algorithms
- [ ] Multi-building support
- [ ] Advanced analytics dashboard
- [ ] Grafana integration
- [ ] Kubernetes deployment configs
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Unit & integration tests

---

**⭐ If you find this project helpful, please give it a star!**

