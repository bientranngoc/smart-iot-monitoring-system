import json
import logging
import threading
import redis
from datetime import datetime

from celery import shared_task
from celery.signals import worker_ready
import paho.mqtt.client as mqtt
from django.utils import timezone

from confluent_kafka import Producer, Consumer, KafkaError

# -------------------- Config --------------------
KAFKA_BOOTSTRAP = 'iot-kafka:9092'
KAFKA_TOPIC     = 'raw-data'
GROUP_ID        = 'iot-group'

MQTT_BROKER     = 'iot-mosquitto'
MQTT_PORT       = 1883
MQTT_TOPIC      = 'sensors/data'

REDIS_HOST = 'iot-redis'
REDIS_PORT = 6379
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s') # Cấu hình logging mức DEBUG

# -------------------- Kafka Producer --------------------
# Tạo global Kafka producer (singleton pattern)
# Tái sử dụng connection, tránh tạo producer mới mỗi lần gửi message
kproducer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP}) 

def _delivery_report(err, msg): # Được gọi khi Kafka broker xác nhận nhận được message (hoặc lỗi)
    if err is not None:
        logging.error("Kafka delivery failed: %s", err)
    else:
        logging.debug("Kafka delivered to %s [%d] @ %d",
                      msg.topic(), msg.partition(), msg.offset())

def send_to_kafka(message: str):
    # Không flush từng message để tránh chậm; poll(0) là đủ phục vụ callback
    kproducer.produce(KAFKA_TOPIC, value=message.encode('utf-8'), on_delivery=_delivery_report)
    kproducer.poll(0)

# -------------------- MQTT -> Kafka --------------------
def on_message(_client, _userdata, msg): # Được gọi khi nhận message từ MQTT broker
    try:
        payload = msg.payload.decode('utf-8')
        logging.info("MQTT -> %s", payload)
        send_to_kafka(payload)
    except Exception:
        logging.exception("Failed to process MQTT message")

def run_mqtt_loop(): # Hàm sẽ chạy trong background thread
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC) # Subscribe topic sensors/data
    client.loop_forever()   # Vòng lặp vĩnh viễn để nhận message và gọi callback

# -------------------- Kafka -> DB --------------------
def handle_payload(payload: str):
    # Import models trong hàm để an toàn khi Celery fork
    from monitoring.models import Device, User, Reading, ReadingClient
    # User: người dùng (MySQL)
    # Device: thiết bị IoT (MySQL)
    # Reading: dataclass cho dữ liệu sensor
    # ReadingClient: client MongoDB (pymongo) để lưu readings

    logging.info("=== handle_payload CALLED === payload: %s", payload)

    try:
        data = json.loads(payload)
        logging.info("Parsed JSON data: %s", data)
    except Exception:
        logging.warning("Skip invalid JSON: %s", payload)
        return

    # Chuẩn hóa timestamp
    ts = data.get('timestamp')
    if ts:
        try:
            # nếu publisher gửi ISO-string
            ts = datetime.fromisoformat(ts)
        except Exception:
            ts = timezone.now()
    else:
        ts = timezone.now()

    # MySQL (ORM 'default')
    # Ensure a default user exists. (User model currently has only 'username')
    user, created_user = User.objects.get_or_create(username='default_user')
    logging.info("User get_or_create: username=%s, id=%s, created=%s", 
                 user.username, user.id, created_user)

    # Create or get a Device. Current Device model has 'name' and 'user'.
    device_name = f"Device {data.get('device_id')}"
    device, created_device = Device.objects.get_or_create(
        name=device_name,
        defaults={'user': user},
    )
    logging.info("Device get_or_create: name=%s, id=%s, created=%s", 
                 device.name, device.id, created_device)

    # Persist reading via pymongo-backed ReadingClient
    try:
        # normalize device_id to int when possible
        raw_device_id = data.get('device_id')
        try:
            device_id_val = int(raw_device_id)
        except Exception:
            device_id_val = 0

        reading = Reading(
            device_id=device_id_val,
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            timestamp=ts,
        )
        client = ReadingClient()
        inserted_id = client.insert_reading(reading)
        logging.info("MongoDB insert result: inserted_id=%s", inserted_id)
        if inserted_id is None:
            logging.error("Failed to insert reading into MongoDB for payload: %s", payload)
        else: # Đảm bảo data đã được persist trước khi cache
            # Cache latest reading to Redis after successful MongoDB insert
            try:
                cache_key = f"latest:device{data['device_id']}"
                cache_value = json.dumps(data)
                redis_client.set(cache_key, cache_value, ex=60)  # Expire sau 60s
                logging.info("✓ Cached to Redis: %s", cache_key)  # ĐỔI thành INFO để thấy rõ hơn
            except Exception as e:
                logging.warning("Failed to cache to Redis: %s", e)
            
            # Index to OpenSearch after successful MongoDB insert and Redis cache
            try:
                from opensearchpy import OpenSearch
                os_client = OpenSearch(
                    hosts=[{'host': 'opensearch', 'port': 9200}],
                    use_ssl=False,
                    verify_certs=False
                )
                
                doc_id = f"{device_id_val}_{ts.isoformat()}"
                doc_body = {
                    'device_id': device_id_val,
                    'temperature': data.get('temperature'),
                    'humidity': data.get('humidity'),
                    'timestamp': ts.isoformat()
                }
                
                os_client.index(
                    index='sensor-readings',
                    id=doc_id,
                    body=doc_body
                )
                logging.info("✓ Indexed to OpenSearch: %s", doc_id)
            except Exception as e:
                logging.warning("Failed to index to OpenSearch: %s", e)
    except Exception:
        logging.exception("Failed to persist reading")

