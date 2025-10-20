# 📡 Real-time Communication Strategy - Polling vs WebSocket

## 🎯 TL;DR - Khi nào dùng gì?

| Use Case | Best Choice | Lý do |
|----------|-------------|-------|
| **Temperature sensors** (hiện tại) | ✅ **Polling 5-30s** | Dữ liệu thay đổi chậm, tiết kiệm tài nguyên |
| **IP Camera streams** | ❌ Không dùng cả 2 | Dùng **RTSP/HLS/WebRTC** thay thế |
| **MediaMTX streaming** | ✅ **WebRTC/HLS** | Streaming video chuyên dụng |
| **Chat app** | ✅ **WebSocket** | Cần instant messaging |
| **Stock prices** | ✅ **WebSocket** | Thay đổi liên tục, cần real-time |
| **Motion detection alerts** | ✅ **WebSocket** | Cần thông báo ngay lập tức |

---

## 📊 Case Study: Hệ thống hiện tại (Temperature/Humidity)

### ✅ Polling 5-30s là HỢP LÝ vì:

1. **Dữ liệu thay đổi chậm**
   - Nhiệt độ/độ ẩm không đổi mỗi giây
   - Cập nhật 5-30s là đủ để phát hiện xu hướng
   - Người dùng không cần biết realtime từng mili-giây

2. **Đơn giản, ít bug**
   - Không cần WebSocket server
   - Không cần xử lý reconnection logic
   - Dễ debug, dễ maintain

3. **Tiết kiệm tài nguyên**
   - Ít kết nối đồng thời
   - Backend đỡ stress hơn
   - Phù hợp với IoT devices có battery

4. **Caching hiệu quả**
   - Redis cache 60s hoạt động tốt
   - Nhiều client cùng hit cache
   - Giảm load MongoDB

### ⚠️ Khi NÀO nên chuyển sang WebSocket:

1. **Số lượng readings > 1000/phút**
2. **Cần thông báo alerts ngay lập tức**
3. **Dashboard có > 100 concurrent users**
4. **Dữ liệu thay đổi liên tục (< 1s)**

---

## 📹 Case Study: Nếu IoT là IP Camera

### ❌ **KHÔNG dùng Polling hoặc WebSocket cho video!**

### ✅ **Giải pháp đúng: Video Streaming Protocols**

```
Camera → MediaMTX → Protocol → Browser/App
                       ↓
              ┌────────┼────────┐
              ↓        ↓        ↓
           RTSP     WebRTC     HLS
         (local)   (WebRTC)  (HTTP)
```

### 1️⃣ **RTSP (Real Time Streaming Protocol)**
```
Camera (RTSP stream)
    ↓
MediaMTX Server
    ↓
VLC/ffmpeg player
```

**Khi dùng:**
- Xem camera trên VLC, OBS
- Low latency (<500ms)
- Local network

**Không dùng:**
- Trên web browser (không support RTSP)

---

### 2️⃣ **WebRTC (Web Real-Time Communication)**
```
Camera → MediaMTX → WebRTC → Browser
                              ↓
                         Real-time video
```

**Ưu điểm:**
- ✅ Ultra low latency (<100ms)
- ✅ Peer-to-peer connection
- ✅ Chạy trên browser không cần plugin
- ✅ Support audio + video
- ✅ Tốt nhất cho 2-way communication (video call)

**Nhược điểm:**
- ❌ Phức tạp để setup
- ❌ Tốn bandwidth
- ❌ Cần STUN/TURN server

**Khi dùng:**
- Video call, conference
- Security camera cần xem realtime
- Interactive applications

**Code example:**
```javascript
// React component với WebRTC
import React, { useRef, useEffect } from 'react';

function CameraStream({ streamUrl }) {
  const videoRef = useRef(null);
  const peerConnection = useRef(null);

  useEffect(() => {
    const startStream = async () => {
      const pc = new RTCPeerConnection({
        iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
      });

      pc.ontrack = (event) => {
        videoRef.current.srcObject = event.streams[0];
      };

      // Fetch offer from MediaMTX
      const offer = await fetch(`${streamUrl}/whep`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/sdp' },
      });

      await pc.setRemoteDescription(new RTCSessionDescription({
        type: 'offer',
        sdp: await offer.text()
      }));

      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);

      peerConnection.current = pc;
    };

    startStream();

    return () => {
      if (peerConnection.current) {
        peerConnection.current.close();
      }
    };
  }, [streamUrl]);

  return <video ref={videoRef} autoPlay playsInline />;
}
```

