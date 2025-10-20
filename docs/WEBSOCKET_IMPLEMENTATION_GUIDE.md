# 🚀 WebSocket Implementation Guide (Optional)

## 📋 Khi nào cần implement?

Chỉ implement WebSocket nếu bạn cần:
- ⚠️ **Critical alerts** cần thông báo NGAY LẬP TỨC
- 💬 **Chat/messaging** giữa users
- 🎮 **Real-time collaboration** (như Google Docs)
- 📊 **Live dashboard** với >100 concurrent users

**Cho temperature/humidity monitoring: KHÔNG CẦN WebSocket!**

---

## 🛠️ Implementation Steps (Nếu thực sự cần)

### Step 1: Install Django Channels

```powershell
# In Docker container
docker exec -it iot-app pip install channels channels-redis daphne
```

```python
# requirements.txt
# ... existing packages ...
channels==4.0.0
channels-redis==4.1.0
daphne==4.0.0
```

### Step 2: Update Django Settings

```python
# smart_iot/settings.py

INSTALLED_APPS = [
    'daphne',  # Must be before django.contrib.staticfiles
    'rest_framework',
    'corsheaders',
    # ... existing apps ...
    'channels',
]

# Add ASGI application
ASGI_APPLICATION = 'smart_iot.asgi.application'

# Channel layers for WebSocket
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('iot-redis', 6379)],
        },
    },
}
```

### Step 3: Create ASGI Configuration

```python
# smart_iot/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from monitoring import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_iot.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
```

### Step 4: Create WebSocket Consumer

```python
# monitoring/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime

class AlertConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time alerts only
    NOT for regular sensor readings (use polling for that)
    """
    
    async def connect(self):
        # Join alerts group
        self.room_group_name = 'alerts'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to alerts stream',
            'timestamp': datetime.now().isoformat()
        }))
    
    async def disconnect(self, close_code):
        # Leave alerts group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def alert_message(self, event):
        """
        Send alert to WebSocket
        Called when alert is triggered from Celery task
        """
        await self.send(text_data=json.dumps(event['message']))


class SensorStreamConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time sensor readings
    Use this ONLY if you have high-frequency sensors (>1 reading/second)
    For normal temp/humidity sensors, use polling instead!
    """
    
    async def connect(self):
        self.device_id = self.scope['url_route']['kwargs'].get('device_id')
        
        if self.device_id:
            self.room_group_name = f'device_{self.device_id}'
        else:
            self.room_group_name = 'all_devices'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def sensor_reading(self, event):
        """Send sensor reading to WebSocket"""
        await self.send(text_data=json.dumps(event['message']))
```

### Step 5: Create WebSocket Routing

```python
# monitoring/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # WebSocket for alerts only (recommended)
    re_path(r'ws/alerts/$', consumers.AlertConsumer.as_asgi()),
    
    # WebSocket for sensor stream (optional, usually not needed)
    re_path(r'ws/sensors/$', consumers.SensorStreamConsumer.as_asgi()),
    re_path(r'ws/sensors/(?P<device_id>\w+)/$', consumers.SensorStreamConsumer.as_asgi()),
]
```

### Step 6: Trigger Alerts from Celery Task

