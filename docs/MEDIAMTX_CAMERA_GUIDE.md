# 📹 Camera Integration with MediaMTX - Complete Guide

## 🎯 Overview

MediaMTX là open-source streaming server hỗ trợ nhiều protocols:
- **RTSP** (Real Time Streaming Protocol)
- **WebRTC** (Web Real-Time Communication)
- **HLS** (HTTP Live Streaming)
- **RTMP** (Real-Time Messaging Protocol)

**GitHub:** https://github.com/bluenviron/mediamtx

---

## 🏗️ Architecture

```
┌─────────────┐
│ IP Camera 1 │ rtsp://192.168.1.100:554
└──────┬──────┘
       │
┌──────┴──────┐
│ IP Camera 2 │ rtsp://192.168.1.101:554
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────┐
│         MediaMTX Server             │
│                                     │
│  Ports:                            │
│  - 8554: RTSP                      │
│  - 8888: WebRTC                    │
│  - 8889: HLS                       │
│  - 1935: RTMP                      │
└─────────────┬───────────────────────┘
              ↓
       ┌──────┴──────┐
       ↓             ↓
  ┌────────┐   ┌──────────┐
  │ VLC    │   │ Browser  │
  │ Player │   │ (React)  │
  └────────┘   └──────────┘
                    ↓
              ┌──────────┐
              │ HLS.js   │
              │ Video.js │
              └──────────┘
```

---

## 🚀 Setup MediaMTX with Docker

### Step 1: Add to Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  # ... existing services (iot-app, mongodb, etc.) ...

  mediamtx:
    image: bluenviron/mediamtx:latest
    container_name: mediamtx
    ports:
      - "8554:8554"   # RTSP
      - "8888:8888"   # WebRTC
      - "8889:8889"   # HLS
      - "1935:1935"   # RTMP (optional)
    volumes:
      - ./mediamtx.yml:/mediamtx.yml
      - ./camera-recordings:/recordings  # For recording streams
    environment:
      - MTX_LOGLEVEL=info
    restart: unless-stopped
    networks:
      - smart-iot-monitoring-system_default

networks:
  smart-iot-monitoring-system_default:
    external: true
```

### Step 2: MediaMTX Configuration

```yaml
# mediamtx.yml
# MediaMTX configuration file

# Log level: debug, info, warn
logLevel: info

# Enable metrics API
metrics: yes
metricsAddress: :9998

# API for management
api: yes
apiAddress: :9997

# RTSP server
rtspAddress: :8554

# WebRTC server
webrtcAddress: :8888
webrtcICEServers:
  - urls: [stun:stun.l.google.com:19302]

# HLS server
hlsAddress: :8889
hlsAlwaysRemux: yes
hlsVariant: mpegts
hlsSegmentCount: 3
hlsSegmentDuration: 1s

# Paths (streams)
paths:
  # Example: Static RTSP camera
  camera_front:
    source: rtsp://admin:password@192.168.1.100:554/stream1
    sourceProtocol: automatic
    sourceOnDemand: no  # Always pull stream
    runOnReady: echo "Front camera is ready"
    runOnDemand: echo "Front camera stream requested"
    record: yes
    recordPath: /recordings/camera_front/%Y-%m-%d_%H-%M-%S.mp4
    recordFormat: mp4
    recordSegmentDuration: 1h

  camera_back:
    source: rtsp://admin:password@192.168.1.101:554/stream1
    sourceProtocol: automatic
    sourceOnDemand: no
    record: yes
    recordPath: /recordings/camera_back/%Y-%m-%d_%H-%M-%S.mp4

  camera_garage:
    source: rtsp://admin:password@192.168.1.102:554/stream1
    sourceProtocol: automatic
    sourceOnDemand: yes  # Only pull when someone watches

  # Dynamic path for any camera
  ~^camera_.*:
    source: publisher
    runOnPublish: python /scripts/notify_camera_online.py $RTSP_PATH
    runOnUnPublish: python /scripts/notify_camera_offline.py $RTSP_PATH

  # Allow RTSP publishing (for mobile apps)
  all:
    source: publisher
```

### Step 3: Start MediaMTX

```powershell
# Start MediaMTX
docker-compose up -d mediamtx

# Check logs
docker logs -f mediamtx

