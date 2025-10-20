# 📱 Hướng Dẫn Kết Nối Camera Điện Thoại vào Smart Building System

## 🎯 Tổng Quan

Thay vì dùng camera giả lập, bạn có thể biến **điện thoại thành camera IP** để giám sát thực tế trong Smart Building system. Guide này hướng dẫn từng bước cách kết nối.

---

## 📋 Yêu Cầu

### Phần Cứng
- ✅ Điện thoại Android hoặc iOS
- ✅ Máy tính chạy Smart Building system
- ✅ Cả 2 thiết bị kết nối **cùng mạng WiFi**

### Phần Mềm
- ✅ Docker Desktop đang chạy
- ✅ Smart Building system đã setup (Phase 1 & 2)
- ✅ MediaMTX container đang chạy

---

## 🔧 Phương Pháp 1: Dùng IP Webcam (Android) - KHUYẾN NGHỊ ⭐

### Bước 1: Cài Đặt App

1. Mở **Google Play Store**
2. Tìm và cài đặt **"IP Webcam"** by Pavel Khlebovich
3. Mở app sau khi cài xong

### Bước 2: Cấu Hình App

1. **Video Settings**:
   - Resolution: `640x480` (tiết kiệm băng thông) hoặc `1280x720` (HD)
   - Quality: `70-80%`
   - Frame rate: `15-30 FPS`

2. **Connection Settings**:
   - Port: `8080` (default)
   - Username: `admin` (tùy chọn)
   - Password: `admin123` (tùy chọn)

3. **Scroll xuống cuối** và nhấn **"Start Server"**

### Bước 3: Lấy IP Address

App sẽ hiển thị URL dạng:
```
http://192.168.1.XXX:8080
```

**Ví dụ thực tế**: `http://192.168.1.105:8080`

### Bước 4: Test Stream

Mở browser trên máy tính, truy cập:
```
http://192.168.1.105:8080
```

Bạn sẽ thấy giao diện web với:
- ✅ Live video preview
- ✅ Audio controls
- ✅ Video settings
- ✅ RTSP URL: `rtsp://192.168.1.105:8080/h264_pcm.sdp`

### Bước 5: Kết Nối với MediaMTX

#### 5.1. Kiểm tra MediaMTX đang chạy:

```powershell
docker ps | Select-String mediamtx
```

Kết quả mong đợi:
```
iot-mediamtx   Up 2 hours   0.0.0.0:8889->8889/tcp
```

#### 5.2. Tạo script test kết nối:

**File: `scripts/test_phone_camera.py`**

```python
#!/usr/bin/env python
"""
Test phone camera connection with MediaMTX
"""
import requests
import subprocess
import time

def test_phone_rtsp(phone_ip, phone_port=8080):
    """Test if phone RTSP stream is accessible"""
    rtsp_url = f"rtsp://{phone_ip}:{phone_port}/h264_pcm.sdp"
    
    print(f"🔍 Testing RTSP stream: {rtsp_url}")
    
    # Use ffprobe to check stream
    cmd = [
        'docker', 'exec', 'iot-mediamtx',
        'ffprobe', 
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,codec_name',
        '-of', 'default=noprint_wrappers=1',
        rtsp_url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Phone camera stream is accessible!")
            print(f"   Stream info:\n{result.stdout}")
            return True
        else:
            print("❌ Cannot access phone camera stream")
            print(f"   Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⏱️  Timeout - check if phone and PC are on same WiFi")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    # THAY ĐỔI IP NÀY THEO ĐIỆN THOẠI CỦA BẠN
    phone_ip = "192.168.1.105"  # ⚠️ Change this!
    
    test_phone_rtsp(phone_ip)
```

#### 5.3. Chạy test:

```powershell
docker exec iot-app python scripts/test_phone_camera.py
```

### Bước 6: Cập Nhật Database

#### 6.1. Tạo script update camera:

**File: `scripts/update_phone_camera.py`**

