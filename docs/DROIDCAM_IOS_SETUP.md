# 📱 DroidCam OBS on iOS - Complete Setup Guide

## 🎯 Overview

Hướng dẫn chi tiết cách biến **iPhone thành camera IP** cho Smart Building system sử dụng **DroidCam OBS**.

---

## ⏱️ Time Required: 10 minutes

---

## 📋 Requirements

### Hardware
- ✅ iPhone (iOS 13.0 or later)
- ✅ PC running Smart Building system
- ✅ Both connected to **SAME WiFi network**
- ✅ Lightning cable (for charging)

### Software
- ✅ DroidCam OBS app (FREE on App Store)
- ✅ Smart Building system running (Docker containers up)
- ✅ MediaMTX container active

---

## 🚀 Step-by-Step Setup

### Step 1: Install DroidCam OBS (2 minutes)

1. Open **App Store** on iPhone
2. Search: **"DroidCam OBS"** (by Dev47Apps)
3. Tap **Get** → Install (FREE)
4. Open app after installation

**Note**: DroidCam OBS is the iOS version. Don't confuse with regular DroidCam (Android only).

---

### Step 2: Configure DroidCam OBS (1 minute)

1. **Open DroidCam OBS** on iPhone
2. **Grant permissions**:
   - Camera access → **Allow**
   - Microphone access → **Allow** (optional)
   - Local network → **Allow**

3. **App will show**:
   ```
   WiFi IP: 192.168.1.110  ← YOUR IPHONE IP
   Port: 4747              ← FIXED PORT
   Status: Waiting...
   ```

4. **Important**: Note down your **WiFi IP** (e.g., `192.168.1.110`)

---

### Step 3: Check iPhone IP Address (30 seconds)

**Method 1: From DroidCam OBS app**
- Look at app screen → "WiFi IP: X.X.X.X"

**Method 2: From iPhone Settings**
1. Settings → WiFi
2. Tap the (i) icon next to connected WiFi
3. Look at "IP Address"

**Example**: `192.168.1.110`

---

### Step 4: Verify Same WiFi Network (30 seconds)

**iPhone**:
- Settings → WiFi → Connected to: "MyHomeWiFi"

**PC**:
```powershell
# Check PC WiFi
ipconfig | Select-String "IPv4"
```

**Both should be in same subnet** (e.g., `192.168.1.X`)

---

### Step 5: Test Connection from PC (1 minute)

⚠️ **IMPORTANT**: Replace `192.168.1.110` with YOUR iPhone's actual IP!

```powershell
# Run test script
docker exec iot-app python scripts/test_droidcam_ios.py 192.168.1.110
```

**Expected Output** (if successful):
```
🔍 Testing DroidCam OBS (iOS) connection...
   URL: rtsp://192.168.1.110:4747/video
   This will take 5-10 seconds...

✅ DroidCam OBS stream is accessible!

📊 Stream Info:
width=1280
height=720
codec_name=h264
r_frame_rate=30/1

🎉 iPhone camera is ready!

📝 Next step: Update database with this iPhone IP
   Run: docker exec iot-app python scripts/update_phone_camera.py "Main Lobby" 192.168.1.110 4747 droidcam
```

---

### Step 6: Update Database (1 minute)

Choose which zone to assign this iPhone camera:

**Option A: Main Lobby** (Entrance monitoring)
```powershell
docker exec iot-app python scripts/update_phone_camera.py "Main Lobby" 192.168.1.110 4747 droidcam
```

**Option B: Server Room** (Critical monitoring)
```powershell
docker exec iot-app python scripts/update_phone_camera.py "Server Room" 192.168.1.110 4747 droidcam
```

**Option C: Office Floor 5** (General monitoring)
```powershell
docker exec iot-app python scripts/update_phone_camera.py "Office Floor 5" 192.168.1.110 4747 droidcam
```

**Option D: Parking Lot**
```powershell
docker exec iot-app python scripts/update_phone_camera.py "Parking Lot" 192.168.1.110 4747 droidcam
```

