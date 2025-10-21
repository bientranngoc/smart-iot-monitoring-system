"""
Kafka producer for MQTT -> Kafka pipeline
"""

import logging
from confluent_kafka import Producer

logger = logging.getLogger(__name__)

# Config
KAFKA_BOOTSTRAP = 'iot-kafka:9092'
KAFKA_TOPIC = 'raw-data'

# Global Kafka producer (singleton pattern)
# Reuse connection to avoid creating new producer each time
_kproducer = None


def get_kafka_producer():
    """Get or create Kafka producer instance"""
    global _kproducer
    if _kproducer is None:
        _kproducer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP})
    return _kproducer


def _delivery_report(err, msg):
    """
    Callback when Kafka broker acknowledges message (or error)
    
    Args:
        err: Error object if delivery failed
        msg: Message object
    """
    if err is not None:
        logger.error("Kafka delivery failed: %s", err)
    else:
        logger.debug("Kafka delivered to %s [%d] @ %d",
                      msg.topic(), msg.partition(), msg.offset())


def send_to_kafka(message: str) -> bool:
    """
    Send message to Kafka topic
    
    Args:
        message: JSON string message
        
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        producer = get_kafka_producer()
        # Don't flush each message to avoid slowness; poll(0) is enough to serve callbacks
        producer.produce(
            KAFKA_TOPIC, 
            value=message.encode('utf-8'), 
            on_delivery=_delivery_report
        )
        producer.poll(0)
        return True
    except Exception as e:
        logger.error("Failed to send to Kafka: %s", e)
        return False
