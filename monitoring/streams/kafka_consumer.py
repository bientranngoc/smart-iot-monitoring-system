"""
Kafka consumer - Processes sensor data from Kafka topic
"""

import logging
from confluent_kafka import Consumer, KafkaError

logger = logging.getLogger(__name__)

# Config
KAFKA_BOOTSTRAP = 'iot-kafka:9092'
KAFKA_TOPIC = 'raw-data'
GROUP_ID = 'iot-group'


def run_kafka_consumer():
    """
    Run Kafka consumer loop (blocking)
    
    This function will run in a background thread.
    Consumes messages from Kafka topic and processes them.
    """
    from .handlers import on_kafka_message
    
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP,
        'group.id': GROUP_ID,
        'auto.offset.reset': 'latest',  # Only read NEW messages
        'enable.auto.commit': True,
    })
    
    consumer.subscribe([KAFKA_TOPIC])
    logger.info("Kafka consumer subscribed to %s", KAFKA_TOPIC)

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                logger.error("Kafka error: %s", msg.error())
                continue

            try:
                payload = msg.value().decode('utf-8')
                on_kafka_message(payload)
            except Exception:
                logger.exception("Failed to handle Kafka message")
    finally:
        consumer.close()


if __name__ == "__main__":
    import os
    import sys
    import django
    
    # Setup Django for standalone script
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_iot.settings')
    django.setup()
    
    logging.basicConfig(level=logging.INFO)
    run_kafka_consumer()