---

### 3️⃣ **HLS (HTTP Live Streaming)**
```
Camera → MediaMTX → HLS (.m3u8) → Browser
                                    ↓
                              Video.js/hls.js
```

**Ưu điểm:**
- ✅ Dễ setup nhất
- ✅ Tương thích tốt (iOS, Android, browsers)
- ✅ Adaptive bitrate (tự động điều chỉnh quality)
- ✅ Có thể cache bằng CDN
- ✅ Scale tốt cho nhiều viewers

**Nhược điểm:**
- ❌ Latency cao (5-30 seconds)
- ❌ Không realtime

**Khi dùng:**
- Live broadcast (YouTube, Twitch style)
- Recording playback
- Không cần low latency
- Nhiều người xem cùng lúc

**Code example:**
```javascript
// React component với HLS
import React, { useRef, useEffect } from 'react';
import Hls from 'hls.js';

function CameraStream({ streamUrl }) {
  const videoRef = useRef(null);

  useEffect(() => {
    if (Hls.isSupported()) {
      const hls = new Hls();
      hls.loadSource(`${streamUrl}/index.m3u8`);
      hls.attachMedia(videoRef.current);
      
      return () => hls.destroy();
    } else if (videoRef.current.canPlayType('application/vnd.apple.mpegurl')) {
      // Native HLS support (Safari)
      videoRef.current.src = `${streamUrl}/index.m3u8`;
    }
  }, [streamUrl]);

  return (
    <video 
      ref={videoRef} 
      controls 
      autoPlay 
      style={{ width: '100%', maxWidth: '800px' }}
    />
  );
}
```

---

### 4️⃣ **DASH (Dynamic Adaptive Streaming over HTTP)**

Tương tự HLS nhưng chuẩn mở hơn. MediaMTX support cả HLS và DASH.

---

## 🎥 MediaMTX Integration Guide

### Architecture với MediaMTX:

```
┌──────────────┐
│  IP Camera   │ (RTSP)
└──────┬───────┘
       ↓
┌──────────────┐
│  MediaMTX    │ (Server)
│  Port 8554   │
└──────┬───────┘
       ↓
   ┌───┴────┬─────────┬─────────┐
   ↓        ↓         ↓         ↓
 RTSP    WebRTC     HLS       HTTP
(VLC)   (Browser)  (Web)     (API)
```

### Step 1: Setup MediaMTX với Docker

```yaml
# docker-compose.yml
version: '3.8'

services:
  mediamtx:
    image: bluenviron/mediamtx:latest
    container_name: mediamtx
    ports:
      - "8554:8554"   # RTSP
      - "8888:8888"   # WebRTC
      - "8889:8889"   # HLS
    volumes:
      - ./mediamtx.yml:/mediamtx.yml
    restart: unless-stopped

  # Your existing services...
  iot-app:
    # ...
```

### Step 2: MediaMTX Config

```yaml
# mediamtx.yml
paths:
  camera1:
    source: rtsp://admin:password@192.168.1.100:554/stream1
    runOnReady: echo "Camera 1 ready"
    
  camera2:
    source: rtsp://admin:password@192.168.1.101:554/stream1
    
  # Dynamic path for any camera
  ~^camera_.*:
    source: publisher
    runOnPublish: python /scripts/notify_camera_online.py $RTSP_PATH
```

### Step 3: React Dashboard Component

```javascript
// src/components/CameraGrid.jsx
import React, { useState } from 'react';
import Hls from 'hls.js';

const CAMERAS = [
  { id: 1, name: 'Front Door', stream: 'camera1' },
  { id: 2, name: 'Backyard', stream: 'camera2' },
  { id: 3, name: 'Garage', stream: 'camera3' },
];

function CameraGrid() {
  const [selectedCamera, setSelectedCamera] = useState(null);

  return (
    <div className="camera-grid">
      <div className="grid grid-cols-2 gap-4">
        {CAMERAS.map((camera) => (
          <CameraView 
            key={camera.id} 
            camera={camera}
            onFullscreen={() => setSelectedCamera(camera)}
          />
        ))}
      </div>

      {selectedCamera && (
        <FullscreenCamera 
          camera={selectedCamera} 
          onClose={() => setSelectedCamera(null)} 
        />
      )}
    </div>
  );
}

function CameraView({ camera, onFullscreen }) {
  const videoRef = React.useRef(null);

  React.useEffect(() => {
    const streamUrl = `http://localhost:8889/${camera.stream}/index.m3u8`;
    
    if (Hls.isSupported()) {
      const hls = new Hls({
        enableWorker: true,
        lowLatencyMode: true,
        backBufferLength: 90
      });
      
      hls.loadSource(streamUrl);
      hls.attachMedia(videoRef.current);
      
      hls.on(Hls.Events.ERROR, (event, data) => {
        console.error('HLS Error:', data);
      });

      return () => hls.destroy();
    }
  }, [camera.stream]);

  return (
    <div className="card relative">
      <div className="absolute top-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded">
        {camera.name}
      </div>
      <video 
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className="w-full rounded"
      />
      <button 
        onClick={onFullscreen}
        className="absolute bottom-2 right-2 bg-white p-2 rounded-full shadow-lg"
      >
        🔍
      </button>
    </div>
  );
}