**Expected Output**:
```
======================================================================
✅ Camera Updated Successfully!
======================================================================

📍 Zone: Main Lobby (Floor 1)
📹 Camera: Main Lobby Camera

🔗 URLs:
   RTSP (input):  rtsp://192.168.1.110:4747/video
   HLS (output):  http://localhost:8889/lobby_main/index.m3u8
   WebRTC:        http://localhost:8889/lobby_main

📝 MediaMTX Path: lobby_main

⚙️  Old RTSP: rtsp://admin:password@192.168.1.101:554/stream1
```

---

### Step 7: Restart MediaMTX (30 seconds)

```powershell
# Restart to apply changes
docker-compose restart mediamtx

# Wait for startup
timeout 10

# Check logs
docker logs iot-mediamtx --tail 20
```

**Look for**:
```
[RTSP] [path lobby_main] source ready
[HLS] [path lobby_main] stream ready
```

✅ This means iPhone camera is connected!

---

### Step 8: Test Live Stream (30 seconds)

**Method 1: Browser**
```powershell
Start-Process "http://localhost:8889/lobby_main/"
```

You should see:
- 🎥 Live video from iPhone
- ▶️ Play button
- 📊 Stream info (resolution, FPS)

**Method 2: VLC Player** (if installed)
```powershell
Start-Process "vlc://rtsp://192.168.1.110:4747/video"
```

**Method 3: API**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/zones/1/status/" -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json | Select-Object -ExpandProperty cameras
```

Should return:
```json
{
  "hls_url": "http://localhost:8889/lobby_main/index.m3u8",
  "rtsp_url": "rtsp://192.168.1.110:4747/video",
  "name": "Main Lobby Camera"
}
```

---

## ✅ Success Checklist

After completing setup:

- [ ] DroidCam OBS app running on iPhone
- [ ] App shows "WiFi IP" and camera preview
- [ ] Test script shows "✅ DroidCam OBS stream is accessible"
- [ ] Database updated with iPhone IP
- [ ] MediaMTX restarted successfully
- [ ] MediaMTX logs show "source ready"
- [ ] Browser shows live video at http://localhost:8889/lobby_main/
- [ ] Stream stable for 5+ minutes

---

## 🔍 Troubleshooting

### ❌ Problem 1: "Cannot access DroidCam OBS stream"

**Symptoms**: Test script fails with connection error

**Solutions**:

1. **Check iPhone WiFi**:
   ```powershell
   ping 192.168.1.110
   ```
   - If ping fails → iPhone not on same network
   - Check iPhone Settings → WiFi

2. **Check DroidCam OBS app**:
   - Is app open and showing camera?
   - Does it show "WiFi IP: X.X.X.X"?
   - Try closing and reopening app

3. **Check PC firewall**:
   ```powershell
   Test-NetConnection -ComputerName 192.168.1.110 -Port 4747
   ```
   - If fails → Firewall blocking
   - Temporarily disable firewall to test

4. **Check IP changed**:
   - iPhone IP can change when reconnecting WiFi
   - Check app again for current IP
   - Re-run test with new IP

---

### ❌ Problem 2: "Stream shows black screen"

**Solutions**:

1. **Check app permissions**:
   - iPhone Settings → DroidCam OBS
   - Camera → **Enabled**
   - Local Network → **Enabled**

2. **Restart app**:
   - Close DroidCam OBS completely
   - Reopen app
   - Camera preview should appear

3. **Check camera in use**:
   - Close other apps using camera
   - FaceTime, Instagram, etc.

---

### ❌ Problem 3: "Stream is laggy/choppy"

**Solutions**:

1. **Check WiFi signal**:
   - iPhone should be near router (3+ bars)
   - Move iPhone closer to router
   - Use 5GHz WiFi if available

2. **Reduce quality** (DroidCam OBS app):
   - Settings → Video Quality → **Medium** or **Low**
   - Resolution → **640x480** (saves bandwidth)
   - FPS → **15-20** (lower = smoother on slow WiFi)

3. **Close other WiFi apps**:
   - Stop streaming on other devices
   - Pause downloads/uploads

---

### ❌ Problem 4: "iPhone IP keeps changing"

**Solutions**:

1. **Reserve IP in Router** (Recommended):
   - Login to router admin (e.g., 192.168.1.1)
   - Find "DHCP Reservation" or "Static IP"
   - Assign fixed IP to iPhone's MAC address
   - Example: Always assign 192.168.1.110 to this iPhone

2. **Quick Update Script**:
   ```powershell
   # When IP changes, just run update again
   docker exec iot-app python scripts/update_phone_camera.py "Main Lobby" <NEW_IP> 4747 droidcam
   docker-compose restart mediamtx
   ```

---

### ❌ Problem 5: "MediaMTX not connecting to iPhone"

**Check MediaMTX logs**:
```powershell
docker logs iot-mediamtx --tail 50 | Select-String "error"
```

**Common errors**:

1. **"connection refused"**:
   - iPhone app not running
   - Wrong IP address
   - Firewall blocking port 4747

2. **"timeout"**:
   - iPhone on different WiFi
   - Poor WiFi signal
   - iPhone in sleep mode

3. **"no video track"**:
   - Camera permission denied
   - App glitch → Restart app

**Fix**: Restart MediaMTX after fixing issue
```powershell
docker-compose restart mediamtx
```

---

## 📊 DroidCam OBS Settings

### Recommended Settings

**Video Quality**:
- Resolution: **1280x720** (HD) or **640x480** (Save bandwidth)
- FPS: **30** (Smooth) or **15** (Stable)
- Bitrate: Auto

**Connection**:
- Mode: **WiFi** (not USB)
- Port: **4747** (fixed)

**Advanced**:
- Mirror video: OFF (unless camera is front-facing)
- Auto-focus: ON
- Exposure: Auto

---

## 🔋 Battery & Power Management

### For 24/7 Operation

**1. Keep iPhone Plugged In** ⚡
- Use Lightning cable + power adapter
- iPhone will charge while streaming
- Battery won't drain

**2. Optimize Settings**:
```
iPhone Settings:
  → Display & Brightness
    → Auto-Lock: Never
  
  → Battery
    → Low Power Mode: OFF
    
  → DroidCam OBS (in app settings)
    → Keep Screen On: Optional (uses more power)
    → Background Mode: Not available on iOS