# Expected output:
# 2025/10/20 10:30:00 INF MediaMTX v1.0.0
# 2025/10/20 10:30:00 INF [RTSP] listener opened on :8554
# 2025/10/20 10:30:00 INF [WebRTC] listener opened on :8888
# 2025/10/20 10:30:00 INF [HLS] listener opened on :8889
```

---

## 🎥 React Components for Cameras

### Option 1: HLS Streaming (Recommended)

**Latency:** 5-30 seconds (OK cho monitoring)
**Pros:** Dễ setup, stable, scale tốt
**Cons:** Latency cao

```javascript
// src/components/CameraView.jsx
import React, { useRef, useEffect, useState } from 'react';
import Hls from 'hls.js';

function CameraView({ cameraName, streamPath }) {
  const videoRef = useRef(null);
  const hlsRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const streamUrl = `http://localhost:8889/${streamPath}/index.m3u8`;

    if (Hls.isSupported()) {
      const hls = new Hls({
        enableWorker: true,
        lowLatencyMode: true,
        backBufferLength: 90,
        maxBufferLength: 30,
        maxMaxBufferLength: 60,
      });

      hls.loadSource(streamUrl);
      hls.attachMedia(videoRef.current);

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        console.log(`✅ ${cameraName} stream loaded`);
        setIsLoading(false);
        videoRef.current.play().catch(e => console.log('Autoplay prevented:', e));
      });

      hls.on(Hls.Events.ERROR, (event, data) => {
        console.error(`❌ HLS Error (${cameraName}):`, data);
        if (data.fatal) {
          setError('Failed to load stream');
          switch (data.type) {
            case Hls.ErrorTypes.NETWORK_ERROR:
              console.log('Network error, trying to recover...');
              hls.startLoad();
              break;
            case Hls.ErrorTypes.MEDIA_ERROR:
              console.log('Media error, trying to recover...');
              hls.recoverMediaError();
              break;
            default:
              console.log('Fatal error, destroying HLS instance');
              hls.destroy();
              break;
          }
        }
      });

      hlsRef.current = hls;

      return () => {
        if (hlsRef.current) {
          hlsRef.current.destroy();
        }
      };
    } else if (videoRef.current.canPlayType('application/vnd.apple.mpegurl')) {
      // Native HLS support (Safari)
      videoRef.current.src = streamUrl;
      videoRef.current.addEventListener('loadedmetadata', () => {
        setIsLoading(false);
      });
    } else {
      setError('HLS not supported in this browser');
    }
  }, [cameraName, streamPath]);

  return (
    <div className="card relative">
      {/* Camera name badge */}
      <div className="absolute top-2 left-2 bg-black bg-opacity-70 text-white px-3 py-1 rounded z-10">
        <span className="font-semibold">{cameraName}</span>
      </div>

      {/* Live indicator */}
      <div className="absolute top-2 right-2 bg-red-600 text-white px-3 py-1 rounded flex items-center z-10">
        <span className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></span>
        LIVE
      </div>

      {/* Loading overlay */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-10">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-white mx-auto mb-2"></div>
            <p className="text-white">Loading stream...</p>
          </div>
        </div>
      )}

      {/* Error overlay */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-red-900 z-10">
          <div className="text-center text-white">
            <p className="text-4xl mb-2">⚠️</p>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Video player */}
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className="w-full rounded"
        style={{ backgroundColor: '#000' }}
      />
    </div>
  );
}

export default CameraView;
```

### Option 2: WebRTC Streaming (Low Latency)

**Latency:** <100ms
**Pros:** Realtime, tốt cho 2-way communication
**Cons:** Phức tạp hơn, tốn bandwidth

```javascript
// src/components/CameraViewWebRTC.jsx
import React, { useRef, useEffect, useState } from 'react';

