#!/usr/bin/env python
"""
Test Smart Building - Publish messages to trigger alerts
"""
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import time

def publish_test_messages():
    client = mqtt.Client()
    client.connect('iot-mosquitto', 1883, 60)
    
    # Test 1: Server Room - HIGH temperature (should trigger CRITICAL alert)
    print("\n🔥 Test 1: Server Room HIGH Temperature")
    msg1 = {
        'device_id': 2,  # Server Room sensor
        'temperature': 28.5,  # MAX is 22°C -> ALERT!
        'humidity': 65.0,
        'timestamp': datetime.now().isoformat()
    }
    client.publish('sensors/data', json.dumps(msg1))
    print(f"   Published: {msg1}")
    print(f"   Expected: CRITICAL ALERT (28.5°C > 22°C max)")
    print(f"   Expected: HVAC Cooling ON")
    
    time.sleep(3)
    
    # Test 2: Main Lobby - Normal temperature
    print("\n✅ Test 2: Main Lobby NORMAL Temperature")
    msg2 = {
        'device_id': 1,  # Main Lobby sensor
        'temperature': 23.5,  # Within range 22-26°C
        'humidity': 55.0,
        'timestamp': datetime.now().isoformat()
    }
    client.publish('sensors/data', json.dumps(msg2))
    print(f"   Published: {msg2}")
    print(f"   Expected: NO ALERT (within 22-26°C range)")
    print(f"   Expected: HVAC Standby")
    
    time.sleep(3)
    
    # Test 3: Office Floor 5 - HIGH temperature
    print("\n🌡️  Test 3: Office Floor 5 HIGH Temperature")
    msg3 = {
        'device_id': 4,  # Office sensor
        'temperature': 27.8,  # MAX is 26°C -> WARNING
        'humidity': 62.0,
        'timestamp': datetime.now().isoformat()
    }
    client.publish('sensors/data', json.dumps(msg3))
    print(f"   Published: {msg3}")
    print(f"   Expected: WARNING ALERT (27.8°C > 26°C max)")
    print(f"   Expected: HVAC Cooling ON (SCHEDULE mode)")
    
    client.disconnect()
    
    print("\n" + "="*60)
    print("✅ Test messages published!")
    print("="*60)
    print("\n📊 Check results:")
    print("1. Celery logs: docker logs iot-celery --tail 50")
    print("2. Alerts API: http://localhost:8000/api/building-alerts/active/")
    print("3. Zone status: http://localhost:8000/api/zones/2/status/")
    print("4. HVAC status: http://localhost:8000/api/hvac-controls/")

if __name__ == '__main__':
    publish_test_messages()
