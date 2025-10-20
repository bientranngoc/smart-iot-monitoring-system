# 🎯 Ứng dụng thực tế: IoT Sensors + Cameras với MediaMTX

## 📋 Tổng quan

Khi kết hợp **IoT sensors** (temperature, humidity) với **IP cameras** thông qua MediaMTX, bạn tạo ra một hệ thống giám sát toàn diện cho nhiều lĩnh vực khác nhau.

---

## 🏭 1. Smart Factory / Nhà máy thông minh

### Bài toán thực tế:

**Giám sát phòng sản xuất điện tử:**
- 🌡️ Temperature sensors → Kiểm tra nhiệt độ khu vực hàn thiếc
- 💧 Humidity sensors → Đảm bảo độ ẩm trong phòng sạch
- 📹 IP Cameras → Giám sát quy trình sản xuất

### Workflow:

```
┌─────────────────────────────────────────────────────┐
│           Smart Factory Monitoring                  │
└─────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
   Temperature      Humidity          Camera
   Sensor 1-5       Sensor 1-5        1-5
        ↓                ↓                ↓
   MQTT Broker      MQTT Broker      RTSP Stream
        ↓                ↓                ↓
    Django API       Django API       MediaMTX
        ↓                ↓                ↓
        └────────────────┴────────────────┘
                         ↓
              React Dashboard
                         ↓
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
   Temperature       Camera View      Alert System
   Charts (5s)       (HLS Stream)    (WebSocket)
```

### Tính năng:

1. **Real-time Monitoring Dashboard**
   ```javascript
   // Dashboard hiển thị đồng thời:
   - Temperature chart theo từng khu vực
   - Humidity trends
   - Live camera feeds từ 5 góc nhà máy
   - Alert khi nhiệt độ vượt ngưỡng
   ```

2. **Alert System**
   ```
   Nếu Temperature > 35°C trong khu vực hàn:
   ├─ WebSocket alert → Dashboard
   ├─ Browser notification
   ├─ Auto record camera tại vị trí đó
   └─ Email/SMS to manager
   ```

3. **Historical Analysis**
   ```
   Xem lại:
   - Temperature trends trong 30 ngày
   - Video recordings khi có alert
   - Correlation giữa nhiệt độ và lỗi sản phẩm
   ```

### Code Example:

```javascript
// src/components/FactoryDashboard.jsx
function FactoryDashboard() {
  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Left: Sensor data */}
      <div className="space-y-4">
        <TemperatureChart zones={['Zone A', 'Zone B', 'Zone C']} />
        <HumidityChart />
        <AlertPanel />
      </div>
      
      {/* Right: Camera grid */}
      <div>
        <CameraGrid cameras={[
          { name: 'Hàn thiếc', stream: 'camera_soldering' },
          { name: 'Lắp ráp', stream: 'camera_assembly' },
          { name: 'Kiểm tra', stream: 'camera_qc' },
          { name: 'Đóng gói', stream: 'camera_packing' }
        ]} />
      </div>
    </div>
  );
}
```

---

## 🏥 2. Hospital / Bệnh viện

### Bài toán thực tế:

**Giám sát phòng bảo quản vaccine/thuốc:**
- 🌡️ Temperature sensors → Nhiệt độ tủ lạnh bảo quản vaccine (-20°C đến -80°C)
- 💧 Humidity sensors → Độ ẩm kho thuốc
- 📹 IP Cameras → Giám sát ra vào kho, chống trộm
- 🚪 Door sensors → Phát hiện cửa mở quá lâu

### Tính năng quan trọng:

1. **Critical Temperature Monitoring**
   ```python
   # monitoring/tasks.py
   VACCINE_TEMP_MIN = -80
   VACCINE_TEMP_MAX = -60
   
   def handle_payload(message):
       # ... existing code ...
       
       if temperature < VACCINE_TEMP_MIN or temperature > VACCINE_TEMP_MAX:
           # CRITICAL ALERT
           trigger_emergency_alert(
               title="⚠️ VACCINE TEMPERATURE CRITICAL!",
               message=f"Freezer {device_id}: {temperature}°C",
               priority="CRITICAL",
               actions=[
                   "notify_manager_immediately",
                   "start_recording_camera",
                   "send_sms_to_on_duty_staff",
                   "log_to_regulatory_system"
               ]
           )
   ```

