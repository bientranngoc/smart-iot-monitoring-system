"""
Test MQTT Publishing for Smart Building System
Publishes sensor data to trigger alerts and test dashboard updates
"""
import json
import time
from datetime import datetime
import paho.mqtt.client as mqtt

# MQTT Configuration
MQTT_BROKER = "localhost"  # Use localhost since we're running outside Docker
MQTT_PORT = 1883
MQTT_TOPIC = "sensors/data"  # Must match the topic in monitoring/tasks.py

def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
    else:
        print(f"❌ Failed to connect, return code {rc}")

def publish_sensor_data(client, device_id, temperature=None, humidity=None):
    """
    Publish sensor data to MQTT topic
    Format matches what monitoring/tasks.py expects: {device_id, temperature, humidity, timestamp}
    """
    data = {
        "device_id": device_id,
        "timestamp": datetime.now().isoformat()
    }
    
    if temperature is not None:
        data["temperature"] = temperature
    if humidity is not None:
        data["humidity"] = humidity
    
    payload = json.dumps(data)
    result = client.publish(MQTT_TOPIC, payload)
    
    status = "✅" if result.rc == 0 else "❌"
    values = []
    if temperature is not None:
        values.append(f"temp={temperature}°C")
    if humidity is not None:
        values.append(f"humidity={humidity}%")
    print(f"{status} Device {device_id}: {', '.join(values)}")
    
    return result.rc == 0

def test_normal_conditions(client):
    """Test 1: Publish normal sensor readings"""
    print("\n" + "="*60)
    print("TEST 1: Normal Conditions (No Alerts Expected)")
    print("="*60)
    print("Publishing normal readings for all zones...")
    
    # Device 1 - Main Lobby (Normal: 22-24°C, 45-60% humidity)
    publish_sensor_data(client, device_id=1, temperature=23.0, humidity=55.0)
    time.sleep(0.5)
    
    # Device 2 - Server Room (Normal: 18-22°C, 40-50% humidity) 
    publish_sensor_data(client, device_id=2, temperature=20.0, humidity=45.0)
    time.sleep(0.5)
    
    # Device 3 - Parking Lot
    publish_sensor_data(client, device_id=3, temperature=25.0, humidity=60.0)
    time.sleep(0.5)
    
    # Device 4 - Office Floor 5
    publish_sensor_data(client, device_id=4, temperature=24.0, humidity=50.0)
    time.sleep(1)

def test_high_temperature_alert(client):
    """Test 2: Trigger high temperature alert (>28°C)"""
    print("\n" + "="*60)
    print("TEST 2: High Temperature Alert (>28°C)")
    print("="*60)
    print("Publishing HIGH temperature for Server Room...")
    
    # Device 2 - Server Room: High temperature (should trigger alert and HVAC cooling)
    publish_sensor_data(client, device_id=2, temperature=30.0, humidity=48.0)
    time.sleep(3)  # Wait for Celery/MQTT worker to process
    
    print("⚠️  Expected: Temperature alert created + HVAC starts cooling")
    time.sleep(1)

def test_extreme_temperature(client):
    """Test 3: Trigger extreme temperature alert"""
    print("\n" + "="*60)
    print("TEST 3: Extreme Temperature (>32°C)")
    print("="*60)
    print("Publishing EXTREME temperature for Office Floor 5...")
    
    # Device 4 - Office Floor 5: Extreme temperature
    publish_sensor_data(client, device_id=4, temperature=33.0, humidity=65.0)
    time.sleep(3)  # Wait for Celery/MQTT worker to process
    
    print("⚠️  Expected: Critical temperature alert created")
    time.sleep(1)

def test_multiple_zones_stress(client):
    """Test 4: Multiple zones with various conditions"""
    print("\n" + "="*60)
    print("TEST 4: Multiple Zones - Rapid Fire Test")
    print("="*60)
    print("Publishing data for all zones in quick succession...")
    
    # Rapid-fire sensor data for all zones
    test_data = [
        (1, 26.0, 60.0),  # Main Lobby - Normal
        (2, 31.0, 45.0),  # Server Room - HIGH TEMP!
        (3, 28.0, 55.0),  # Parking Lot - Warm
        (4, 27.0, 70.0),  # Office Floor 5 - High humidity
        (1, 25.0, 58.0),  # Main Lobby update
        (2, 32.0, 46.0),  # Server Room - HIGHER!
    ]
    
    for device_id, temp, humidity in test_data:
        publish_sensor_data(client, device_id=device_id, temperature=temp, humidity=humidity)
        time.sleep(0.5)
    
    print("\n⚠️  Expected: Multiple alerts from Server Room")
    time.sleep(2)

def test_recovery_conditions(client):
    """Test 5: Publish normal data to clear alerts"""
    print("\n" + "="*60)
    print("TEST 5: Recovery - Return to Normal Conditions")
    print("="*60)
    print("Publishing normal readings to clear alerts...")
    
    # Return all zones to normal temperatures
    publish_sensor_data(client, device_id=1, temperature=23.0, humidity=55.0)
    time.sleep(0.5)
    publish_sensor_data(client, device_id=2, temperature=21.0, humidity=45.0)
    time.sleep(0.5)
    publish_sensor_data(client, device_id=3, temperature=24.0, humidity=52.0)
    time.sleep(0.5)
    publish_sensor_data(client, device_id=4, temperature=24.0, humidity=50.0)
    time.sleep(2)
    
    print("✅ Expected: System returns to normal, alerts resolved")
    time.sleep(1)

def main():
    """Main test execution"""
    print("=" * 60)
    print("🧪 Smart Building MQTT Alert Testing")
    print("=" * 60)
    print(f"📡 Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"📢 Topic: {MQTT_TOPIC}")
    print("=" * 60)
    
    # Create MQTT client
    client = mqtt.Client(client_id="test_alerts_publisher")
    client.on_connect = on_connect
    
    try:
        # Connect to broker
        print("\n🔌 Connecting to MQTT broker...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        time.sleep(1)  # Wait for connection
        
        # Run tests
        test_normal_conditions(client)
        time.sleep(2)
        
        test_high_temperature_alert(client)
        time.sleep(3)
        
        test_extreme_temperature(client)
        time.sleep(3)
        
        test_multiple_zones_stress(client)
        time.sleep(3)
        
        test_recovery_conditions(client)
        time.sleep(2)
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        print("\n📊 Check your dashboard at: http://localhost:3001")
        print("   - Active alerts should appear at the top")
        print("   - Zone cards should show updated sensor values")
        print("   - HVAC status should reflect cooling/heating states")
        print("   - Data auto-refreshes every 30 seconds")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("\n🔌 Disconnected from MQTT broker")

if __name__ == "__main__":
    main()
