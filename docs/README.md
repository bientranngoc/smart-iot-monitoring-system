# 📚 Smart Building IoT System - Documentation

Comprehensive guides for Smart Building monitoring system with real phone cameras.

---

## 📖 Available Guides

### 🏢 [SMART_BUILDING_PHASE1.md](./SMART_BUILDING_PHASE1.md)
**Database & Models Setup**
- Smart Building database schema
- 7 Django models (Building, Zone, ZoneSensor, etc.)
- Sample data creation
- Database migrations

**When to use**: First-time setup, understanding data structure

---

### ⚙️ [SMART_BUILDING_PHASE2.md](./SMART_BUILDING_PHASE2.md)
**Backend API Implementation**
- REST API endpoints
- Celery task processing
- HVAC auto-control logic
- Alert system
- Threshold monitoring

**When to use**: Backend development, API integration

---

### 📱 [PHONE_CAMERA_SETUP.md](./PHONE_CAMERA_SETUP.md) ⭐ **NEW!**
**Complete Phone Camera Integration Guide**
- Turn old phones into IP cameras
- 3 methods: IP Webcam (Android), DroidCam, iVCam (iOS)
- MediaMTX configuration
- Production deployment tips
- Troubleshooting guide

**When to use**: 
- Want real camera instead of simulation
- Setting up multi-camera monitoring
- Production deployment with physical cameras

**Time required**: 15-30 minutes per camera

---

### ⚡ [PHONE_CAMERA_QUICK_REFERENCE.md](./PHONE_CAMERA_QUICK_REFERENCE.md) ⭐ **NEW!**
**Quick Reference Card**
- 5-minute quick start
- Common scenarios
- Troubleshooting commands
- Settings cheatsheet
- Emergency procedures

**When to use**: 
- Need quick commands
- Troubleshooting issues
- Reference during setup

**Time required**: 2-5 minutes

---

## 🚀 Recommended Learning Path

### For Beginners (Full Journey)

```
Day 1: Understanding the System
├─ Read: SMART_BUILDING_PHASE1.md
│  └─ Learn: Database structure, models, relationships
│
├─ Action: Run Phase 1 setup
│  └─ Create database, apply migrations, load sample data
│
└─ Verify: API returns building data

Day 2: Backend Logic
├─ Read: SMART_BUILDING_PHASE2.md
│  └─ Learn: API endpoints, Celery tasks, HVAC control
│
├─ Action: Test backend functionality
│  └─ Publish MQTT messages, verify alerts, check HVAC
│
└─ Verify: End-to-end flow works (MQTT → Alert → HVAC)

Day 3: Camera Integration
├─ Read: PHONE_CAMERA_SETUP.md (Sections 1-6)
│  └─ Learn: Phone camera apps, RTSP streams, MediaMTX
│
├─ Action: Setup first phone camera
│  └─ Install app, test connection, update database
│
└─ Verify: Stream visible in browser

Day 4: Production Deployment
├─ Read: PHONE_CAMERA_SETUP.md (Sections 7-10)
│  └─ Learn: Multi-camera setup, optimization, troubleshooting
│
├─ Action: Deploy all cameras
│  └─ Setup 4 zones, optimize settings, test stability
│
└─ Verify: 24-hour stress test passed

Day 5: Frontend Dashboard (Coming Soon)
└─ Read: SMART_BUILDING_PHASE3.md (When available)
   └─ Learn: React components, live video, charts
```

### For Experienced Developers (Fast Track)

```
Hour 1: Database + Backend
├─ Skim: SMART_BUILDING_PHASE1.md + PHASE2.md
└─ Run: Phase 1 + 2 setup scripts

Hour 2: Camera Setup  
├─ Read: PHONE_CAMERA_QUICK_REFERENCE.md
└─ Run: Quick start commands for 1-2 cameras

Hour 3: Testing & Deployment
├─ Reference: Troubleshooting sections
└─ Deploy: Production configuration
```

---

## 🎯 Documentation by Use Case

### I want to...