```python
# monitoring/tasks.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Alert thresholds
TEMP_HIGH_THRESHOLD = 35.0
TEMP_LOW_THRESHOLD = 10.0
HUMIDITY_HIGH_THRESHOLD = 80.0
HUMIDITY_LOW_THRESHOLD = 20.0

def handle_payload(message):
    try:
        data = json.loads(message.value.decode("utf-8"))
        logger.info(f"Processing: {data}")
        
        device_id = data.get("device_id")
        temperature = data.get("temperature")
        humidity = data.get("humidity")
        timestamp_str = data.get("timestamp")
        
        # ... existing code to save to MySQL, MongoDB, Redis ...
        
        # NEW: Check for alerts and send via WebSocket
        check_and_send_alerts(device_id, temperature, humidity, timestamp_str)
        
    except Exception as e:
        logger.error(f"Error: {e}")


def check_and_send_alerts(device_id, temperature, humidity, timestamp):
    """
    Check sensor values and send WebSocket alerts if thresholds exceeded
    """
    channel_layer = get_channel_layer()
    alerts = []
    
    # Check temperature alerts
    if temperature > TEMP_HIGH_THRESHOLD:
        alerts.append({
            'type': 'danger',
            'title': '🔥 High Temperature Alert!',
            'message': f'Device {device_id}: Temperature is {temperature}°C (threshold: {TEMP_HIGH_THRESHOLD}°C)',
            'device_id': device_id,
            'value': temperature,
            'metric': 'temperature',
            'timestamp': timestamp
        })
    elif temperature < TEMP_LOW_THRESHOLD:
        alerts.append({
            'type': 'warning',
            'title': '❄️ Low Temperature Alert!',
            'message': f'Device {device_id}: Temperature is {temperature}°C (threshold: {TEMP_LOW_THRESHOLD}°C)',
            'device_id': device_id,
            'value': temperature,
            'metric': 'temperature',
            'timestamp': timestamp
        })
    
    # Check humidity alerts
    if humidity > HUMIDITY_HIGH_THRESHOLD:
        alerts.append({
            'type': 'warning',
            'title': '💧 High Humidity Alert!',
            'message': f'Device {device_id}: Humidity is {humidity}% (threshold: {HUMIDITY_HIGH_THRESHOLD}%)',
            'device_id': device_id,
            'value': humidity,
            'metric': 'humidity',
            'timestamp': timestamp
        })
    elif humidity < HUMIDITY_LOW_THRESHOLD:
        alerts.append({
            'type': 'warning',
            'title': '🌵 Low Humidity Alert!',
            'message': f'Device {device_id}: Humidity is {humidity}% (threshold: {HUMIDITY_LOW_THRESHOLD}%)',
            'device_id': device_id,
            'value': humidity,
            'metric': 'humidity',
            'timestamp': timestamp
        })
    
    # Send alerts via WebSocket
    for alert in alerts:
        try:
            async_to_sync(channel_layer.group_send)(
                "alerts",
                {
                    "type": "alert_message",
                    "message": alert
                }
            )
            logger.info(f"Alert sent: {alert['title']}")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
```

### Step 7: React Component for WebSocket Alerts

```javascript
// src/components/RealTimeAlerts.jsx
import React, { useEffect, useState, useRef } from 'react';

function RealTimeAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket('ws://localhost:8000/ws/alerts/');

    ws.onopen = () => {
      console.log('✅ WebSocket connected');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('📨 Alert received:', data);

      if (data.type !== 'connection') {
        // Add new alert to list
        setAlerts(prev => [data, ...prev].slice(0, 50));

        // Show browser notification
        if (Notification.permission === 'granted') {
          new Notification(data.title, {
            body: data.message,
            icon: '/alert-icon.png',
            tag: `alert-${data.device_id}-${data.timestamp}`
          });
        }

        // Play sound (optional)
        const audio = new Audio('/alert-sound.mp3');
        audio.play().catch(e => console.log('Audio play failed:', e));
      }
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log('🔌 WebSocket disconnected');
      setIsConnected(false);
      
      // Auto-reconnect after 5s
      setTimeout(() => {
        window.location.reload();
      }, 5000);
    };

    wsRef.current = ws;

    // Request notification permission
    if (Notification.permission === 'default') {
      Notification.requestPermission();
    }

    // Cleanup
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const clearAlerts = () => {
    setAlerts([]);
  };

  const getAlertIcon = (type) => {
    switch(type) {
      case 'danger': return '🔥';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
      default: return '📢';
    }
  };

  const getAlertClass = (type) => {
    switch(type) {
      case 'danger': return 'bg-red-50 border-red-500 text-red-900';
      case 'warning': return 'bg-yellow-50 border-yellow-500 text-yellow-900';
      case 'info': return 'bg-blue-50 border-blue-500 text-blue-900';
      default: return 'bg-gray-50 border-gray-500 text-gray-900';
    }
  };

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold flex items-center">
          <span className="mr-2">🚨</span>
          Real-time Alerts
          {isConnected && (
            <span className="ml-2 flex items-center text-sm text-green-600">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></span>
              Live
            </span>
          )}
          {!isConnected && (
            <span className="ml-2 flex items-center text-sm text-red-600">
              <span className="w-2 h-2 bg-red-500 rounded-full mr-1"></span>
              Disconnected
            </span>
          )}
        </h3>
        <button 
          onClick={clearAlerts}
          className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
        >
          Clear All
        </button>
      </div>

      {alerts.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p className="text-4xl mb-2">✅</p>
          <p>No alerts - All systems normal</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {alerts.map((alert, index) => (
            <div 
              key={index}
              className={`p-4 border-l-4 rounded ${getAlertClass(alert.type)} animate-fade-in`}
            >
              <div className="flex items-start">
                <span className="text-2xl mr-3">{getAlertIcon(alert.type)}</span>
                <div className="flex-1">
                  <h4 className="font-bold">{alert.title}</h4>
                  <p className="text-sm mt-1">{alert.message}</p>
                  <div className="flex items-center mt-2 text-xs opacity-75">
                    <span>Device: {alert.device_id}</span>
                    <span className="mx-2">•</span>
                    <span>{new Date(alert.timestamp).toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default RealTimeAlerts;
```