```python
#!/usr/bin/env python
"""
Update ZoneCamera with real phone camera URL
"""
import os
import sys
import django

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_iot.settings')
django.setup()

from monitoring.models import ZoneCamera

def update_camera_for_zone(zone_name, phone_ip, phone_port=8080, username='', password=''):
    """
    Update camera RTSP URL for a specific zone
    
    Args:
        zone_name: Tên zone (VD: "Server Room", "Main Lobby")
        phone_ip: IP của điện thoại (VD: "192.168.1.105")
        phone_port: Port của IP Webcam app (default: 8080)
        username: Username nếu đã set trong app (optional)
        password: Password nếu đã set trong app (optional)
    """
    try:
        # Tìm camera của zone
        camera = ZoneCamera.objects.filter(zone__name=zone_name).first()
        
        if not camera:
            print(f"❌ Không tìm thấy camera cho zone: {zone_name}")
            print(f"   Các zone có sẵn:")
            for cam in ZoneCamera.objects.all():
                print(f"   - {cam.zone.name}")
            return False
        
        # Build RTSP URL
        if username and password:
            rtsp_url = f"rtsp://{username}:{password}@{phone_ip}:{phone_port}/h264_pcm.sdp"
        else:
            rtsp_url = f"rtsp://{phone_ip}:{phone_port}/h264_pcm.sdp"
        
        # Update camera
        old_url = camera.rtsp_url
        camera.rtsp_url = rtsp_url
        camera.save()
        
        print(f"✅ Camera updated successfully!")
        print(f"   Zone: {zone_name}")
        print(f"   Old RTSP: {old_url}")
        print(f"   New RTSP: {rtsp_url}")
        print(f"   MediaMTX path: {camera.mediamtx_path}")
        print(f"   HLS URL: {camera.hls_url}")
        print(f"   WebRTC URL: {camera.webrtc_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    # ⚠️ THAY ĐỔI CÁC THÔNG SỐ NÀY
    ZONE_NAME = "Server Room"  # Chọn: "Server Room", "Main Lobby", "Parking Lot", "Office Floor 5"
    PHONE_IP = "192.168.1.105"  # IP của điện thoại
    USERNAME = ""  # Để trống nếu không dùng auth
    PASSWORD = ""  # Để trống nếu không dùng auth
    
    update_camera_for_zone(ZONE_NAME, PHONE_IP, username=USERNAME, password=PASSWORD)
```

#### 6.2. Sửa IP và chạy:

```powershell
# Mở file và sửa PHONE_IP
notepad scripts\update_phone_camera.py

# Chạy update
docker exec iot-app python scripts/update_phone_camera.py
```

### Bước 7: Cấu Hình MediaMTX Ingestion

#### 7.1. Cập nhật mediamtx.yml:

**File: `infra/mediamtx/mediamtx.yml`** (thêm vào cuối file)

```yaml
# Real phone camera streams
paths:
  server_room:
    runOnInit: ffmpeg -rtsp_transport tcp -i rtsp://192.168.1.105:8080/h264_pcm.sdp -c copy -f rtsp rtsp://localhost:$RTSP_PORT/server_room
    runOnInitRestart: yes
  
  lobby_main:
    runOnInit: ffmpeg -rtsp_transport tcp -i rtsp://192.168.1.106:8080/h264_pcm.sdp -c copy -f rtsp rtsp://localhost:$RTSP_PORT/lobby_main
    runOnInitRestart: yes
```

**Giải thích**:
- `runOnInit`: Tự động pull RTSP từ phone khi MediaMTX khởi động
- `runOnInitRestart: yes`: Tự động restart nếu connection bị mất
- Thay `192.168.1.105` bằng IP điện thoại của bạn

#### 7.2. Restart MediaMTX:

```powershell
docker-compose restart mediamtx
```

#### 7.3. Kiểm tra logs:

```powershell
docker logs iot-mediamtx --tail 20
```

Bạn sẽ thấy:
```
[RTSP] [path server_room] source ready
[HLS] [path server_room] stream ready
```

### Bước 8: Test Trên Dashboard

#### 8.1. Check API:

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/zones/2/status/" -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json | Select-Object -ExpandProperty cameras | ConvertTo-Json
```

Kết quả:
```json
{
  "hls_url": "http://localhost:8889/server_room/index.m3u8",
  "rtsp_url": "rtsp://192.168.1.105:8080/h264_pcm.sdp",
  "name": "Server Room Camera"
}
```

#### 8.2. Test HLS stream trong browser:

Mở: `http://localhost:8889/server_room/`

Bạn sẽ thấy video player với live stream từ điện thoại! 📹

---

## 🔧 Phương Pháp 2: Dùng DroidCam (iOS & Android)

### Bước 1: Cài App