#### "Set up the entire system from scratch"
1. Start with **SMART_BUILDING_PHASE1.md**
2. Continue with **SMART_BUILDING_PHASE2.md**
3. Finish with **PHONE_CAMERA_SETUP.md**

#### "Use real phone cameras instead of fake streams"
→ Go directly to **PHONE_CAMERA_SETUP.md**

#### "Quickly fix camera connection issues"
→ Open **PHONE_CAMERA_QUICK_REFERENCE.md** → Troubleshooting section

#### "Add a new zone with camera"
→ **SMART_BUILDING_PHASE1.md** (Add zone) + **PHONE_CAMERA_QUICK_REFERENCE.md** (Setup camera)

#### "Understand the API endpoints"
→ **SMART_BUILDING_PHASE2.md** → API section

#### "Customize HVAC control logic"
→ **SMART_BUILDING_PHASE2.md** → Celery tasks section

---

## 📊 Feature Coverage Matrix

| Feature | Phase 1 | Phase 2 | Phone Camera | Quick Ref |
|---------|---------|---------|--------------|-----------|
| Database models | ✅ | - | - | - |
| Sample data | ✅ | - | - | - |
| REST APIs | - | ✅ | - | - |
| HVAC control | - | ✅ | - | - |
| Alert system | - | ✅ | - | - |
| Camera streaming | - | - | ✅ | - |
| MediaMTX setup | - | - | ✅ | - |
| Phone camera apps | - | - | ✅ | ✅ |
| Troubleshooting | - | ⚠️ | ✅ | ✅ |
| Quick commands | - | - | - | ✅ |
| Production tips | - | - | ✅ | ✅ |

Legend: ✅ Full coverage | ⚠️ Partial coverage | - Not covered

---

## 🛠️ Quick Command Reference

### Setup Commands
```powershell
# Phase 1: Database
docker exec iot-app python scripts/create_smart_building_data.py

# Phase 2: Test backend
docker exec iot-app python scripts/test_smart_building.py

# Phone Camera: Test connection
docker exec iot-app python scripts/test_phone_camera.py 192.168.1.105

# Phone Camera: Update database
docker exec iot-app python scripts/update_phone_camera.py "Server Room" 192.168.1.105

# Phone Camera: Setup all
docker exec iot-app python scripts/setup_all_phone_cameras.py
```

### Verification Commands
```powershell
# Check API
Invoke-WebRequest -Uri "http://localhost:8000/api/buildings/1/overview/" -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json

# Check alerts
Invoke-WebRequest -Uri "http://localhost:8000/api/building-alerts/active/" -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json

# Check cameras
Start-Process "http://localhost:8889/"

# Check logs
docker logs iot-celery --tail 50
docker logs iot-mediamtx --tail 50
```

### Troubleshooting Commands
```powershell
# Restart services
docker-compose restart celery
docker-compose restart mediamtx

# Check status
docker-compose ps

# View all logs
docker-compose logs --tail 50
```

---

## 📱 Camera App Downloads