### Step 8: Add to Dashboard

```javascript
// src/components/Dashboard.jsx
import React from 'react';
import RealTimeAlerts from './RealTimeAlerts';
import LatestReadings from './LatestReadings';
// ... other imports ...

function Dashboard() {
  // ... existing code ...

  return (
    <div className="space-y-6">
      {/* Stats cards */}
      {/* ... existing stats ... */}

      {/* Real-time Alerts via WebSocket */}
      <RealTimeAlerts />

      {/* Latest Readings via Polling */}
      <LatestReadings />

      {/* Charts */}
      {/* ... existing charts ... */}
    </div>
  );
}
```

### Step 9: Update Docker Compose

```yaml
# docker-compose.yml
services:
  iot-app:
    # Change command to use Daphne instead of runserver
    command: >
      sh -c "python manage.py migrate &&
             daphne -b 0.0.0.0 -p 8000 smart_iot.asgi:application"
    # ... rest of config ...
```

### Step 10: Update CORS for WebSocket

```python
# smart_iot/settings.py

# Add WebSocket to CORS
CORS_ALLOW_ALL_ORIGINS = False  # Set to True for development only
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "ws://localhost:3000",
    "ws://127.0.0.1:3000",
]

# Allow WebSocket headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'sec-websocket-key',
    'sec-websocket-version',
    'sec-websocket-protocol',
]
```

---

## 🧪 Testing WebSocket

### Test 1: Browser Console

```javascript
// Open browser console at http://localhost:3000
const ws = new WebSocket('ws://localhost:8000/ws/alerts/');

ws.onopen = () => console.log('✅ Connected');
ws.onmessage = (e) => console.log('📨 Message:', JSON.parse(e.data));
ws.onerror = (e) => console.error('❌ Error:', e);
ws.onclose = () => console.log('🔌 Disconnected');

// Trigger a test alert by publishing high temperature
// In another terminal:
// docker exec -it iot-app python scripts/publish.py
// (publish temperature > 35°C)
```

### Test 2: Python Test Script

```python
# scripts/test_websocket.py
import asyncio
import websockets
import json

async def test_alerts():
    uri = "ws://localhost:8000/ws/alerts/"
    
    async with websockets.connect(uri) as websocket:
        print("✅ Connected to WebSocket")
        
        # Listen for messages
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"📨 Received: {data}")

if __name__ == "__main__":
    asyncio.run(test_alerts())
```

Run:
```powershell
pip install websockets
python scripts/test_websocket.py
```

---

## 📊 Performance Comparison

### Polling (Current Implementation)
```
Client → HTTP GET /api/readings/latest_all/ (every 5s)
Server → Query Redis → Return JSON
Connections: 1 per 5s per client
```

### WebSocket (New Implementation)
```
Client ←→ WebSocket connection (persistent)
Server → Push alert when threshold exceeded
Connections: 1 persistent per client
```

**Resource usage:**
- **1 user**: WebSocket = Polling (similar)
- **10 users**: WebSocket < Polling (WebSocket wins)
- **100 users**: WebSocket << Polling (WebSocket wins big)

---

## 🎯 Khuyến nghị cuối cùng

### Cho Temperature/Humidity IoT:
✅ **GIỮ NGUYÊN POLLING 5-30s** cho normal readings

✅ **THÊM WebSocket chỉ cho ALERTS** (optional):
- Temperature > 35°C hoặc < 10°C
- Humidity > 80% hoặc < 20%
- Device offline
- Battery low

### Cấu trúc hybrid tối ưu:
```javascript
// Dashboard.jsx
<Dashboard>
  <RealTimeAlerts />        {/* WebSocket - critical alerts only */}
  <LatestReadings />        {/* Polling 5s - normal data */}
  <StatisticsCharts />      {/* Polling 30s - aggregations */}
</Dashboard>
```

**Không over-engineer!** Chỉ thêm WebSocket khi thực sự cần. 🎯
