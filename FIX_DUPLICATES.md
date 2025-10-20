# Giải quyết vấn đề Duplicate Data trong MongoDB

## 🔍 Vấn đề

Bạn đã phát hiện đúng: **Dữ liệu bị trùng lặp nhiều** trong MongoDB readings collection.

### Nguyên nhân:
1. **Kafka consumer offset `'earliest'`**: Mỗi lần restart consumer → đọc lại TẤT CẢ messages từ đầu Kafka topic
2. **Không có unique constraint**: MongoDB cho phép insert cùng reading nhiều lần
3. **Multiple consumers**: Nếu chạy nhiều consumer instance → duplicate processing

---

## ✅ Các giải pháp đã áp dụng

### 1. **Thêm Unique Compound Index trong MongoDB**

**File:** `monitoring/models.py` → `ReadingClient._connect()`

```python
# Tự động tạo index (device_id, timestamp) UNIQUE
self._collection.create_index(
    [("device_id", 1), ("timestamp", 1)],
    unique=True,
    background=True
)
```

**Kết quả:**
- ✅ MongoDB TỰ ĐỘNG reject duplicate readings (cùng device_id + timestamp)
- ✅ Không cần logic phức tạp trong code
- ✅ Insert trùng → PyMongoError → log debug và tiếp tục

### 2. **Đổi Kafka offset reset: `earliest` → `latest`**

**Files:** `scripts/consumer.py`, `monitoring/tasks.py`

```python
'auto.offset.reset': 'latest'  # Chỉ đọc message MỚI từ lúc consumer start
```

**Kết quả:**
- ✅ Restart consumer → KHÔNG đọc lại messages cũ
- ✅ Chỉ process messages mới publish sau khi consumer start
- ⚠️ Lưu ý: Nếu consumer down → messages trong thời gian đó bị miss (trừ khi Kafka retention còn)

### 3. **Cải thiện Error Handling**

**File:** `monitoring/models.py` → `insert_reading()`

```python
except PyMongoError as e:
    if 'duplicate key error' in str(e).lower():
        logging.debug("Duplicate reading ignored")  # DEBUG level, không spam logs
        return None
    logging.error(f"PyMongoError: {e}")  # ERROR level cho lỗi thật
```

**Kết quả:**
- ✅ Duplicate → log level DEBUG (không spam)
- ✅ Lỗi khác → log level ERROR

---

## 🛠️ Script làm sạch duplicates hiện tại

**File:** `scripts/clean_duplicates.py`

### Chạy script:
```powershell
docker exec -it iot-app python scripts/clean_duplicates.py
```

### Script sẽ:
1. ✅ Đếm tổng readings và phân bố theo device
2. ✅ Tìm duplicates (cùng device_id + timestamp)
3. ✅ Xóa duplicates (giữ lại 1 bản ghi đầu tiên)
4. ✅ Tạo unique index
5. ✅ Hiển thị kết quả sau khi clean

**Output mẫu:**
```
Current statistics:
  Total readings: 150

Finding duplicates...
  Found 50 groups of duplicates

Removing duplicates...
  ✓ Removed 100 duplicates
  
Final statistics:
  Total readings: 50
  Removed: 100
```

---

## 🎯 So sánh các phương pháp

| Phương pháp | Ưu điểm | Nhược điểm | Khuyến nghị |
|-------------|---------|------------|-------------|
| **Unique Index** | • Đảm bảo 100% không duplicate<br>• Tự động, không cần code<br>• Performance tốt | • Cần cleanup duplicates cũ trước | ✅ **KHUYẾN NGHỊ** |
| **Offset 'latest'** | • Giảm duplicate khi restart | • Miss messages nếu consumer down<br>• Không ngăn duplicate 100% | ⚠️ Kết hợp với index |
| **Idempotent insert** | • Application-level control | • Cần check exist trước insert<br>• Chậm hơn | ❌ Không cần nếu có index |
| **Message deduplication** | • Ngăn duplicate ở source | • Phức tạp<br>• Cần thêm cache/storage | ❌ Overkill |

---

## 📊 Kiến trúc Data Storage

### Tại sao tách MySQL và MongoDB?

| Database | Data Type | Đặc điểm | Use Case |
|----------|-----------|----------|----------|
| **MySQL** | Metadata | • Structured<br>• ACID transactions<br>• Relations (User → Device) | • Quản lý users<br>• Quản lý devices<br>• Authentication<br>• Device ownership |
| **MongoDB** | Time-series | • Schema-flexible<br>• High write throughput<br>• Horizontal scaling | • Sensor readings<br>• Logs<br>• Analytics<br>• Historical data |

