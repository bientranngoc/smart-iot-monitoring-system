# 📱 iVCam Setup Guide - iOS Camera for Smart Building

Complete guide to use iPhone as security camera using **iVCam**.

---

## 📋 Overview

**iVCam** creates a **virtual webcam** on your PC that uses your iPhone camera. This is easier than RTSP streaming for iOS devices.

### ✅ Advantages
- ✅ Easy setup (app + PC client)
- ✅ Works reliably on iOS
- ✅ Free to use (with ads)
- ✅ Good video quality
- ✅ Stable connection

### ⚠️ Requirements
- iPhone with iOS 11+
- Windows PC (same WiFi network)
- 200MB free space

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install iVCam App on iPhone

1. Open **App Store** on iPhone
2. Search: **"iVCam Webcam"**
3. Install app by **e2eSoft**
4. Open app (allow Camera & Network permissions)

### Step 2: Install iVCam Client on Windows PC

1. Download from: https://www.e2esoft.com/ivcam/
2. Or direct link: https://www.e2esoft.com/files/iVCamSetup_v7.4.exe
3. Run installer (Next → Next → Install)
4. Launch **iVCam** application on PC

### Step 3: Connect iPhone to PC

1. **Ensure iPhone and PC on same WiFi network**
2. Open iVCam app on **iPhone**
3. Open iVCam application on **PC**
4. **Auto-connect**: PC will detect iPhone automatically
5. ✅ You'll see iPhone camera feed in PC app!

---

## 🎥 Use with MediaMTX (Smart Building Project)

After iVCam connects, iPhone becomes a **virtual webcam** on Windows. We'll stream this to MediaMTX.

### Option A: Stream via FFmpeg (Recommended)

**1. Check virtual webcam name:**

```powershell
ffmpeg -list_devices true -f dshow -i dummy
```

Look for: `e2eSoft iVCam` in the output.

**2. Update MediaMTX config:**

Edit `infra/mediamtx/mediamtx.yml`:

```yaml
paths:
  lobby_main:
    # Run FFmpeg to capture iVCam virtual webcam
    runOnInit: >
      ffmpeg -f dshow -i video="e2eSoft iVCam"
      -c:v libx264 -preset ultrafast -tune zerolatency
      -b:v 2000k -maxrate 2500k -bufsize 5000k
      -g 50 -keyint_min 25
      -f rtsp rtsp://localhost:$RTSP_PORT/$MTX_PATH
    runOnInitRestart: yes
```

**3. Restart MediaMTX:**

```powershell
docker-compose restart mediamtx
```

**4. Open stream in browser:**

```powershell
Start-Process "http://localhost:8889/lobby_main/"
```

✅ You should see live video from iPhone!

---

## 🔧 Advanced Configuration

### High Quality Settings

For better video quality (1080p, 30fps):

```yaml
paths:
  lobby_main:
    runOnInit: >
      ffmpeg -f dshow -video_size 1920x1080 -framerate 30
      -i video="e2eSoft iVCam"
      -c:v libx264 -preset medium -tune zerolatency
      -b:v 4000k -maxrate 5000k -bufsize 10000k
      -pix_fmt yuv420p -g 60
      -f rtsp rtsp://localhost:$RTSP_PORT/$MTX_PATH
    runOnInitRestart: yes
```

### Low Latency Settings

For minimal delay (surveillance use):

```yaml
paths:
  lobby_main:
    runOnInit: >
      ffmpeg -f dshow -rtbufsize 100M -i video="e2eSoft iVCam"
      -c:v libx264 -preset ultrafast -tune zerolatency
      -b:v 1500k -maxrate 2000k -bufsize 3000k
      -g 30 -sc_threshold 0 -probesize 32
      -analyzeduration 0 -fflags nobuffer
      -f rtsp rtsp://localhost:$RTSP_PORT/$MTX_PATH
    runOnInitRestart: yes
```

---

## 🚨 Troubleshooting

### Issue 1: PC doesn't detect iPhone

**Symptoms:**
- iVCam PC app shows "No device found"
- iPhone app shows "Waiting for connection"

**Solutions:**

✅ **Check WiFi:**
```powershell
# On PC - Get IP
ipconfig | Select-String "IPv4"

# On iPhone - Settings → WiFi → Info (i) button
# Both must be 192.168.0.XXX or 192.168.1.XXX (same subnet)
```

✅ **Disable VPN** on both devices

✅ **Allow firewall:**
- Windows Firewall → Allow an app
- Find "iVCam" → Check both Private & Public

✅ **Restart both:**
- Close iVCam app on iPhone
- Close iVCam on PC
- Reopen PC app first, then iPhone app

---

### Issue 2: Virtual webcam not found

**Symptoms:**
```
[dshow @ ...] Could not enumerate video devices
```

**Solutions:**

✅ **Verify iVCam is connected:**
- Open iVCam PC app
- Ensure iPhone shows "Connected" status
- You should see live camera feed in PC app

✅ **Check webcam name:**
```powershell
ffmpeg -list_devices true -f dshow -i dummy 2>&1 | Select-String "iVCam"
```

If not found, try:
- `"e2eSoft iVCam"` (most common)
- `"iVCam"` (older versions)
- `"e2eSoft VCam"` (alternative name)

✅ **Test webcam directly:**
```powershell
# Open webcam in VLC to verify it works
vlc dshow:// :dshow-vdev="e2eSoft iVCam"
```

---

### Issue 3: FFmpeg stream fails