def run_kafka_consumer():
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP,
        'group.id': GROUP_ID,
        'auto.offset.reset': 'latest',  # ĐỔI: chỉ đọc message MỚI
        'enable.auto.commit': True,
    })
    consumer.subscribe([KAFKA_TOPIC])

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                logging.error("Kafka error: %s", msg.error())
                continue

            try:
                handle_payload(msg.value().decode('utf-8'))
            except Exception:
                logging.exception("Failed to handle Kafka message")
    finally:
        consumer.close()

# -------------------- Khởi động 2 stream một lần --------------------
_streams_started = False # Biến global để đảm bảo streams chỉ start 1 lần
_streams_lock = threading.Lock() # mutex lock để tránh race condition khi nhiều thread gọi start_streams_once()

def start_streams_once():
    global _streams_started
    with _streams_lock:
        if _streams_started:
            logging.info("Streams already running; skip starting again.")
            return "already_started"
        threading.Thread(target=run_mqtt_loop, daemon=True).start()
        threading.Thread(target=run_kafka_consumer, daemon=True).start()
        _streams_started = True
        logging.info("MQTT & Kafka streams started.")
        return "started"

@worker_ready.connect # Khi Celery worker sẵn sàng (sau khi load tasks, connect broker), signal worker_ready được emit
def _boot_streams(**_kwargs):
    start_streams_once()

# -------------------- Tasks tiện kiểm tra/thủ công --------------------
@shared_task
def mqtt_subscribe_task():
    """Cho phép kick thủ công (có khóa tránh start trùng)."""
    return start_streams_once()

@shared_task
def kafka_consumer_task():
    """Cho phép kick thủ công (có khóa tránh start trùng)."""
    return start_streams_once()

@shared_task
def ping():
    return "ok"

# IoT Devices
#     ↓ (publish JSON)
# MQTT Broker (iot-mosquitto)
#     ↓ (subscribe sensors/data)
# [MQTT Thread] on_message()
#     ↓ send_to_kafka()
# Kafka Broker (iot-kafka) topic: raw-data
#     ↓ (consume)
# [Kafka Thread] run_kafka_consumer()
#     ↓ handle_payload()
#     ├─→ MySQL (Device, User via ORM)
#     └─→ MongoDB (Reading via pymongo)