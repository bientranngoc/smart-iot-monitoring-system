# 🏢 Smart IoT Monitoring System - Smart Building

Hệ thống giám sát và quản lý tòa nhà thông minh với IoT, streaming camera real-time, và điều khiển HVAC tự động.

![Django](https://img.shields.io/badge/Django-4.2-green)
![React](https://img.shields.io/badge/React-18.2-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Mục lục

- [Tổng quan](#-tổng-quan)
- [Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
- [Công nghệ sử dụng](#-công-nghệ-sử-dụng)
- [Cài đặt](#-cài-đặt)
- [Sử dụng](#-sử-dụng)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Screenshots](#-screenshots)

---

## 🎯 Tổng quan

**Smart IoT Monitoring System** là giải pháp toàn diện cho việc giám sát và quản lý tòa nhà thông minh, bao gồm:

### ✨ Tính năng chính

- 🌡️ **Giám sát Real-time**: Theo dõi nhiệt độ, độ ẩm, CO2, người vào ra
- 📹 **Live Camera Streaming**: Xem camera trực tiếp qua HLS từ iPhone/smartphone
- 🚨 **Alert System**: Cảnh báo tự động khi vượt ngưỡng an toàn
- ❄️ **HVAC Control**: Điều khiển hệ thống điều hòa thông minh
- 📊 **Dashboard**: Giao diện React hiện đại, responsive
- 🔄 **Real-time Updates**: Auto-refresh mỗi 30 giây
- 📈 **Data Analytics**: Lưu trữ và phân tích dữ liệu lịch sử

### 🏗️ Cấu trúc tòa nhà mẫu (ABC Office Tower)

- **Main Lobby** (Tầng 1): Giám sát ra vào, nhiệt độ môi trường
- **Server Room** (Tầng 1): Kiểm soát nhiệt độ nghiêm ngặt (18-22°C)
- **Parking Lot** (Tầng 0): Giám sát an ninh và môi trường
- **Office Floor 5** (Tầng 5): Tối ưu điều kiện làm việc

---

## 🏛️ Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                       │
│  ┌─────────────────┐         ┌──────────────────┐              │
│  │  React Dashboard│◄────────┤  Live Camera HLS │              │
│  │  (Port 3001)    │         │  (MediaMTX:8889) │              │
│  └────────┬────────┘         └──────────────────┘              │
└───────────┼──────────────────────────────────────────────────────┘
            │
            │ REST API (Port 8000)
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Django REST Framework + Celery                  │  │
│  │  • BuildingViewSet    • ZoneViewSet                       │  │
│  │  • SensorViewSet      • AlertViewSet                      │  │
│  │  • HVACControlViewSet • CameraViewSet                     │  │
│  └────────────────┬──────────────────────────────────────────┘  │
└───────────────────┼──────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────┐        ┌──────────────┐
│  MQTT Broker │        │    Kafka     │
│  (Mosquitto) │───────▶│  Streaming   │
│  Port 1883   │        │  Port 9092   │
└──────────────┘        └──────┬───────┘
        ▲                       │
        │                       ▼
┌──────────────┐        ┌──────────────┐
│ IoT Sensors  │        │   Celery     │
│ MQTT Publish │        │   Workers    │
└──────────────┘        └──────┬───────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  MySQL   │  │ MongoDB  │  │  Redis   │  │OpenSearch│       │
│  │ (Relational│ │(Time-series│ │ (Cache) │  │ (Search) │       │
│  │   Data)  │  │  Data)   │  │          │  │          │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### 🔄 Data Flow

1. **IoT Sensors** → MQTT Broker → Celery Worker
2. Celery Worker → Kafka Stream → Data Processing
3. Data Processing → MySQL (metadata) + MongoDB (time-series)
4. Celery Tasks → Check thresholds → Create alerts
5. HVAC Controller → Auto-adjust temperature
6. React Dashboard → Poll API → Display updates

---

## 🛠️ Công nghệ sử dụng

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

## 📦 Cài đặt

### Yêu cầu hệ thống

- Docker Desktop 20.x+
- Docker Compose 2.x+
- Node.js 18.x+ (cho frontend development)
- Python 3.11+ (nếu chạy local)
- iPhone/Android với iVCam app (cho camera streaming)
- OBS Studio (cho camera streaming)

### 1. Clone Repository

```bash
git clone https://github.com/bientranngoc/smart-iot-monitoring-system.git
cd smart-iot-monitoring-system
```

### 2. Cấu hình Environment Variables

```bash
# Copy file .env mẫu
cp .env.example .env

# Chỉnh sửa các biến môi trường
nano .env
```

**Các biến quan trọng:**
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

### 3. Khởi động Backend (Docker)

```bash
# Build và start tất cả services
docker-compose up -d

# Kiểm tra containers đang chạy
docker ps
```

**Services sẽ chạy:**
- `iot-app` (Django): http://localhost:8000
- `iot-mysql`: Port 3306
- `iot-mongodb`: Port 27017
- `iot-redis`: Port 6379
- `iot-mosquitto`: Port 1883, 9001
- `iot-kafka`: Port 9092
- `iot-celery`: Background worker
- `iot-mediamtx`: Port 8889, 1935
- `iot-opensearch`: Port 9200

### 4. Khởi tạo Database

```bash
# Chạy migrations
docker exec -it iot-app python manage.py migrate

# Tạo superuser
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

Frontend sẽ chạy tại: http://localhost:3001

### 6. Setup Camera Streaming (Optional)

#### a. Cài đặt iVCam
1. Tải **iVCam** app trên iPhone/Android
2. Tải **iVCam driver** trên PC: https://www.e2esoft.com/ivcam/
3. Kết nối phone và PC cùng WiFi
4. Mở app iVCam → Camera sẽ xuất hiện trên PC như webcam

#### b. Setup OBS Studio
1. Tải OBS Studio: https://obsproject.com/
2. Mở OBS → Add source → **Video Capture Device**
3. Chọn **e2eSoft iVCam** làm device
4. Settings → Stream:
   - Service: Custom
   - Server: `rtmp://localhost:1935/lobby_main`
   - Stream Key: để trống
5. Click **Start Streaming**

#### c. Kiểm tra stream
```bash
# Xem logs MediaMTX
docker logs iot-mediamtx --tail 20

# Test HLS stream
curl http://localhost:8889/lobby_main/index.m3u8
```

Stream URL: `http://localhost:8889/lobby_main/index.m3u8`

---

## 🚀 Sử dụng

### 1. Truy cập Dashboard

Mở trình duyệt: **http://localhost:3001**

Dashboard hiển thị:
- 📊 Stats cards: Average temperature, occupancy, CO2, energy usage
- 🏠 Zone cards: Real-time sensor data cho mỗi zone
- 🚨 Active alerts: Danh sách cảnh báo chưa xử lý
- 📹 Live camera: Click "Show Live Camera" để xem stream

### 2. Test với MQTT

#### Gửi sensor data thủ công:

```bash
# Chạy test script (publish multiple readings)
python scripts/test_alerts.py
```

Test script sẽ:
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

Truy cập Django Admin: **http://localhost:8000/admin**

Login với superuser đã tạo ở bước cài đặt.

Quản lý:
- Buildings, Zones, Devices
- Sensors, Cameras, HVAC Controls
- Alerts, Energy Logs
- Users & Permissions

---

## 📚 API Documentation

### Building Endpoints

#### `GET /api/buildings/`
Lấy danh sách tất cả buildings

**Response:**
```json
[
  {
    "id": 1,
    "name": "ABC Office Tower",
    "address": "123 Tech Street, Innovation District",
    "total_floors": 20,
    "total_zones": 4
  }
]
```

#### `GET /api/buildings/{id}/`
Chi tiết một building

---

### Zone Endpoints

#### `GET /api/zones/`
Lấy danh sách zones

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
Lấy trạng thái real-time của zone (bao gồm sensors, HVAC, cameras)

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
Lấy danh sách alerts

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
    "title": "🔥 Temperature Too High",
    "message": "Server Room: 30.0°C (Max: 22.0°C)",
    "sensor_value": 30.0,
    "created_at": "2025-10-21T08:00:00Z",
    "acknowledged": false
  }
]
```

#### `POST /api/building-alerts/{id}/acknowledge/`
Xác nhận đã xử lý alert

---

### HVAC Control Endpoints

#### `GET /api/hvac-controls/`
Lấy danh sách HVAC controls

#### `PATCH /api/hvac-controls/{id}/`
Cập nhật HVAC settings

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

### Dashboard không hiển thị dữ liệu

1. Kiểm tra backend đang chạy:
```bash
curl http://localhost:8000/api/buildings/
```

2. Kiểm tra CORS settings trong `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3001",
]
```

### Camera stream không chạy

1. Kiểm tra MediaMTX logs:
```bash
docker logs iot-mediamtx --tail 20
```

2. Kiểm tra OBS đã start streaming chưa

3. Test stream URL trực tiếp:
```bash
curl http://localhost:8889/lobby_main/index.m3u8
```

### MQTT messages không được xử lý

1. Kiểm tra Celery worker:
```bash
docker logs iot-celery --tail 50
```

2. Kiểm tra Kafka đang chạy:
```bash
docker ps | grep kafka
```

3. Restart Celery:
```bash
docker restart iot-celery
```

### Database connection errors

1. Kiểm tra MySQL container:
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
├── docs/                      # Documentation files
├── frontend/                  # React frontend
│   ├── public/               # Static files
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── LiveCameraView.jsx
│   │   │   └── ZoneCard.jsx
│   │   ├── pages/            # Page components
│   │   │   └── SmartBuildingDashboard.jsx
│   │   ├── services/         # API services
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── infra/                     # Infrastructure configs
│   └── mosquitto/
│       └── mosquitto.conf
├── monitoring/                # Django app - Smart Building
│   ├── migrations/
│   ├── admin.py              # Admin interface
│   ├── models.py             # 7 models (Building, Zone, etc.)
│   ├── serializers.py        # DRF serializers
│   ├── views.py              # API ViewSets
│   ├── tasks.py              # Celery tasks
│   └── urls.py               # URL routing
├── scripts/                   # Utility scripts
│   ├── consumer.py           # Kafka consumer
│   ├── mqtt_worker.py        # MQTT subscriber
│   ├── publish.py            # MQTT publisher
│   ├── test_alerts.py        # Alert testing
│   └── check_status.py       # Status checker
├── smart_iot/                 # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py             # Celery config
│   └── wsgi.py
├── docker-compose.yml         # Docker services
├── Dockerfile                 # Django app image
├── requirements.txt           # Python dependencies
├── manage.py                  # Django management
└── README.md                  # This file
```

---

## 🔐 Security Notes

### Production Deployment

⚠️ **Trước khi deploy production:**

1. **Đổi SECRET_KEY** trong `settings.py`
2. **Tắt DEBUG mode**: `DEBUG = False`
3. **Cấu hình ALLOWED_HOSTS**:
```python
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

4. **Update CORS_ALLOWED_ORIGINS** với domain thật
5. **Sử dụng environment variables** cho sensitive data
6. **Enable HTTPS** với SSL certificate
7. **Secure database credentials**
8. **Configure firewall rules**

### Environment Variables

Không commit file `.env` vào git. Sử dụng `.env.example` làm template.

---

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
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- Django & DRF community
- React & Vite developers
- MediaMTX for excellent RTSP/HLS streaming
- All open-source contributors

---

## 📮 Support

Nếu gặp vấn đề hoặc có câu hỏi:

1. 🐛 [Open an issue](https://github.com/bientranngoc/smart-iot-monitoring-system/issues)
2. 💬 [Discussions](https://github.com/bientranngoc/smart-iot-monitoring-system/discussions)
3. 📧 Email: your.email@example.com

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

