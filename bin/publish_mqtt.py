import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt

# Kết nối MQTT và publish 10 bản tin JSON vào topic sensors/data
MQTT_BROKER = "iot-mosquitto" # Địa chỉ hostname của MQTT broker (service Docker iot-mosquitto)
MQTT_PORT = 1883 
MQTT_TOPIC = "sensors/data" # Topic MQTT mà dữ liệu sensor sẽ được publish vào

def publish_data():
    client = mqtt.Client() # instance của MQTT client
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start() # Bắt đầu vòng lặp network trong background thread để xử lý các message và duy trì kết nối

    for _ in range(10):  # Gửi 10 messages giả lập
        data = {
            "device_id": random.randint(1, 5),
            "temperature": round(random.uniform(20, 30), 2),
            "humidity": round(random.uniform(50, 70), 2),
            "timestamp": datetime.now().isoformat()
        }
        payload = json.dumps(data)
        client.publish(MQTT_TOPIC, payload) # Publish message (payload JSON) lên topic sensors/data
        print(f"Published: {payload}")
        time.sleep(2)  # Delay 2s giữa messages

    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    publish_data()