function FullscreenCamera({ camera, onClose }) {
  const videoRef = React.useRef(null);

  React.useEffect(() => {
    const streamUrl = `http://localhost:8889/${camera.stream}/index.m3u8`;
    
    if (Hls.isSupported()) {
      const hls = new Hls();
      hls.loadSource(streamUrl);
      hls.attachMedia(videoRef.current);
      return () => hls.destroy();
    }
  }, [camera.stream]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center">
      <button 
        onClick={onClose}
        className="absolute top-4 right-4 text-white text-4xl"
      >
        ✕
      </button>
      <div className="w-full h-full p-8">
        <h2 className="text-white text-2xl mb-4">{camera.name}</h2>
        <video 
          ref={videoRef}
          controls
          autoPlay
          className="w-full h-full object-contain"
        />
      </div>
    </div>
  );
}

export default CameraGrid;
```

---

## 🔄 Hybrid Approach: Sensor Data + Cameras

### Architecture tổng hợp:

```
┌─────────────────────────────────────────────────┐
│           Smart IoT Monitoring System           │
└─────────────────────────────────────────────────┘
           ↓                              ↓
    ┌──────────┐                   ┌──────────┐
    │ Sensors  │                   │ Cameras  │
    │ (MQTT)   │                   │ (RTSP)   │
    └────┬─────┘                   └────┬─────┘
         ↓                              ↓
    ┌────────┐                   ┌──────────┐
    │ Kafka  │                   │MediaMTX  │
    └────┬───┘                   └────┬─────┘
         ↓                              ↓
    ┌────────┐                   ┌──────────┐
    │ Celery │                   │   HLS    │
    └────┬───┘                   └────┬─────┘
         ↓                              ↓
  ┌──────┴──────┐                      │
  ↓      ↓      ↓                      │
MySQL MongoDB Redis                    │
  ↓      ↓      ↓                      │
  └──────┴──────┘                      │
         ↓                              ↓
    ┌─────────────────────────────────────┐
    │       Django REST API                │
    └─────────────────────────────────────┘
         ↓                              ↓
    ┌─────────┐                   ┌─────────┐
    │ Polling │                   │ Streaming│
    │  (5s)   │                   │  (HLS)   │
    └─────────┘                   └─────────┘
         ↓                              ↓
    ┌─────────────────────────────────────┐
    │      React Dashboard                 │
    │  - Sensor Charts (Polling)           │
    │  - Camera Grid (HLS Streaming)       │
    └─────────────────────────────────────┘
```

### React Dashboard với cả Sensors và Cameras:

```javascript
// src/components/DashboardWithCameras.jsx
import React from 'react';
import SensorDashboard from './Dashboard';  // Existing component
import CameraGrid from './CameraGrid';      // New component

function DashboardWithCameras() {
  return (
    <div className="space-y-6">
      {/* Sensor monitoring - Polling 5s */}
      <section>
        <h2 className="text-2xl font-bold mb-4">
          📊 Sensor Monitoring
        </h2>
        <SensorDashboard />
      </section>

      {/* Camera feeds - HLS Streaming */}
      <section>
        <h2 className="text-2xl font-bold mb-4">
          📹 Live Camera Feeds
        </h2>
        <CameraGrid />
      </section>

      {/* Motion detection alerts - WebSocket */}
      <section>
        <h2 className="text-2xl font-bold mb-4">
          🚨 Real-time Alerts
        </h2>
        <AlertsPanel />
      </section>
    </div>
  );
}
```

---

## ⚡ Khi NÀO dùng WebSocket cho Sensors?

### Tình huống cần WebSocket:

```javascript
// src/components/AlertsPanel.jsx
import React, { useEffect, useState } from 'react';

