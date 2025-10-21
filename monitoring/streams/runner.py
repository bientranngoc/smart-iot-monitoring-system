"""
Stream runner - Manages MQTT and Kafka stream threads
"""

import logging
import threading

logger = logging.getLogger(__name__)

# Stream state
_streams_started = False
_streams_lock = threading.Lock()


def start_streams_once():
    """
    Start MQTT and Kafka streams once (thread-safe)
    
    Uses mutex lock to prevent race condition when multiple threads call this.
    
    Returns:
        "started" if streams were started, "already_started" if already running
    """
    global _streams_started
    
    with _streams_lock:
        if _streams_started:
            logger.info("Streams already running; skip starting again.")
            return "already_started"
        
        # Start MQTT subscriber thread
        from .mqtt_subscriber import run_mqtt_loop
        threading.Thread(target=run_mqtt_loop, daemon=True).start()
        
        # Start Kafka consumer thread
        from .kafka_consumer import run_kafka_consumer
        threading.Thread(target=run_kafka_consumer, daemon=True).start()
        
        _streams_started = True
        logger.info("✓ MQTT & Kafka streams started.")
        return "started"
