# Hướng dẫn chạy IoT Monitoring System

## ✅ Vấn đề đã tìm ra

**Nguyên nhân:** `scripts/consumer.py` chỉ **print** message ra console mà KHÔNG gọi `handle_payload()` để ghi vào database!

**Đã sửa:** Thêm logic gọi `handle_payload()` vào `scripts/consumer.py`

## 🚀 Cách chạy hệ thống

### **Cách 1: Dùng Celery (KHUYẾN NGHỊ - Đơn giản nhất)**

Celery worker tự động start cả MQTT subscriber và Kafka consumer trong background threads.

#### Bước 1: Start Celery worker
```powershell
docker exec -it iot-app celery -A smart_iot worker --loglevel=debug
```

**Log bạn sẽ thấy:**
```
[INFO] MQTT & Kafka streams started.
```

#### Bước 2: Publish test data (terminal mới)
```powershell
docker exec -it iot-app python scripts/publish.py
```

#### Bước 3: Kiểm tra logs
Trong terminal Celery worker, bạn sẽ thấy:
```
[INFO] MQTT -> {"device_id": 1, "temperature": 25.5, ...}
[INFO] === handle_payload CALLED === payload: {...}
[INFO] User get_or_create: username=default_user, id=X, created=True/False
[INFO] Device get_or_create: name=Device 1, id=Y, created=True/False
```

#### Bước 4: Verify data trong MySQL
```powershell
docker exec -it iot-mysql mysql -u user -ppassword smart_iot -e "SELECT * FROM users; SELECT * FROM devices;"
```

---

### **Cách 2: Dùng scripts riêng biệt (Đã sửa consumer.py)**

Nếu muốn chạy từng component riêng lẻ thay vì dùng Celery.

#### Bước 1: Start MQTT subscriber (Terminal 1)
```powershell
docker exec -it iot-app python -m scripts.mqtt_worker
```

**Output:**
```
MQTT Subscriber running...
```

#### Bước 2: Start Kafka consumer (Terminal 2)
```powershell
docker exec -it iot-app python scripts/consumer.py
```

**Output:**
```
Kafka consumer started, waiting for messages...
```

#### Bước 3: Publish test data (Terminal 3)
```powershell
docker exec -it iot-app python scripts/publish.py
```

**Output:**
```
Published: {"device_id": 1, "temperature": 25.5, ...}
Published: {"device_id": 2, "temperature": 23.1, ...}
...
```

#### Bước 4: Kiểm tra logs
Trong **Terminal 2 (consumer.py)**, bạn sẽ thấy:
```
Received from Kafka: {"device_id": 1, ...}
2025-10-20 03:24:12,281 [INFO] === handle_payload CALLED === payload: {...}
2025-10-20 03:24:12,286 [INFO] User get_or_create: username=default_user, id=2, created=True
2025-10-20 03:24:12,291 [INFO] Device get_or_create: name=Device 1, id=3, created=True
✓ Processed payload successfully
```

#### Bước 5: Verify data trong MySQL
```powershell
docker exec -it iot-mysql mysql -u user -ppassword smart_iot -e "SELECT * FROM users; SELECT * FROM devices;"
```

---

## 📊 Flow hoạt động

```
IoT Devices (publish.py)
    ↓ publish JSON
MQTT Broker (iot-mosquitto) - topic: sensors/data
    ↓ subscribe
MQTT Worker (on_message)
    ↓ send_to_kafka()
Kafka Broker (iot-kafka) - topic: raw-data
    ↓ consume
Kafka Consumer (run_kafka_consumer / consumer.py)
    ↓ handle_payload()
    ├─→ MySQL (User, Device via Django ORM)
    └─→ MongoDB (Reading via pymongo)
```

---

## 🐛 Debug/Troubleshooting

### Không thấy data trong MySQL?

#### 1. Kiểm tra xem handle_payload() có được gọi không:
```powershell
# Trong logs (Celery hoặc consumer.py), tìm dòng này:
=== handle_payload CALLED === payload: ...
```

Nếu **KHÔNG có** → MQTT/Kafka pipeline không hoạt động
Nếu **CÓ** → Data đã được ghi, kiểm tra DB

#### 2. Test trực tiếp:
```powershell
docker exec -it iot-app python scripts/test_db_write.py
```

#### 3. Kiểm tra MySQL trực tiếp:
```powershell
docker exec -it iot-mysql mysql -u user -ppassword smart_iot
```

```sql
SHOW TABLES;
SELECT * FROM users;
SELECT * FROM devices;
SELECT COUNT(*) FROM devices;
```

#### 4. Xem logs của tất cả containers:
```powershell
docker logs iot-app -f
docker logs iot-mosquitto -f
docker logs iot-kafka -f
docker logs iot-mysql -f
```

---

## 🎯 So sánh 2 cách

| Feature | Celery Worker | Scripts riêng |
|---------|--------------|---------------|
| Số terminals cần | 2 | 3 |
| Auto-start streams | ✅ | ❌ (phải start thủ công) |
| Task scheduling | ✅ | ❌ |
| Production-ready | ✅ | ❌ |
| Dễ debug | ❌ (logs lẫn nhau) | ✅ (logs riêng biệt) |
| Khuyến nghị | **Development & Production** | **Testing từng component** |

---

## ✅ Checklist trước khi chạy

- [ ] Docker containers đang chạy: `docker ps`
- [ ] Celery worker hoặc MQTT/Kafka consumers đang chạy
- [ ] Thấy log "MQTT & Kafka streams started" hoặc "MQTT Subscriber running"
- [ ] Chạy `publish.py`
- [ ] Kiểm tra logs có `=== handle_payload CALLED ===`
- [ ] Verify MySQL: `SELECT * FROM devices;`

---

## 🎉 Expected Results

Sau khi chạy `publish.py` (gửi 10 messages với device_id từ 1-5):

### MySQL:
```
mysql> SELECT * FROM users;
+----+---------------+---------------------+
| id | username      | created_at          |
+----+---------------+---------------------+
|  1 | default_user  | 2025-10-20 03:24:12 |
+----+---------------+---------------------+

mysql> SELECT * FROM devices;
+----+-----------+---------+---------------------+
| id | name      | user_id | created_at          |
+----+-----------+---------+---------------------+
|  1 | Device 1  |       1 | 2025-10-20 03:24:12 |
|  2 | Device 2  |       1 | 2025-10-20 03:24:14 |
|  3 | Device 3  |       1 | 2025-10-20 03:24:16 |
|  4 | Device 4  |       1 | 2025-10-20 03:24:18 |
|  5 | Device 5  |       1 | 2025-10-20 03:24:20 |
+----+-----------+---------+---------------------+
```

### MongoDB:
```
> db.readings.count()
10

> db.readings.findOne()
{
    "_id": ObjectId("..."),
    "device_id": 1,
    "temperature": 25.5,
    "humidity": 60.0,
    "timestamp": ISODate("2025-10-20T03:24:12.000Z")
}
```