function CameraViewWebRTC({ cameraName, streamPath }) {
  const videoRef = useRef(null);
  const pcRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const startWebRTC = async () => {
      try {
        // Create peer connection
        const pc = new RTCPeerConnection({
          iceServers: [
            { urls: 'stun:stun.l.google.com:19302' },
          ],
        });

        pc.ontrack = (event) => {
          console.log(`✅ Track received from ${cameraName}`);
          if (videoRef.current) {
            videoRef.current.srcObject = event.streams[0];
            setIsConnected(true);
          }
        };

        pc.oniceconnectionstatechange = () => {
          console.log(`ICE state: ${pc.iceConnectionState}`);
          if (pc.iceConnectionState === 'failed') {
            setError('Connection failed');
          }
        };

        // Request WHEP offer from MediaMTX
        const response = await fetch(`http://localhost:8888/${streamPath}/whep`, {
          method: 'OPTIONS',
        });

        if (!response.ok) {
          throw new Error('Failed to get stream info');
        }

        // Get offer
        const offerResponse = await fetch(`http://localhost:8888/${streamPath}/whep`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/sdp',
          },
        });

        const offer = await offerResponse.text();

        await pc.setRemoteDescription(new RTCSessionDescription({
          type: 'offer',
          sdp: offer,
        }));

        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);

        // Send answer
        await fetch(`http://localhost:8888/${streamPath}/whep`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/sdp',
          },
          body: answer.sdp,
        });

        pcRef.current = pc;
      } catch (err) {
        console.error(`❌ WebRTC Error (${cameraName}):`, err);
        setError(err.message);
      }
    };

    startWebRTC();

    return () => {
      if (pcRef.current) {
        pcRef.current.close();
      }
    };
  }, [cameraName, streamPath]);

  return (
    <div className="card relative">
      <div className="absolute top-2 left-2 bg-black bg-opacity-70 text-white px-3 py-1 rounded z-10">
        {cameraName}
      </div>

      {isConnected && (
        <div className="absolute top-2 right-2 bg-green-600 text-white px-3 py-1 rounded flex items-center z-10">
          <span className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></span>
          LIVE (WebRTC)
        </div>
      )}

      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-red-900 text-white z-10">
          <div className="text-center">
            <p className="text-4xl mb-2">⚠️</p>
            <p>{error}</p>
          </div>
        </div>
      )}

      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className="w-full rounded"
        style={{ backgroundColor: '#000' }}
      />
    </div>
  );
}

export default CameraViewWebRTC;
```

### Camera Grid Component

```javascript
// src/components/CameraGrid.jsx
import React, { useState } from 'react';
import CameraView from './CameraView';

const CAMERAS = [
  { id: 1, name: 'Front Door', stream: 'camera_front' },
  { id: 2, name: 'Backyard', stream: 'camera_back' },
  { id: 3, name: 'Garage', stream: 'camera_garage' },
  { id: 4, name: 'Living Room', stream: 'camera_living' },
];

