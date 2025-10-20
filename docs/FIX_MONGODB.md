# Fix MongoDB Connection - Quick Guide

## ✅ Đã sửa

1. **Thêm MongoDB config vào `.env`:**
   ```
   MONGODB_URI=mongodb://root:root@iot-mongodb:27017/
   MONGODB_DB_NAME=iot
   ```

2. **Thêm MongoDB settings vào `smart_iot/settings.py`:**
   ```python
   MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://root:root@iot-mongodb:27017/')
   MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'iot')
   ```

3. **Cải thiện error logging trong `ReadingClient`**

4. **Tạo script test: `scripts/test_mongodb.py`**

---

## 🚀 Cách test MongoDB

### Bước 1: Test connection trước
```powershell
docker exec -it iot-app python scripts/test_mongodb.py
```

**Expected output:**
```
MongoDB Connection Test
Settings:
  MONGODB_URI: mongodb://root:root@iot-mongodb:27017/
  MONGODB_DB_NAME: iot

1. Testing ReadingClient connection...
   ✓ Connected to MongoDB!
   ✓ Database: iot
   
2. Testing insert_reading()...
   ✓ Insert successful! ID: 67xxxxxx

3. Testing find_readings()...
   ✓ Found 1 readings for device_id=999
```

### Bước 2: Restart consumer để load config mới

**Nếu đang dùng scripts:**

Dừng consumer cũ (Ctrl+C) và chạy lại:
```powershell
docker exec -it iot-app python scripts/consumer.py
```

**Nếu đang dùng Celery:**

Restart Celery worker:
```powershell
# Ctrl+C để stop worker cũ
docker exec -it iot-app celery -A smart_iot worker --loglevel=debug
```

### Bước 3: Publish data
```powershell
docker exec -it iot-app python scripts/publish.py
```

### Bước 4: Check MongoDB

Vào MongoDB shell:
```powershell
docker exec -it iot-mongodb mongosh -u root -p root
```

Trong MongoDB shell:
```javascript
use iot
db.readings.count()
db.readings.find().limit(5)
db.readings.aggregate([
  {$group: {_id: "$device_id", count: {$sum: 1}}},
  {$sort: {_id: 1}}
])
```

---

## 🐛 Nếu vẫn không hoạt động

### Check 1: MongoDB container đang chạy?
```powershell
docker ps | findstr mongodb
```

### Check 2: Test connection từ container
```powershell
docker exec -it iot-app python -c "from pymongo import MongoClient; client = MongoClient('mongodb://root:root@iot-mongodb:27017/'); print(client.server_info())"
```

### Check 3: Xem logs MongoDB
```powershell
docker logs iot-mongodb --tail 50
```

### Check 4: Xem error trong consumer logs
Logs phải show lỗi cụ thể giờ:
```
[ERROR] PyMongoError in insert_reading: <error message>
```

---

## 📊 Expected Results

Sau khi publish 10 messages:

### MySQL (users & devices):
```sql
SELECT COUNT(*) FROM devices;  -- 5 devices (device_id 1-5)
```

### MongoDB (readings):
```javascript
db.readings.count()  // 10 readings
db.readings.aggregate([{$group: {_id: "$device_id", count: {$sum: 1}}}])
// Kết quả: 10 readings phân bố cho device_id 1-5
```

---

## ✅ Checklist

- [ ] `.env` có `MONGODB_URI` và `MONGODB_DB_NAME`
- [ ] `settings.py` có MongoDB config
- [ ] `docker ps` show `iot-mongodb` đang chạy
- [ ] `test_mongodb.py` chạy thành công
- [ ] Restart consumer/worker để load config mới
- [ ] Publish data
- [ ] Check MongoDB có readings