function AlertsPanel() {
  const [alerts, setAlerts] = useState([]);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    // WebSocket chỉ cho ALERTS, không phải tất cả data
    const websocket = new WebSocket('ws://localhost:8000/ws/alerts/');

    websocket.onmessage = (event) => {
      const alert = JSON.parse(event.data);
      
      // Show notification
      if (Notification.permission === 'granted') {
        new Notification(alert.title, {
          body: alert.message,
          icon: '/alert-icon.png'
        });
      }

      setAlerts(prev => [alert, ...prev].slice(0, 50));
    };

    setWs(websocket);

    return () => websocket.close();
  }, []);

  return (
    <div className="card">
      <h3>🚨 Real-time Alerts (WebSocket)</h3>
      {alerts.map((alert, i) => (
        <div key={i} className={`alert alert-${alert.level}`}>
          <strong>{alert.title}</strong>
          <p>{alert.message}</p>
          <span>{new Date(alert.timestamp).toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
}
```

**Dùng WebSocket khi:**
- ❗ Temperature > 35°C (cảnh báo ngay)
- 🚪 Motion detected (cảnh báo xâm nhập)
- 🔥 Smoke detected (báo cháy)
- 💧 Water leak detected

**Vẫn dùng Polling cho:**
- 📊 Normal sensor readings
- 📈 Charts và statistics
- 📋 Historical data

---

## 📊 So sánh Performance

| Method | Latency | Server Load | Battery Impact | Best For |
|--------|---------|-------------|----------------|----------|
| **Polling 30s** | 0-30s | Thấp | Thấp | Normal sensors |
| **Polling 5s** | 0-5s | Trung bình | Trung bình | Temp/Humidity |
| **WebSocket** | <100ms | Cao | Cao | Alerts, Chat |
| **HLS** | 5-30s | Trung bình | N/A | Video playback |
| **WebRTC** | <100ms | Rất cao | N/A | Live video call |

---

## 🎯 Khuyến nghị cho hệ thống của bạn

### Giữ nguyên Polling 5s cho sensors ✅

**Lý do:**
- Nhiệt độ/độ ẩm không cần instant update
- Tiết kiệm pin cho IoT devices
- Backend đơn giản, dễ maintain
- Redis caching hoạt động tốt
- 5s là đủ nhanh cho monitoring

### Thêm WebSocket chỉ cho Alerts (optional) ⚡

```python
# monitoring/consumers.py (Django Channels)
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("alerts", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("alerts", self.channel_name)

    async def alert_message(self, event):
        await self.send(text_data=json.dumps(event['message']))
```

```python
# monitoring/tasks.py - Trigger alerts
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def handle_payload(message):
    # ... existing code ...
    
    # Check for alerts
    if reading.temperature > 35:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "alerts",
            {
                "type": "alert_message",
                "message": {
                    "title": "High Temperature Alert!",
                    "level": "danger",
                    "message": f"Device {device_id}: {reading.temperature}°C",
                    "timestamp": reading.timestamp.isoformat()
                }
            }
        )
```

### Nếu thêm Cameras: Dùng MediaMTX + HLS 📹

**Không dùng:**
- ❌ Polling để lấy video frames
- ❌ WebSocket để stream video
- ❌ REST API để lấy images

**Dùng:**
- ✅ MediaMTX server
- ✅ HLS cho playback (latency 5-30s OK)
- ✅ WebRTC nếu cần low latency (<1s)

---

## 🏁 Kết luận

### Cho hệ thống Temperature/Humidity hiện tại:
**✅ GIỮ NGUYÊN POLLING 5-30s** - Đây là lựa chọn tối ưu!

### Nếu thêm Cameras:
**✅ Dùng MediaMTX + HLS/WebRTC** - Chuyên dụng cho video

### Nếu cần Alerts realtime:
**✅ Thêm WebSocket chỉ cho alerts** - Hybrid approach

### Architecture đề xuất:
```
Polling (5s)     → Sensor readings, charts
WebSocket        → Critical alerts only
HLS/WebRTC       → Video streaming (nếu có cameras)
```

**Đừng over-engineer!** Polling 5s là perfect cho IoT sensors như temperature/humidity. 🎯