2. **Compliance & Audit Trail**
   ```javascript
   // Dashboard hiển thị:
   - Temperature logs (bắt buộc theo quy định FDA/WHO)
   - Video recordings (chứng minh không ai mở tủ lạnh)
   - Alert history (khi nào có sự cố)
   - Staff access logs (ai vào kho, khi nào)
   ```

3. **24/7 Monitoring Dashboard**
   ```javascript
   // src/components/HospitalDashboard.jsx
   function HospitalDashboard() {
     return (
       <div className="space-y-6">
         {/* Critical temperature monitors */}
         <div className="grid grid-cols-3 gap-4">
           <FreezerMonitor 
             name="Vaccine Freezer A" 
             minTemp={-80} 
             maxTemp={-60}
             camera="camera_freezer_a"
           />
           <FreezerMonitor 
             name="Vaccine Freezer B"
             minTemp={-80} 
             maxTemp={-60}
             camera="camera_freezer_b"
           />
           <FridgeMonitor 
             name="Medicine Fridge"
             minTemp={2} 
             maxTemp={8}
             camera="camera_fridge"
           />
         </div>
         
         {/* Camera surveillance */}
         <CameraGrid cameras={[
           { name: 'Kho vaccine', stream: 'camera_vaccine_storage' },
           { name: 'Lối vào kho', stream: 'camera_entrance' },
           { name: 'Khu vực chuẩn bị', stream: 'camera_prep' }
         ]} />
         
         {/* Compliance reports */}
         <ComplianceReport period="24h" />
       </div>
     );
   }
   ```

---

## 🏪 3. Cold Storage / Kho lạnh thực phẩm

### Bài toán thực tế:

**Giám sát kho lạnh bảo quản thực phẩm:**
- 🌡️ Temperature sensors → Nhiệt độ các khu vực khác nhau
- 💧 Humidity sensors → Độ ẩm (quan trọng cho thực phẩm đông lạnh)
- 📹 IP Cameras → Giám sát hoạt động, chống trộm
- 🚪 Door sensors → Cảnh báo cửa mở

### Use cases:

1. **Multi-zone Temperature Control**
   ```javascript
   const ZONES = [
     { name: 'Thịt đông lạnh', temp: -18, camera: 'camera_frozen_meat' },
     { name: 'Rau củ ướp lạnh', temp: 4, camera: 'camera_vegetables' },
     { name: 'Hải sản', temp: -25, camera: 'camera_seafood' },
     { name: 'Sản phẩm sữa', temp: 2, camera: 'camera_dairy' }
   ];
   
   // Dashboard hiển thị tất cả zones
   <ZoneGrid zones={ZONES} />
   ```

2. **Inventory Management với Camera AI**
   ```javascript
   // Tương lai có thể thêm AI
   - Camera detect khi hàng sắp hết
   - Temperature sensor + camera = Phát hiện cửa mở quá lâu
   - Tự động alert khi nhiệt độ tăng + camera thấy có người
   ```

3. **Energy Optimization**
   ```javascript
   // Phân tích:
   - Khi nào nhiệt độ tăng (cửa mở)
   - Thời gian cửa mở trung bình
   - Correlation với hóa đơn điện
   ```

---

## 🏠 4. Smart Building / Tòa nhà thông minh

### Bài toán thực tế:

**Quản lý tòa nhà văn phòng:**
- 🌡️ Temperature sensors → HVAC control (điều hòa)
- 💧 Humidity sensors → Air quality
- 📹 IP Cameras → Security, parking, entrance
- 💡 Light sensors → Auto lighting

### Dashboard tổng hợp:

