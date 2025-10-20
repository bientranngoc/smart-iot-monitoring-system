import os
import sys
import django

# Setup Django để có thể import models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_iot.settings')
django.setup()

from confluent_kafka import Consumer, KafkaError
from monitoring.tasks import handle_payload  # Import hàm xử lý payload

KAFKA_BOOTSTRAP = 'iot-kafka:9092' # Địa chỉ hostname của Kafka broker (service Docker iot-kafka)
KAFKA_TOPIC = 'raw-data' # Topic Kafka mà dữ liệu sensor sẽ được consume
GROUP_ID = 'iot-group' # Group ID cho consumer

consumer = Consumer({ 
    'bootstrap.servers': KAFKA_BOOTSTRAP, # Danh sách các Kafka broker
    'group.id': GROUP_ID, # Consumer group ID để quản lý offset
    'auto.offset.reset': 'latest', # ĐỔI: chỉ đọc message MỚI (từ thời điểm consumer start)
    'enable.auto.commit': True,
})

consumer.subscribe([KAFKA_TOPIC]) # Đăng ký consumer để nhận message từ topic raw-data

print("Kafka consumer started, waiting for messages...")

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue # Bỏ qua và tiếp tục vòng lặp nếu không nhận được message nào
    if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
            continue # Lỗi đã đọc hết partition (không phải lỗi nghiêm trọng) → tiếp tục
        else:
            print(msg.error())
            break
    
    payload = msg.value().decode('utf-8')
    print(f"Received from Kafka: {payload}")
    
    # GỌI handle_payload() để xử lý data và ghi vào DB
    try:
        handle_payload(payload)
        print(f"✓ Processed payload successfully")
    except Exception as e:
        print(f"✗ Failed to process payload: {e}")
        import traceback
        traceback.print_exc()

consumer.close()