**Symptoms:**
- MediaMTX logs: "runOnInit exited with error"
- No video in browser

**Solutions:**

✅ **Test FFmpeg command manually:**
```powershell
# Run in separate PowerShell window
ffmpeg -f dshow -i video="e2eSoft iVCam" -c:v libx264 -preset ultrafast -f rtsp rtsp://localhost:8554/lobby_main
```

✅ **Check MediaMTX logs:**
```powershell
docker logs iot-mediamtx --tail 50
```

✅ **Simplify config for testing:**
```yaml
paths:
  lobby_main:
    runOnInit: ffmpeg -f dshow -i video="e2eSoft iVCam" -c:v copy -f rtsp rtsp://localhost:$RTSP_PORT/$MTX_PATH
    runOnInitRestart: yes
```

---

### Issue 4: Video lag or stuttering

**Symptoms:**
- Stream works but choppy
- High latency (5+ seconds delay)

**Solutions:**

✅ **Use WiFi 5GHz instead of 2.4GHz**

✅ **Lower resolution:**
```yaml
runOnInit: >
  ffmpeg -f dshow -video_size 1280x720 -framerate 25
  -i video="e2eSoft iVCam" ...
```

✅ **Reduce bitrate:**
```yaml
-b:v 1000k -maxrate 1500k -bufsize 3000k
```

✅ **Move closer to WiFi router**

✅ **Close other apps on iPhone** (Safari, Music, etc.)

---

## 📊 Performance Tips

### Battery Saving
- Lower resolution: 720p instead of 1080p
- Reduce framerate: 20fps instead of 30fps
- Use low power mode on iPhone (Settings → Battery)
- Connect iPhone to charger for 24/7 monitoring

### Network Optimization
- Use 5GHz WiFi band
- Assign static IP to iPhone (router settings)
- Use QoS on router (prioritize iVCam traffic)
- Reduce buffer sizes in FFmpeg

### Quality vs Latency
```yaml
# High quality (recording)
-preset medium -b:v 4000k

# Balanced
-preset fast -b:v 2000k

# Low latency (live monitoring)
-preset ultrafast -b:v 1000k -tune zerolatency
```

---

## 🔄 Alternative: Direct RTSP (Advanced)

iVCam also supports **direct RTSP streaming** (no PC client needed):

### Setup RTSP Mode

1. **Enable RTSP in iVCam app:**
   - Open iVCam on iPhone
   - Settings → Enable RTSP Server
   - Note the RTSP URL (e.g., rtsp://192.168.0.106:8080/live)

2. **Update MediaMTX config:**

```yaml
paths:
  lobby_main:
    source: rtsp://192.168.0.106:8080/live
    sourceProtocol: tcp
    sourceOnDemand: yes
```

3. **Test:**

```powershell
docker-compose restart mediamtx
Start-Process "http://localhost:8889/lobby_main/"
```

⚠️ **Note:** RTSP mode is a **paid feature** in iVCam ($9.99). Free version only supports virtual webcam mode.

---

## 📖 Compare with Other Solutions

| Feature | iVCam | DroidCam OBS | IP Webcam |
|---------|-------|--------------|-----------|
| iOS Support | ✅ Yes | ✅ Yes | ❌ Android only |
| Free Version | ✅ Yes (ads) | ✅ Yes | ✅ Yes |
| Virtual Webcam | ✅ Yes | ✅ Yes | ❌ No |
| Direct RTSP | 💰 Paid | ✅ Free | ✅ Free |
| Setup Difficulty | 🟢 Easy | 🟡 Medium | 🟢 Easy |
| Video Quality | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Latency | 🟡 Medium (1-3s) | 🟢 Low (0.5-2s) | 🟢 Low (0.5-1s) |
| Stability | 🟢 Stable | 🟢 Stable | 🟢 Very Stable |

### Recommendation

- **For iOS + Easy setup:** Use **iVCam** (this guide)
- **For iOS + Best quality:** Pay for **DroidCam OBS** ($5.99)
- **For Android:** Use **IP Webcam** (free, best features)

---

## ✅ Next Steps

After iVCam setup works:

1. **Test stability** (leave running for 1 hour)
2. **Add more cameras** (Server Room, Parking, Office zones)
3. **Create React dashboard** with live video player
4. **Setup motion detection** (optional)
5. **Configure alerts** (send snapshot when alert triggered)

---

## 🆘 Support

### iVCam Official Resources
- Website: https://www.e2esoft.com/ivcam/
- FAQ: https://www.e2esoft.com/ivcam/faq/
- Support: support@e2esoft.com

### Project Issues
If streaming doesn't work after following this guide:

1. Share MediaMTX logs:
```powershell
docker logs iot-mediamtx --tail 100 > logs.txt
```

2. Share FFmpeg output:
```powershell
ffmpeg -f dshow -list_devices true -i dummy 2>&1 > devices.txt
```

3. Check iVCam connection status in PC app

---

## 📚 Related Documents

- [PHONE_CAMERA_SETUP.md](./PHONE_CAMERA_SETUP.md) - Overview of all camera options
- [MEDIAMTX_SETUP.md](./MEDIAMTX_SETUP.md) - MediaMTX streaming server guide
- [DROIDCAM_IOS_SETUP.md](./DROIDCAM_IOS_SETUP.md) - Alternative: DroidCam OBS guide

---

**🎉 Ready to use iPhone as security camera with iVCam!**

Good luck with your Smart Building project! 🏢📹