```javascript
// src/components/SmartBuildingDashboard.jsx
function SmartBuildingDashboard() {
  return (
    <div className="space-y-6">
      {/* Building overview */}
      <BuildingMap 
        floors={10}
        sensorsPerFloor={5}
        camerasPerFloor={3}
      />
      
      {/* Environmental controls */}
      <div className="grid grid-cols-2 gap-4">
        <EnvironmentPanel 
          title="Floor 1 - Lobby"
          temperature={22}
          humidity={55}
          camera="camera_lobby"
        />
        <EnvironmentPanel 
          title="Floor 5 - Server Room"
          temperature={18}
          humidity={45}
          camera="camera_server_room"
          critical={true}
        />
      </div>
      
      {/* Security cameras */}
      <SecurityCameraGrid cameras={[
        { name: 'Main Entrance', stream: 'camera_entrance' },
        { name: 'Parking Lot', stream: 'camera_parking' },
        { name: 'Emergency Exit', stream: 'camera_emergency' },
        { name: 'Server Room', stream: 'camera_server' }
      ]} />
      
      {/* Energy dashboard */}
      <EnergyConsumption 
        hvacStatus="auto"
        currentLoad="450 kW"
        prediction="Optimize by 15%"
      />
    </div>
  );
}
```

### Automation Logic:

```python
# monitoring/automation.py
def smart_building_automation():
    """
    Tự động hóa dựa trên sensors + cameras
    """
    
    # Rule 1: HVAC Control
    if temperature > 26 and humidity > 70:
        # Turn on AC
        hvac.set_temperature(24)
        # Record camera to see if windows are open
        camera.start_recording('camera_room_a')
    
    # Rule 2: Security
    if motion_detected and temperature_abnormal:
        # Possible fire or intrusion
        camera.start_recording('all_cameras')
        send_alert('Security team')
    
    # Rule 3: Energy Saving
    if no_motion_detected_for('30_minutes'):
        # Turn off lights
        lights.off()
        # Keep camera on (security)
        camera.mode = 'low_power'
```

---

## 🌾 5. Smart Agriculture / Nông nghiệp thông minh

### Bài toán thực tế:

**Giám sát nhà kính trồng rau sạch:**
- 🌡️ Temperature sensors → Nhiệt độ nhà kính
- 💧 Humidity sensors → Độ ẩm đất, không khí
- 📹 IP Cameras → Giám sát cây trồng, phát hiện sâu bệnh
- 💦 Soil moisture sensors → Tự động tưới

### Smart Greenhouse Dashboard:

```javascript
// src/components/GreenhouseDashboard.jsx
function GreenhouseDashboard() {
  return (
    <div className="space-y-6">
      <h2>🌿 Smart Greenhouse Control</h2>
      
      {/* Environmental conditions */}
      <div className="grid grid-cols-3 gap-4">
        <MetricCard 
          icon="🌡️"
          label="Temperature"
          value={28}
          optimal={[20, 30]}
          unit="°C"
        />
        <MetricCard 
          icon="💧"
          label="Humidity"
          value={65}
          optimal={[60, 80]}
          unit="%"
        />
        <MetricCard 
          icon="💦"
          label="Soil Moisture"
          value={75}
          optimal={[70, 85]}
          unit="%"
        />
      </div>
      
      {/* Camera monitoring */}
      <CameraGrid cameras={[
        { name: 'Khu A - Rau xà lách', stream: 'camera_lettuce' },
        { name: 'Khu B - Cà chua', stream: 'camera_tomato' },
        { name: 'Hệ thống tưới', stream: 'camera_irrigation' },
        { name: 'Tổng quan', stream: 'camera_overview' }
      ]} />
      
      {/* AI Analysis (future) */}
      <PlantHealthAnalysis 
        camera="camera_lettuce"
        aiModel="plant-disease-detection"
      />
      
      {/* Automation controls */}
      <AutomationPanel 
        irrigation="auto"
        ventilation="auto"
        lighting="scheduled"
      />
    </div>
  );
}
```