```

**3. Monitor Temperature**:
- iPhone may get warm during long streaming
- Ensure good ventilation
- Don't cover iPhone with case if gets hot
- Place near fan if necessary

---

## 🎯 Integration with Smart Building

### When Alert Triggers

**Scenario**: Temperature in Main Lobby exceeds threshold

1. **Sensor detects**: Temp = 27.5°C (max: 26°C)
2. **Celery creates alert**: BuildingAlert severity=WARNING
3. **Camera recording triggered**: iPhone camera at Main Lobby
4. **Recording saved**: `/recordings/lobby_main/1_20251020_150030.mp4`
5. **Dashboard shows**: 
   - 🔴 Alert badge on Main Lobby zone
   - 📹 Camera feed highlighted
   - 🎥 Recording available for playback

### API Integration

**Get iPhone camera stream URL**:
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/zones/1/status/" -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

**Response includes**:
```json
{
  "cameras": [
    {
      "name": "Main Lobby Camera",
      "hls_url": "http://localhost:8889/lobby_main/index.m3u8",
      "webrtc_url": "http://localhost:8889/lobby_main",
      "rtsp_url": "rtsp://192.168.1.110:4747/video"
    }
  ]
}
```

---

## 💡 Pro Tips

### 1. Mounting iPhone as Fixed Camera

**Options**:
- 🔹 iPhone tripod mount ($10-20)
- 🔹 Suction cup car mount
- 🔹 3M Command strips + phone holder
- 🔹 Desktop phone stand with adjustable angle

**Positioning**:
- ✅ Angle for best view of monitored area
- ✅ Avoid direct sunlight (causes glare)
- ✅ Near power outlet for charging
- ✅ Good WiFi signal (3+ bars)

### 2. Multiple iPhones Setup

**Example: 2 iPhones for dual coverage**

iPhone 1 (Main Lobby):
```powershell
docker exec iot-app python scripts/update_phone_camera.py "Main Lobby" 192.168.1.110 4747 droidcam
```

iPhone 2 (Server Room):
```powershell
docker exec iot-app python scripts/update_phone_camera.py "Server Room" 192.168.1.111 4747 droidcam
```

Then:
```powershell
docker-compose restart mediamtx
```

Both streams available:
- http://localhost:8889/lobby_main/
- http://localhost:8889/server_room/

### 3. WiFi Optimization

**5GHz vs 2.4GHz**:
- ✅ Use 5GHz if available (less interference, faster)
- ⚠️ 2.4GHz has better range but slower

**Router Settings**:
- Enable QoS (Quality of Service) for iPhone IP
- Reserve bandwidth for camera streaming
- Assign fixed IP (DHCP reservation)

### 4. Testing Stability

**24-hour test**:
```powershell
# Start streaming
# Check after 1 hour, 6 hours, 24 hours