### Làm sao tránh duplicate?

#### MySQL (Users, Devices):
```python
User.objects.get_or_create(username='default_user')  # Django ORM handle duplicate
Device.objects.get_or_create(name='Device 1')        # Database unique constraint
```
✅ **Không duplicate** - Django ORM + DB constraints

#### MongoDB (Readings):
```python
# Trước khi fix:
collection.insert_one(doc)  # Có thể duplicate ❌

# Sau khi fix (với unique index):
collection.insert_one(doc)  # Tự động reject duplicate ✅
```

---

## 🚀 Các bước triển khai

### Bước 1: Clean duplicates hiện tại
```powershell
docker exec -it iot-app python scripts/clean_duplicates.py
```

### Bước 2: Restart consumer để áp dụng offset mới
```powershell
# Dừng consumer cũ (Ctrl+C)
docker exec -it iot-app python scripts/consumer.py
```

### Bước 3: Test với data mới
```powershell
# Xóa topic để test clean
docker exec -it iot-kafka kafka-topics --bootstrap-server localhost:9092 --delete --topic raw-data
docker exec -it iot-kafka kafka-topics --bootstrap-server localhost:9092 --create --topic raw-data --partitions 1 --replication-factor 1

# Publish data mới
docker exec -it iot-app python scripts/publish.py
```

### Bước 4: Verify không có duplicate
```powershell
docker exec -it iot-mongodb mongosh -u root -p root --eval "
use iot;
db.readings.count();
db.readings.aggregate([
  {\$group: {
    _id: {\$concat: [{\$toString: '\$device_id'}, '-', {\$toString: '\$timestamp'}]},
    count: {\$sum: 1}
  }},
  {\$match: {count: {\$gt: 1}}}
]);
"
```

**Expected:** Không có duplicate!

---

## 🎯 Best Practices đã áp dụng

### 1. **Idempotency**
- MongoDB unique index → duplicate insert = no-op
- Kafka offset commit → message chỉ process 1 lần (nếu consumer stable)

### 2. **Data Integrity**
- MySQL foreign keys (User → Device)
- MongoDB unique compound index (device_id, timestamp)

### 3. **Error Handling**
- Duplicate → DEBUG log (không spam)
- Real errors → ERROR log
- Graceful degradation

### 4. **Monitoring**
- Log inserted_id để track success
- Count by device để detect anomalies
- Test scripts để verify integrity

---

## 📈 Kết quả mong đợi

### Trước khi fix:
```javascript
db.readings.count()  // 150 (có 100 duplicates)
```

### Sau khi fix:
```javascript
db.readings.count()  // 50 (unique readings only)

// Try insert duplicate manually:
db.readings.insertOne({device_id: 1, temperature: 25, humidity: 60, timestamp: ISODate("2025-10-20T04:00:00Z")})
db.readings.insertOne({device_id: 1, temperature: 25, humidity: 60, timestamp: ISODate("2025-10-20T04:00:00Z")})
// → Error: E11000 duplicate key error ✅
```

---

## 🔍 Troubleshooting

### Vẫn thấy duplicates sau khi fix?

1. **Check index đã tạo chưa:**
```javascript
db.readings.getIndexes()
// Phải có: { device_id: 1, timestamp: 1 } unique: true
```

2. **Check offset đã đổi chưa:**
```python
# Trong consumer.py hoặc tasks.py
'auto.offset.reset': 'latest'  # Phải là 'latest'
```

3. **Check có chạy nhiều consumer không:**
```powershell
docker ps | findstr consumer
# Chỉ nên có 1 consumer cho 1 group_id
```

4. **Reset Kafka consumer group nếu cần:**
```powershell
docker exec -it iot-kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group iot-group --reset-offsets --to-latest --topic raw-data --execute
```

---

## ✅ Checklist

- [ ] Chạy `clean_duplicates.py` để xóa duplicates cũ
- [ ] Verify unique index đã tạo trong MongoDB
- [ ] Đổi `auto.offset.reset` thành `'latest'`
- [ ] Restart consumer với config mới
- [ ] Test publish → không có duplicate
- [ ] Monitor logs không thấy spam "duplicate key error"

---

Hệ thống giờ đã có **deduplication tự động**! 🎉