### Automation với AI:

```python
# monitoring/greenhouse_ai.py
def greenhouse_automation():
    """
    Kết hợp sensors + camera với AI
    """
    
    # Temperature + Humidity → Control ventilation
    if temperature > 32 or humidity > 85:
        ventilation.open()
        fans.turn_on()
    
    # Soil moisture → Auto irrigation
    if soil_moisture < 70:
        irrigation.start()
        camera.record('camera_irrigation')  # Record for audit
    
    # Camera AI → Detect plant disease
    camera_image = camera.get_frame('camera_lettuce')
    disease_detected = ai_model.detect_disease(camera_image)
    
    if disease_detected:
        send_alert(
            title="🐛 Plant Disease Detected!",
            image=camera_image,
            location="Khu A - Rau xà lách",
            recommendation="Apply pesticide XYZ"
        )
```

---

## 🏬 6. Retail Store / Cửa hàng

### Bài toán thực tế:

**Giám sát cửa hàng tiện lợi:**
- 🌡️ Temperature sensors → Tủ lạnh đồ uống, tủ đông
- 💧 Humidity sensors → Kho hàng
- 📹 IP Cameras → Security, customer behavior
- 🚪 Door sensors → Customer counting

### Retail Dashboard:

```javascript
// src/components/RetailDashboard.jsx
function RetailDashboard() {
  return (
    <div className="space-y-6">
      {/* Refrigeration monitoring */}
      <div className="grid grid-cols-4 gap-4">
        <FridgeMonitor name="Tủ lạnh 1" temp={4} camera="camera_fridge1" />
        <FridgeMonitor name="Tủ lạnh 2" temp={5} camera="camera_fridge2" />
        <FreezerMonitor name="Tủ đông" temp={-18} camera="camera_freezer" />
        <ACMonitor name="Điều hòa" temp={24} camera="camera_store" />
      </div>
      
      {/* Security cameras */}
      <CameraGrid cameras={[
        { name: 'Quầy thu ngân', stream: 'camera_cashier' },
        { name: 'Lối vào', stream: 'camera_entrance' },
        { name: 'Khu vực hàng hóa', stream: 'camera_products' },
        { name: 'Kho', stream: 'camera_storage' }
      ]} />
      
      {/* Analytics */}
      <CustomerAnalytics 
        footTraffic={245}  // From camera AI
        avgTemperature={24}
        energyCost={150000}
      />
    </div>
  );
}
```

---

## 🏭 7. Data Center / Trung tâm dữ liệu

### Bài toán thực tế:

**Giám sát server room:**
- 🌡️ Temperature sensors → Server racks (must be 18-24°C)
- 💧 Humidity sensors → Prevent condensation
- 📹 IP Cameras → Security, compliance
- 🔥 Smoke detectors → Fire prevention

### Critical Monitoring:

```javascript
// src/components/DataCenterDashboard.jsx
function DataCenterDashboard() {
  return (
    <div className="space-y-6">
      {/* Rack-level monitoring */}
      <div className="grid grid-cols-5 gap-2">
        {Array.from({length: 20}, (_, i) => (
          <ServerRackMonitor 
            key={i}
            rackId={i + 1}
            temperature={19 + Math.random() * 4}
            humidity={45 + Math.random() * 10}
            camera={`camera_rack_${i + 1}`}
            critical={true}
          />
        ))}
      </div>
      
      {/* Security cameras */}
      <CameraGrid cameras={[
        { name: 'Main Entrance (Biometric)', stream: 'camera_entrance' },
        { name: 'Server Rows 1-5', stream: 'camera_rows_1_5' },
        { name: 'Server Rows 6-10', stream: 'camera_rows_6_10' },
        { name: 'Cooling System', stream: 'camera_cooling' },
        { name: 'Power Distribution', stream: 'camera_power' }
      ]} />
      
      {/* Critical alerts */}
      <CriticalAlertPanel 
        temperature={true}
        humidity={true}
        smoke={true}
        motion={true}
        door={true}
      />
    </div>
  );
}
```