function CameraGrid() {
  const [selectedCamera, setSelectedCamera] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'single'

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold flex items-center">
          <span className="mr-2">📹</span>
          Live Camera Feeds
        </h2>
        <div className="flex space-x-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`px-4 py-2 rounded-lg ${
              viewMode === 'grid'
                ? 'bg-primary-500 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Grid View
          </button>
          <button
            onClick={() => setViewMode('single')}
            className={`px-4 py-2 rounded-lg ${
              viewMode === 'single'
                ? 'bg-primary-500 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Single View
          </button>
        </div>
      </div>

      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {CAMERAS.map((camera) => (
            <div
              key={camera.id}
              onClick={() => {
                setSelectedCamera(camera);
                setViewMode('single');
              }}
              className="cursor-pointer transform hover:scale-105 transition-transform"
            >
              <CameraView
                cameraName={camera.name}
                streamPath={camera.stream}
              />
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {/* Camera selector */}
          <div className="flex space-x-2 overflow-x-auto pb-2">
            {CAMERAS.map((camera) => (
              <button
                key={camera.id}
                onClick={() => setSelectedCamera(camera)}
                className={`px-4 py-2 rounded-lg whitespace-nowrap ${
                  selectedCamera?.id === camera.id
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-200 text-gray-700'
                }`}
              >
                {camera.name}
              </button>
            ))}
          </div>

          {/* Selected camera in large view */}
          {selectedCamera && (
            <div className="max-w-4xl mx-auto">
              <CameraView
                cameraName={selectedCamera.name}
                streamPath={selectedCamera.stream}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default CameraGrid;
```

---

## 📦 Install Required NPM Packages

```powershell
cd frontend
npm install hls.js
```

Update `package.json`:
```json
{
  "dependencies": {
    "hls.js": "^1.4.0"
  }
}
```

---

## 🔧 Django Integration (Optional)

### Store Camera Metadata in Database

```python
# monitoring/models.py
from django.db import models

class Camera(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    stream_path = models.CharField(max_length=100, unique=True)  # e.g., 'camera_front'
    rtsp_url = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    device = models.ForeignKey('Device', on_delete=models.CASCADE, related_name='cameras', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.stream_path})"

    @property
    def hls_url(self):
        return f"http://localhost:8889/{self.stream_path}/index.m3u8"

    @property
    def webrtc_url(self):
        return f"http://localhost:8888/{self.stream_path}/whep"
```

### Create Camera API

```python
# monitoring/serializers.py
from rest_framework import serializers
from .models import Camera

class CameraSerializer(serializers.ModelSerializer):
    hls_url = serializers.ReadOnlyField()
    webrtc_url = serializers.ReadOnlyField()

    class Meta:
        model = Camera
        fields = ['id', 'name', 'location', 'stream_path', 'rtsp_url', 
                  'is_active', 'device', 'hls_url', 'webrtc_url']
```

```python
# monitoring/views.py
from rest_framework import viewsets
from .models import Camera
from .serializers import CameraSerializer

class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    
    def get_queryset(self):
        queryset = Camera.objects.all()
        device_id = self.request.query_params.get('device_id')
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        return queryset
```

```python
# monitoring/urls.py
from rest_framework.routers import DefaultRouter
from .views import CameraViewSet

router.register(r'cameras', CameraViewSet)
```

### Fetch Cameras from API

```javascript
// src/services/api.js
export const apiService = {
  // ... existing methods ...
  
  // Cameras
  getCameras: () => api.get('/cameras/'),
  getCamera: (id) => api.get(`/cameras/${id}/`),
  getCamerasByDevice: (deviceId) => 
    api.get('/cameras/', { params: { device_id: deviceId } }),
};
```

```javascript
// src/components/CameraGrid.jsx - Fetch from API
function CameraGrid() {
  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCameras = async () => {
      try {
        const response = await apiService.getCameras();
        setCameras(response.data);
      } catch (error) {
        console.error('Error fetching cameras:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCameras();
  }, []);

  if (loading) return <div>Loading cameras...</div>;

  return (
    <div className="grid grid-cols-2 gap-4">
      {cameras.map((camera) => (
        <CameraView
          key={camera.id}
          cameraName={camera.name}
          streamPath={camera.stream_path}
        />
      ))}
    </div>
  );
}
```

---

## 🎯 Complete Dashboard with Sensors + Cameras

```javascript
// src/App.jsx - Add Cameras route
import CameraGrid from './components/CameraGrid';

function App() {
  return (
    <Router>
      <Navigation />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/devices" element={<DeviceList />} />
        <Route path="/readings" element={<ReadingsTable />} />
        <Route path="/search" element={<SearchForm />} />
        <Route path="/cameras" element={<CameraGrid />} />  {/* NEW */}
      </Routes>
    </Router>
  );
}
```

---

## 🚀 Testing

### Test 1: View stream in VLC

```
rtsp://localhost:8554/camera_front
```

### Test 2: View HLS in browser

```
http://localhost:8889/camera_front/index.m3u8
```

### Test 3: Check MediaMTX API

```powershell
# Get all paths
curl http://localhost:9997/v3/paths/list

# Get specific path
curl http://localhost:9997/v3/paths/get/camera_front
```

---

## 📊 Performance Tips

1. **Use HLS for >10 viewers** - Scalable, can use CDN
2. **Use WebRTC for <10 viewers** - Low latency
3. **Enable recording** - Save streams to disk
4. **Use adaptive bitrate** - HLS supports multiple qualities
5. **Add authentication** - Protect camera streams

---

## 🎉 Summary

✅ **MediaMTX** - Streaming server
✅ **HLS** - Best for monitoring (easy, scalable)
✅ **WebRTC** - Best for real-time (<100ms latency)
✅ **React components** - CameraView, CameraGrid
✅ **Django integration** - Camera model, API

**Your complete IoT system now supports both sensors AND cameras!** 📹🌡️