### Android
- **IP Webcam** (Recommended): [Play Store](https://play.google.com/store/apps/details?id=com.pas.webcam)
- **DroidCam**: [Play Store](https://play.google.com/store/apps/details?id=com.dev47apps.droidcam)

### iOS
- **iVCam**: [App Store](https://apps.apple.com/app/ivcam-webcam/id1164464478)
- **DroidCam OBS**: [App Store](https://apps.apple.com/app/droidcam-obs/id1510258102)

---

## 🎓 Learning Resources

### External Documentation
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [MediaMTX GitHub](https://github.com/bluenviron/mediamtx)
- [RTSP Protocol Guide](https://en.wikipedia.org/wiki/Real_Time_Streaming_Protocol)
- [HLS Streaming](https://developer.apple.com/streaming/)

### Related Technologies
- **MQTT**: Message broker for IoT sensors
- **Kafka**: Event streaming platform
- **Redis**: Caching and task queue
- **MongoDB**: Sensor data storage
- **MySQL**: Relational database for building data
- **Docker**: Containerization

---

## 🤝 Contributing to Documentation

### Found an issue?
1. Note the document name and section
2. Describe the issue or improvement
3. Submit feedback

### Want to add content?
- Follow existing format
- Include code examples
- Add troubleshooting tips
- Test all commands before documenting

---

## 📞 Support

### Check Logs First
```powershell
# Application logs
docker logs iot-app --tail 100

# Celery processing
docker logs iot-celery --tail 100

# MediaMTX streaming
docker logs iot-mediamtx --tail 100

# All services
docker-compose logs --tail 50
```

### Common Issues & Solutions

| Issue | Quick Fix | Full Guide |
|-------|-----------|------------|
| Camera not streaming | `docker-compose restart mediamtx` | PHONE_CAMERA_QUICK_REFERENCE.md |
| Alert not triggering | Check Celery logs | SMART_BUILDING_PHASE2.md |
| API returning 404 | Check URL routing | SMART_BUILDING_PHASE2.md |
| Phone IP changed | Run update_phone_camera.py | PHONE_CAMERA_QUICK_REFERENCE.md |
| MediaMTX connection failed | Check phone WiFi + app running | PHONE_CAMERA_SETUP.md §7 |

---

## 🗺️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     SMART BUILDING SYSTEM                    │
└─────────────────────────────────────────────────────────────┘

📱 PHONE CAMERAS (Phone Camera Guides)
  ├─ IP Webcam (Android) → RTSP → MediaMTX
  ├─ DroidCam (Android/iOS) → RTSP → MediaMTX
  └─ iVCam (iOS) → RTSP → MediaMTX
           ↓
🎥 MediaMTX (Streaming Server)
  ├─ HLS output → http://localhost:8889/{path}/index.m3u8
  └─ WebRTC output → http://localhost:8889/{path}/
           ↓
🌐 DJANGO REST API (Phase 1 & 2)
  ├─ /api/buildings/ → Building overview with zones
  ├─ /api/zones/ → Zone details with sensors + cameras
  ├─ /api/building-alerts/ → Real-time alerts
  └─ /api/hvac-controls/ → HVAC status & control
           ↓
⚙️  CELERY WORKERS (Phase 2)
  ├─ Process MQTT sensor data
  ├─ Check temperature thresholds
  ├─ Auto-control HVAC systems
  └─ Trigger camera recordings on alerts
           ↓
💾 DATABASES (Phase 1)
  ├─ MySQL → Building, Zone, Sensor, Alert data
  ├─ MongoDB → Raw sensor readings
  └─ Redis → Caching + task queue
```

**Document mapping**:
- Phone cameras → **PHONE_CAMERA_SETUP.md**, **PHONE_CAMERA_QUICK_REFERENCE.md**
- MediaMTX config → **PHONE_CAMERA_SETUP.md** §7
- Django API → **SMART_BUILDING_PHASE2.md**
- Celery logic → **SMART_BUILDING_PHASE2.md** §3
- Database models → **SMART_BUILDING_PHASE1.md**

---

## 🎯 Next Steps

After completing all guides:

1. ✅ **Phase 1**: Database ready with 4 zones
2. ✅ **Phase 2**: Backend API + HVAC control working
3. ✅ **Phone Cameras**: Real cameras streaming
4. ⏳ **Phase 3**: React frontend dashboard (Coming next!)

**Ready for Phase 3?**
- Real-time zone monitoring dashboard
- Live camera video feeds
- Interactive HVAC controls
- Alert notifications with acknowledge
- Energy consumption charts
- Floor plan visualization

Stay tuned! 🚀

---

## 📄 Document Index

- `SMART_BUILDING_PHASE1.md` - Database setup (7 models)
- `SMART_BUILDING_PHASE2.md` - Backend API + Celery
- `PHONE_CAMERA_SETUP.md` - Complete phone camera guide
- `PHONE_CAMERA_QUICK_REFERENCE.md` - Quick commands & troubleshooting
- `README.md` - This file (documentation index)

**Last Updated**: October 20, 2025