# Check if still streaming
docker logs iot-mediamtx --tail 10 | Select-String "lobby_main"

# Should show recent activity
```

**If connection drops**:
- Check MediaMTX logs
- Check iPhone didn't go to sleep
- Check WiFi didn't disconnect
- Check app is still running

---

## 🆚 DroidCam OBS vs IP Webcam

| Feature | DroidCam OBS (iOS) | IP Webcam (Android) |
|---------|-------------------|---------------------|
| **Platform** | iOS only | Android only |
| **Price** | FREE | FREE |
| **Port** | 4747 (fixed) | 8080 (changeable) |
| **Quality** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Stability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Features** | Basic | Advanced |
| **Battery Use** | Medium | Medium |
| **Setup Ease** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**Recommendation**: 
- iOS → Use DroidCam OBS ✅
- Android → Use IP Webcam ✅

---

## 📞 Quick Commands Reference

```powershell
# Test iPhone connection
docker exec iot-app python scripts/test_droidcam_ios.py <IPHONE_IP>

# Update database
docker exec iot-app python scripts/update_phone_camera.py "<ZONE_NAME>" <IPHONE_IP> 4747 droidcam

# Restart MediaMTX
docker-compose restart mediamtx

# Check MediaMTX logs
docker logs iot-mediamtx --tail 20

# Test stream in browser
Start-Process "http://localhost:8889/lobby_main/"

# Check API
Invoke-WebRequest -Uri "http://localhost:8000/api/zones/1/status/" -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

---

## 🎯 Next Steps

After iPhone camera is working:

1. **Add more zones**: Repeat process for other zones
2. **Test alerts**: Trigger temperature alert to test recording
3. **Build dashboard**: React frontend with live camera feeds
4. **Monitor performance**: Check stream stability over 24 hours

---

## 📚 Related Documentation

- [Main Phone Camera Setup Guide](./PHONE_CAMERA_SETUP.md)
- [Quick Reference Card](./PHONE_CAMERA_QUICK_REFERENCE.md)
- [Smart Building Phase 2](./SMART_BUILDING_PHASE2.md)

---

## ✅ Summary

**What you've accomplished**:
- 📱 iPhone converted to IP camera using DroidCam OBS
- 🎥 RTSP stream: `rtsp://192.168.1.110:4747/video`
- 🌐 HLS stream: `http://localhost:8889/lobby_main/index.m3u8`
- 🔗 Integrated with Smart Building system
- 🚀 Ready for dashboard integration

**Stream quality**:
- Resolution: 1280x720 (HD) or 640x480 (VGA)
- FPS: 30 or 15
- Codec: H.264
- Latency: ~2-4 seconds (HLS)

**Cost**: **$0** - Free app, repurpose old iPhone! 🎉

---

Need help? Run:
```powershell
docker logs iot-mediamtx --tail 50  # Check streaming
docker logs iot-app --tail 50       # Check API
```

**Happy streaming!** 📹🎉
