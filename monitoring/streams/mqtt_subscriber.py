"""
MQTT subscriber - Receives sensor data from MQTT broker
"""

import logging
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)

# Config
MQTT_BROKER = 'iot-mosquitto'
MQTT_PORT = 1883
MQTT_TOPIC = 'sensors/data'


def run_mqtt_loop():
    """
    Run MQTT subscriber loop (blocking)
    
    This function will run in a background thread.
    Connects to MQTT broker and subscribes to sensor data topic.
    """
    from .handlers import on_mqtt_message
    
    client = mqtt.Client()
    client.on_message = on_mqtt_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC)
    
    logger.info("MQTT Subscriber connected to %s:%d, topic: %s", 
                MQTT_BROKER, MQTT_PORT, MQTT_TOPIC)
    
    # Blocking call - processes network I/O, calls callbacks
    client.loop_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_mqtt_loop()