**Android**: [DroidCam](https://play.google.com/store/apps/details?id=com.dev47apps.droidcam)  
**iOS**: [DroidCam OBS](https://apps.apple.com/app/droidcam-obs/id1510258102)

### Bước 2: Cấu Hình

1. Mở app
2. Chọn **WiFi IP** mode
3. Note lại IP hiển thị (VD: `192.168.1.107`)
4. Port mặc định: `4747`

### Bước 3: RTSP URL

```
rtsp://192.168.1.107:4747/video
```

### Bước 4: Update Database

Giống Phương Pháp 1, Bước 6, nhưng dùng:

```python
PHONE_IP = "192.168.1.107"
RTSP_URL = f"rtsp://{PHONE_IP}:4747/video"
```

---

## 🔧 Phương Pháp 3: Dùng iVCam (iOS - Chất Lượng Cao)

### Bước 1: Cài App

**iOS**: [iVCam](https://apps.apple.com/app/ivcam-webcam/id1164464478)  
**Windows**: Cài [iVCam Client](https://www.e2esoft.com/ivcam/)

### Bước 2: Kết Nối

1. Mở app trên iPhone
2. Mở iVCam client trên Windows
3. Auto detect và kết nối qua WiFi

### Bước 3: Virtual Camera

iVCam tạo **Virtual Webcam** trên Windows:
- Tên: `e2eSoft iVCam`
- Có thể dùng với OBS, ffmpeg, MediaMTX

### Bước 4: Capture với ffmpeg

```powershell
# Test capture
docker exec iot-mediamtx ffmpeg -f dshow -i video="e2eSoft iVCam" -f rtsp rtsp://localhost:8554/iphone_camera
```

---

## 🎯 Kịch Bản Thực Tế: 4 Điện Thoại = 4 Cameras

### Setup Hoàn Chỉnh

| Zone | Phone | IP | App | Mục Đích |
|------|-------|-----|-----|----------|
| **Server Room** | Android cũ #1 | 192.168.1.105 | IP Webcam | Giám sát nhiệt độ server rack 24/7 |
| **Main Lobby** | iPhone cũ | 192.168.1.106 | iVCam | Camera entrance, nhận diện người vào |
| **Parking Lot** | Android cũ #2 | 192.168.1.107 | DroidCam | Giám sát bãi xe |
| **Office Floor 5** | Tablet Android | 192.168.1.108 | IP Webcam | Giám sát văn phòng |

### Script Auto-Update Tất Cả

**File: `scripts/setup_all_phone_cameras.py`**

```python
#!/usr/bin/env python
"""
Setup all phone cameras at once
"""
import os
import sys
import django

sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_iot.settings')
django.setup()

from monitoring.models import ZoneCamera

# Phone camera configuration
CAMERAS = [
    {
        'zone': 'Server Room',
        'ip': '192.168.1.105',
        'port': 8080,
        'type': 'ip_webcam'
    },
    {
        'zone': 'Main Lobby',
        'ip': '192.168.1.106',
        'port': 8080,
        'type': 'ip_webcam'
    },
    {
        'zone': 'Parking Lot',
        'ip': '192.168.1.107',
        'port': 4747,
        'type': 'droidcam'
    },
    {
        'zone': 'Office Floor 5',
        'ip': '192.168.1.108',
        'port': 8080,
        'type': 'ip_webcam'
    }
]

def get_rtsp_url(config):
    """Generate RTSP URL based on app type"""
    ip = config['ip']
    port = config['port']
    app_type = config['type']
    
    if app_type == 'ip_webcam':
        return f"rtsp://{ip}:{port}/h264_pcm.sdp"
    elif app_type == 'droidcam':
        return f"rtsp://{ip}:{port}/video"
    else:
        return f"rtsp://{ip}:{port}/stream"

def setup_all_cameras():
    """Update all cameras with phone IPs"""
    print("🚀 Setting up all phone cameras...\n")
    
    for config in CAMERAS:
        try:
            camera = ZoneCamera.objects.filter(zone__name=config['zone']).first()
            
            if not camera:
                print(f"❌ Camera not found for zone: {config['zone']}")
                continue
            
            rtsp_url = get_rtsp_url(config)
            camera.rtsp_url = rtsp_url
            camera.save()
            
            print(f"✅ {config['zone']}")
            print(f"   IP: {config['ip']}:{config['port']}")
            print(f"   RTSP: {rtsp_url}")
            print(f"   HLS: {camera.hls_url}\n")
            
        except Exception as e:
            print(f"❌ Error updating {config['zone']}: {e}\n")
    
    print("=" * 60)
    print("📋 NEXT STEPS:")
    print("1. Make sure all phones are running camera apps")
    print("2. Restart MediaMTX: docker-compose restart mediamtx")
    print("3. Test streams: http://localhost:8889/")
    print("=" * 60)

if __name__ == '__main__':
    setup_all_cameras()
```

### Chạy Setup:

```powershell
# 1. Sửa IP addresses trong script
notepad scripts\setup_all_phone_cameras.py

# 2. Chạy setup
docker exec iot-app python scripts/setup_all_phone_cameras.py

# 3. Restart MediaMTX
docker-compose restart mediamtx

# 4. Test tất cả streams
Start-Process "http://localhost:8889/"
```

---

## 🔍 Troubleshooting

### ❌ Vấn Đề 1: Không Thấy Stream

**Triệu chứng**: MediaMTX logs show "connection refused"

**Giải pháp**:
```powershell
# Check phone có cùng mạng không
ping 192.168.1.105

# Check port có mở không
Test-NetConnection -ComputerName 192.168.1.105 -Port 8080

# Check firewall trên phone (tắt tạm)
```

### ❌ Vấn Đề 2: Stream Giật, Lag

**Giải pháp**:
1. Giảm resolution xuống `640x480`
2. Giảm FPS xuống `15`
3. Giảm quality xuống `50-60%`
4. Check WiFi signal strength

### ❌ Vấn Đề 3: Connection Bị Drop

**Giải pháp**:

**Trong IP Webcam app**:
- Settings → Power Management → **Disable Battery Optimization**
- Settings → Keep Screen On → **Enable**

**Trong MediaMTX config**:
```yaml
paths:
  server_room:
    runOnInit: ffmpeg -rtsp_transport tcp -reconnect 1 -reconnect_streamed 1 -i rtsp://... -c copy -f rtsp rtsp://localhost:$RTSP_PORT/server_room
    runOnInitRestart: yes
```

### ❌ Vấn Đề 4: Phone Nóng, Pin Hết Nhanh

**Giải pháp**:
1. **Cắm sạc phone liên tục** (quan trọng!)
2. Tắt màn hình (IP Webcam có tùy chọn "Background Mode")
3. Giảm resolution + FPS
4. Đặt phone ở chỗ thoáng mát

---

## 🎬 Demo Video Setup (Từng Bước)

### 1. Test Cơ Bản (5 phút)

```powershell
# Terminal 1: Watch MediaMTX logs
docker logs -f iot-mediamtx

# Terminal 2: Test phone stream
docker exec iot-mediamtx ffprobe rtsp://192.168.1.105:8080/h264_pcm.sdp
```

### 2. Test với VLC Player

1. Mở VLC
2. Media → Open Network Stream
3. Paste: `rtsp://192.168.1.105:8080/h264_pcm.sdp`
4. Play → Nếu thấy video = Success! ✅

### 3. Test với Browser

```powershell
# Open MediaMTX web UI
Start-Process "http://localhost:8889/"
```

Click vào path `server_room` → Thấy live video

---

## 📊 Performance Tips

### WiFi Optimization
- ✅ Dùng WiFi 5GHz thay vì 2.4GHz
- ✅ Phone đặt gần router
- ✅ Tắt các thiết bị không cần thiết

### Phone Settings
- ✅ Airplane mode + WiFi only (tắt cellular)
- ✅ Brightness minimum
- ✅ Background apps tắt hết

### Encoding Settings
```yaml
# Recommended for 4 phone cameras
Resolution: 640x480 (VGA)
FPS: 15
Bitrate: 500-1000 kbps
Codec: H.264
```

---

## 🎯 Production Setup Checklist

### Hardware
- [ ] Điện thoại/tablet cũ (không dùng phone chính)
- [ ] Cáp sạc dài + adapter
- [ ] Giá đỡ phone (tripod mini hoặc gắn tường)
- [ ] Router WiFi ổn định

### Software
- [ ] IP Webcam/DroidCam đã cài và test
- [ ] MediaMTX config đã update
- [ ] Database ZoneCamera đã update RTSP URL
- [ ] Auto-restart on boot đã enable

### Testing
- [ ] Stream chạy ổn định ít nhất 1 giờ
- [ ] Reconnect tự động khi mất kết nối
- [ ] Phone không nóng quá (< 45°C)
- [ ] Battery tối ưu (khi cắm sạc)

---

## 🚀 Next Steps

Sau khi setup xong phone cameras:

1. **Test Smart Building Logic**:
   ```powershell
   # Publish high temperature
   docker exec iot-app python scripts/test_smart_building.py
   
   # Check alert được tạo + camera recording được trigger
   ```

2. **View Live Streams**:
   ```powershell
   # Open React dashboard (Phase 3)
   cd frontend
   npm run dev
   ```

3. **Monitor Performance**:
   ```powershell
   # MediaMTX stats
   Invoke-WebRequest http://localhost:8889/v3/metrics
   ```

---

## 📚 Resources

- [IP Webcam Documentation](https://ip-webcam.appspot.com/)
- [DroidCam Setup Guide](https://www.dev47apps.com/droidcam/)
- [MediaMTX Publish Documentation](https://github.com/bluenviron/mediamtx#publish-to-the-server)
- [FFmpeg RTSP Options](https://ffmpeg.org/ffmpeg-protocols.html#rtsp)

---

## ✅ Summary

✨ **Bây giờ bạn đã có**:
- 📱 4 phone cameras thực tế thay vì giả lập
- 🎥 Live video streaming qua MediaMTX
- 🔔 Alert system trigger camera recording khi có vấn đề
- 📊 Real-time dashboard hiển thị tất cả cameras

**Cost**: **$0** - chỉ cần phone cũ không dùng! 🎉

---

**Need help?** Check logs:
```powershell
# Phone camera connection
docker logs iot-mediamtx --tail 50

# Django API
docker logs iot-app --tail 50

# Celery processing
docker logs iot-celery --tail 50
```
