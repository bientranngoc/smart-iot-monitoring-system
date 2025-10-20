# 📱 Quick Reference - Phone Camera Setup

## 🚀 Quick Start (5 Minutes)

### Step 1: Install App on Phone
**Android**: [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam) (FREE)  
**iOS**: [iVCam](https://apps.apple.com/app/ivcam-webcam/id1164464478) (FREE)

### Step 2: Start Camera Server
1. Open app on phone
2. Scroll down → Tap **"Start Server"**
3. Note the IP address shown (e.g., `192.168.1.105`)

### Step 3: Test Connection
```powershell
# Replace with YOUR phone IP
docker exec iot-app python scripts/test_phone_camera.py 192.168.1.105
```

✅ If test passes → Continue to Step 4  
❌ If test fails → Check troubleshooting section

### Step 4: Update Database
```powershell
# Single camera (replace zone name and IP)
docker exec iot-app python scripts/update_phone_camera.py "Server Room" 192.168.1.105

# OR: Update all 4 cameras at once
notepad scripts\setup_all_phone_cameras.py  # Edit IPs first
docker exec iot-app python scripts/setup_all_phone_cameras.py
```

### Step 5: Restart MediaMTX
```powershell
docker-compose restart mediamtx

# Wait 10 seconds
timeout 10

# Check logs
docker logs iot-mediamtx --tail 20
```

Look for: `[RTSP] [path server_room] source ready` ✅

### Step 6: Test Stream
Open in browser: http://localhost:8889/server_room/

You should see live video from your phone! 🎉

---

## 🎯 Common Scenarios

### Scenario 1: One Phone Camera (Server Room Monitoring)
```powershell
# 1. Start IP Webcam on old Android phone
# 2. Get IP (e.g., 192.168.1.105)

# 3. Test
docker exec iot-app python scripts/test_phone_camera.py 192.168.1.105

# 4. Update
docker exec iot-app python scripts/update_phone_camera.py "Server Room" 192.168.1.105

# 5. Restart MediaMTX
docker-compose restart mediamtx

# 6. Test stream
Start-Process "http://localhost:8889/server_room/"
```

### Scenario 2: Multiple Phones (Full Building Coverage)
```powershell
# 1. Start camera apps on 4 phones/tablets
#    Phone 1 (Server Room): 192.168.1.105
#    Phone 2 (Main Lobby):  192.168.1.106
#    Phone 3 (Parking):     192.168.1.107
#    Phone 4 (Office):      192.168.1.108

# 2. Edit setup script
notepad scripts\setup_all_phone_cameras.py
# Change IPs in CAMERAS list

# 3. Run setup
docker exec iot-app python scripts/setup_all_phone_cameras.py

# 4. Restart MediaMTX
docker-compose restart mediamtx

# 5. Test all streams
Start-Process "http://localhost:8889/"
```

### Scenario 3: Replace Existing Camera
```powershell
# Phone's IP changed or want to use different phone

# 1. Get new phone IP from app

# 2. Update specific zone
docker exec iot-app python scripts/update_phone_camera.py "Main Lobby" 192.168.1.110

# 3. Restart MediaMTX
docker-compose restart mediamtx
```

---

## 🔍 Troubleshooting Commands

### Check Phone Connection
```powershell
# Test ping
ping 192.168.1.105

# Test port
Test-NetConnection -ComputerName 192.168.1.105 -Port 8080

# Open phone web UI in browser
Start-Process "http://192.168.1.105:8080"
```

### Check MediaMTX Status
```powershell
# View logs
docker logs iot-mediamtx --tail 50

# Check running status
docker ps | Select-String mediamtx

# Restart if needed
docker-compose restart mediamtx
```

### Check Database Configuration
```powershell
# View all cameras
docker exec iot-app python manage.py shell -c "from monitoring.models import ZoneCamera; [print(f'{c.zone.name}: {c.rtsp_url}') for c in ZoneCamera.objects.all()]"

# View specific zone
Invoke-WebRequest -Uri "http://localhost:8000/api/zones/2/status/" -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json | Select-Object -ExpandProperty cameras | ConvertTo-Json
```

### Test Stream with VLC
```powershell
# If you have VLC installed
Start-Process "vlc://rtsp://192.168.1.105:8080/h264_pcm.sdp"
```

---

## 📊 App Comparison

| Feature | IP Webcam (Android) | DroidCam (Android/iOS) | iVCam (iOS) |
|---------|---------------------|------------------------|-------------|
| **Price** | FREE | FREE (Pro $5) | FREE (Pro $10) |
| **Quality** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **RTSP Port** | 8080 | 4747 | Custom |
| **Battery Use** | Medium | Low | Medium |
| **Features** | Many | Basic | Advanced |
| **Stability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Recommendation** | ✅ Best for Android | OK for both | ✅ Best for iOS |

---

## ⚙️ Recommended Settings

### IP Webcam (Android)
```
Video Settings:
  Resolution: 640x480 (save bandwidth) or 1280x720 (better quality)
  Quality: 70%
  FPS: 15-20

Power Settings:
  Keep screen on: OFF (save battery)
  Prevent sleep: ON
  
Network:
  Port: 8080
  Authentication: Optional (username/password)
```

### DroidCam
```
Connection:
  WiFi mode
  Port: 4747
  
Video:
  Resolution: 640x480
  FPS: 15
```

### iVCam (iOS)
```
Video:
  Resolution: 720p
  FPS: 30
  
Connection:
  WiFi connection
  Auto-connect: ON
```

---

## 🎬 Integration with Smart Building

### When Temperature Alert Triggers

1. **Celery detects high temperature** (e.g., Server Room 28.5°C)
2. **Alert is created** in BuildingAlert table
3. **Camera recording is triggered** automatically
4. **Recording path saved**: `/recordings/server_room/1_20251020_134016.mp4`
5. **Dashboard shows**:
   - 🔴 Red alert badge on zone
   - 📹 Camera icon is highlighted
   - 🎥 Video recording available for review

### API Returns Live Camera URLs

```json
{
  "zone": "Server Room",
  "cameras": [
    {
      "name": "Server Room Camera",
      "hls_url": "http://localhost:8889/server_room/index.m3u8",
      "webrtc_url": "http://localhost:8889/server_room",
      "rtsp_url": "rtsp://192.168.1.105:8080/h264_pcm.sdp"
    }
  ]
}
```

---

## 💡 Pro Tips

### 1. Optimize Phone Battery
```
✅ Keep phone plugged in 24/7
✅ Lower screen brightness to minimum
✅ Disable cellular data (WiFi only)
✅ Close all other apps
✅ Enable "Background Mode" in camera app
```

### 2. Improve WiFi Stability
```
✅ Use WiFi 5GHz if available
✅ Place phone near router
✅ Reserve static IP for phone in router settings
✅ Disable WiFi power saving on phone
```

### 3. Mounting Phone as Fixed Camera
```
✅ Use cheap phone tripod ($5-10)
✅ Or: 3M Command strips + phone holder
✅ Or: Desktop phone stand
✅ Position for best viewing angle
✅ Ensure power cable reaches outlet
```

### 4. Multi-Zone Coverage Strategy
```
Priority 1 (Critical): Server Room
  → Use best/newest phone
  → Highest resolution (720p+)
  → 24/7 monitoring essential

Priority 2 (High): Main Entrance/Lobby  
  → Use second-best phone
  → Medium resolution (640x480)
  → Business hours focus

Priority 3 (Medium): Parking Lot
  → Use older phone/tablet
  → Lower resolution OK
  → Motion detection mode

Priority 4 (Low): Office areas
  → Use cheapest device
  → Lower FPS (10-15)
  → Recording on-demand only
```

---

## 🚨 Emergency Procedures

### Phone Lost Connection
```powershell
# 1. Check phone is still powered on
# 2. Restart camera app
# 3. Check WiFi connection
# 4. Restart MediaMTX
docker-compose restart mediamtx
```

### Phone IP Changed
```powershell
# 1. Get new IP from camera app
# 2. Update database
docker exec iot-app python scripts/update_phone_camera.py "Server Room" <NEW_IP>
# 3. Restart MediaMTX
docker-compose restart mediamtx
```

### All Cameras Down
```powershell
# 1. Check WiFi router
# 2. Check MediaMTX
docker logs iot-mediamtx --tail 50
docker-compose restart mediamtx

# 3. Check each phone manually
# 4. Re-run setup if needed
docker exec iot-app python scripts/setup_all_phone_cameras.py
```

---

## 📞 Support Commands

```powershell
# View this guide
notepad docs\PHONE_CAMERA_QUICK_REFERENCE.md

# Full setup guide
notepad docs\PHONE_CAMERA_SETUP.md

# List all scripts
ls scripts\*phone*.py

# Docker status
docker-compose ps

# Full system restart
docker-compose restart
```

---

## ✅ Checklist Before Going Live

### Hardware
- [ ] All phones charged and plugged in
- [ ] Phones mounted securely
- [ ] Power cables secured (not tripping hazard)
- [ ] Phone positioned for optimal view
- [ ] WiFi signal strong (3+ bars)

### Software  
- [ ] Camera app installed and configured
- [ ] Server running on each phone
- [ ] IP addresses noted down
- [ ] Database updated with phone IPs
- [ ] MediaMTX restarted
- [ ] All streams tested in browser

### Testing
- [ ] Each stream shows live video
- [ ] Temperature alert triggers camera recording
- [ ] Dashboard displays camera feeds
- [ ] API returns correct camera URLs
- [ ] Streams stable for 1+ hour

### Documentation
- [ ] Phone IPs documented
- [ ] Zone assignments documented
- [ ] Login credentials (if any) saved
- [ ] Troubleshooting contact info ready

---

**Ready to go live!** 🚀

Need help? Check logs:
```powershell
docker logs iot-mediamtx --tail 50  # MediaMTX
docker logs iot-app --tail 50       # Django API
docker logs iot-celery --tail 50    # Alert processing
```
