"""
Stream handlers - Message processing logic
"""

import logging
from monitoring.tasks import handle_payload

logger = logging.getLogger(__name__)


def on_mqtt_message(_client, _userdata, msg):
    """
    Callback when MQTT message is received
    
    Args:
        _client: MQTT client instance
        _userdata: User data
        msg: MQTT message object
    """
    try:
        payload = msg.payload.decode('utf-8')
        logger.info("MQTT -> %s", payload)
        
        # Send to Kafka
        from .producers import send_to_kafka
        send_to_kafka(payload)
    except Exception:
        logger.exception("Failed to process MQTT message")


def on_kafka_message(payload: str):
    """
    Process Kafka message
    
    Args:
        payload: JSON string payload
    """
    try:
        handle_payload(payload)
    except Exception:
        logger.exception("Failed to handle Kafka message")
