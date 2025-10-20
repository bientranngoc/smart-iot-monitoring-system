# Hướng dẫn Debug: Tại sao không có dữ liệu trong MySQL?

## Vấn đề
Chạy full flow: `mqtt_subscribe_task`, `kafka_consumer_task`, rồi `publish.py` nhưng trong MySQL không có dữ liệu devices.

## Các thay đổi đã thực hiện

1. **Thêm debug logging vào `monitoring/tasks.py`**:
   - Log khi `handle_payload()` được gọi
   - Log dữ liệu JSON đã parse
   - Log kết quả `User.objects.get_or_create()`
   - Log kết quả `Device.objects.get_or_create()`
   - Log kết quả insert vào MongoDB
   - Đổi logging level từ INFO sang DEBUG

2. **Tạo script test độc lập: `scripts/test_db_write.py`**
   - Test kết nối database
   - Test tạo User
   - Test tạo Device
   - Test gọi `handle_payload()` trực tiếp
   - Test transaction settings

## Cách chạy để debug

### Bước 1: Chạy script test độc lập (QUAN TRỌNG NHẤT)

```powershell
docker exec -it iot-app python scripts/test_db_write.py
```

Script này sẽ:
- Kiểm tra kết nối MySQL
- Test tạo User và Device trực tiếp
- Gọi `handle_payload()` với dữ liệu mẫu
- Hiển thị tất cả bảng, users, devices trong DB

**Hãy gửi OUTPUT của lệnh này cho tôi!**

### Bước 2: Kiểm tra logs của Celery worker

Nếu bạn đang chạy Celery worker:

```powershell
# Xem logs của container
docker logs iot-app -f
```

Hoặc nếu chạy worker thủ công:

```powershell
docker exec -it iot-app celery -A smart_iot worker -l DEBUG
```

Tìm các dòng log sau khi chạy `publish.py`:
- `=== handle_payload CALLED ===`
- `Parsed JSON data:`
- `User get_or_create:`
- `Device get_or_create:`
- `MongoDB insert result:`

### Bước 3: Chạy manual test trong Django shell

```powershell
docker exec -it iot-app python manage.py shell
```

Trong shell:

```python
from monitoring.tasks import handle_payload
import json
from datetime import datetime

# Test với payload mẫu
payload = json.dumps({
    "device_id": 99,
    "temperature": 25.5,
    "humidity": 60.0,
    "timestamp": datetime.now().isoformat()
})

print("Calling handle_payload...")
handle_payload(payload)

# Kiểm tra kết quả
from monitoring.models import User, Device
print(f"Users: {User.objects.all().values_list('username', flat=True)}")
print(f"Devices: {Device.objects.all().values_list('name', flat=True)}")
```

### Bước 4: Kiểm tra trực tiếp trong MySQL

```powershell
# Vào MySQL container
docker exec -it iot-mysql mysql -u user -ppassword smart_iot

# Trong MySQL shell:
SHOW TABLES;
SELECT * FROM users;
SELECT * FROM devices;
```

## Các nguyên nhân có thể

### 1. handle_payload() không được gọi
**Triệu chứng**: Không thấy log `=== handle_payload CALLED ===`

**Nguyên nhân**:
- MQTT/Kafka stream không chạy
- Message không đến Kafka consumer
- Thread bị lỗi im lặng

**Giải pháp**: Chạy `test_db_write.py` để test trực tiếp function

### 2. Transaction không được commit
**Triệu chứng**: Function chạy xong nhưng data không có trong DB

**Nguyên nhân**:
- Django autocommit bị tắt
- Thread không commit transaction
- Database connection issue

**Giải pháp**: Thêm explicit commit hoặc dùng `@transaction.atomic`

### 3. Database routing issue
**Nguyên nhân**: Nếu có database router, User/Device có thể được ghi vào DB khác

**Giải pháp**: Kiểm tra settings.py cho DATABASE_ROUTERS

### 4. Exception bị nuốt
**Nguyên nhân**: Try/except có thể nuốt lỗi ORM

**Giải pháp**: Debug logging đã thêm sẽ hiện exception

### 5. Model/Migration mismatch
**Nguyên nhân**: Migration chưa chạy hoặc model thực tế khác code

**Giải pháp**: 
```powershell
docker exec -it iot-app python manage.py showmigrations
docker exec -it iot-app python manage.py migrate
```

## Điều tôi cần từ bạn

Hãy chạy **Bước 1** (`scripts/test_db_write.py`) và gửi toàn bộ output. 

Nó sẽ cho tôi biết chính xác vấn đề nằm ở đâu:
- Database connection?
- ORM operations?
- Transaction/commit?
- handle_payload() logic?

Sau khi có output, tôi sẽ biết chính xác cách sửa!