---

## 🎯 Tổng hợp: Lợi ích khi kết hợp Sensors + Cameras

### 1. **Complete Visibility**
```
Sensors → Số liệu định lượng (nhiệt độ, độ ẩm)
Cameras → Xác minh trực quan (ai làm gì, khi nào)
```

### 2. **Root Cause Analysis**
```
Alert: Temperature spike at 3:00 AM
Sensors: Show temperature increased from 22°C → 35°C
Cameras: Video shows someone opened server room door
Result: Human error identified, training needed
```

### 3. **Compliance & Audit**
```
Regulatory requirement: Prove vaccine storage compliance
Sensors: Temperature logs every minute for 365 days
Cameras: Video proof no unauthorized access
Result: Pass FDA audit
```

### 4. **Automation Opportunities**
```
Condition: Temperature > 30°C + Motion detected
Action 1: Turn on AC
Action 2: Start recording camera
Action 3: Send alert to facility manager
Action 4: Log incident for analysis
```

### 5. **Cost Optimization**
```
Analysis:
- Temperature data → HVAC efficiency
- Camera data → Occupancy patterns
- Combined → Smart HVAC scheduling
Result: 20% energy cost reduction
```

---

## 💡 Architecture tổng hợp

```
┌─────────────────────────────────────────────────────────┐
│         Complete IoT + Video Monitoring System          │
└─────────────────────────────────────────────────────────┘
                           ↓
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
   IoT Sensors        IP Cameras        Other Devices
   (MQTT)             (RTSP)            (Modbus, etc)
        ↓                  ↓                  ↓
    Kafka              MediaMTX           Django API
        ↓                  ↓                  ↓
   ┌────┴────┬─────────────┼─────────────┬───┴────┐
   ↓         ↓             ↓             ↓        ↓
MySQL    MongoDB    OpenSearch        Redis    HLS/WebRTC
(Meta)   (History)  (Search)         (Cache)   (Streaming)
   ↓         ↓             ↓             ↓        ↓
   └─────────┴─────────────┴─────────────┴────────┘
                           ↓
                  Django REST API
                           ↓
                  React Dashboard
                           ↓
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
   Sensor Charts      Camera Grid       Alerts
   (Polling 5s)       (HLS Stream)     (WebSocket)
```

---

## 🚀 ROI (Return on Investment)

### Smart Factory Example:
- **Investment:** $50,000 (sensors + cameras + system)
- **Benefits:**
  - Reduce defects by 30% (identify temperature issues) → Save $200,000/year
  - Prevent equipment damage (early warning) → Save $100,000/year
  - Improve efficiency 15% (data-driven decisions) → Save $150,000/year
- **ROI:** 900% in first year

### Hospital Example:
- **Investment:** $30,000 (critical monitoring system)
- **Benefits:**
  - Prevent vaccine loss (1 incident = $500,000 loss) → Priceless
  - Compliance with regulations → Avoid fines
  - Peace of mind → Staff can focus on patients
- **ROI:** Immeasurable (risk prevention)

---

## 🎯 Kết luận

### MediaMTX + IoT Sensors tạo nên hệ thống giám sát toàn diện:

✅ **Sensors** → Dữ liệu định lượng chính xác
✅ **Cameras** → Xác minh trực quan, security
✅ **Combined** → Root cause analysis, compliance, automation

### Ứng dụng thực tế:
1. 🏭 Smart Factory - Giám sát sản xuất
2. 🏥 Hospital - Bảo quản vaccine/thuốc
3. 🏪 Cold Storage - Kho lạnh thực phẩm
4. 🏠 Smart Building - Tòa nhà thông minh
5. 🌾 Agriculture - Nhà kính thông minh
6. 🏬 Retail - Cửa hàng
7. 🏭 Data Center - Server room

**Không chỉ là monitoring, mà là complete management system!** 🎯🚀
