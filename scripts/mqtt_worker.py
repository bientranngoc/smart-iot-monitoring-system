import paho.mqtt.client as mqtt
from monitoring.tasks import on_message, MQTT_BROKER, MQTT_PORT, MQTT_TOPIC # Tách cấu hình và logic xử lý message ra một module riêng

def run(): # Khởi tạo MQTT client và chạy vòng lặp subscribe
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60) # Kết nối tới MQTT broker ở host MQTT_BROKER và cổng MQTT_PORT với keepalive = 60 giây
    client.subscribe(MQTT_TOPIC) # Đăng ký subscribe tới topic MQTT_TOPIC
    print("MQTT Subscriber running...")
    client.loop_forever() # Bắt đầu vòng lặp mạng chính — blocking call — sẽ xử lý I/O, gọi callback (on_connect, on_message, etc.) và giữ kết nối sống

if __name__ == "__main__":
    run()
