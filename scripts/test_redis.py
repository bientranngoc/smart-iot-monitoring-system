"""
Test Redis caching functionality
Run: docker exec -it iot-app python scripts/test_redis.py
"""
import redis
import json
import time

REDIS_HOST = 'iot-redis'
REDIS_PORT = 6379

print("=" * 60)
print("Redis Cache Test")
print("=" * 60)

# Connect to Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

print(f"\n1. Testing connection...")
try:
    redis_client.ping()
    print(f"   ✓ Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    print(f"   ✗ Connection failed: {e}")
    exit(1)

print(f"\n2. Checking for cached device readings...")
keys = list(redis_client.scan_iter("latest:device*"))
print(f"   Found {len(keys)} cached devices:")
for key in sorted(keys):
    data = redis_client.get(key)
    if data:
        reading = json.loads(data)
        ttl = redis_client.ttl(key)
        device_id = key.split('device')[1]
        print(f"   - Device {device_id}: {reading['temperature']}°C, {reading['humidity']}% (TTL: {ttl}s)")

if not keys:
    print(f"   No cached data found. Run publish.py to generate data.")

print(f"\n3. Testing manual cache set/get...")
test_key = "latest:device999"
test_data = {
    "device_id": 999,
    "temperature": 25.5,
    "humidity": 60.0,
    "timestamp": "2025-10-20T04:00:00"
}

try:
    redis_client.set(test_key, json.dumps(test_data), ex=10)
    print(f"   ✓ Set test cache: {test_key}")
    
    cached = redis_client.get(test_key)
    if cached:
        parsed = json.loads(cached)
        print(f"   ✓ Retrieved: {parsed}")
        
        ttl = redis_client.ttl(test_key)
        print(f"   ✓ TTL: {ttl}s")
    
    print(f"\n   Waiting 3 seconds...")
    time.sleep(3)
    
    ttl_after = redis_client.ttl(test_key)
    print(f"   ✓ TTL after 3s: {ttl_after}s")
    
    print(f"\n   Deleting test cache...")
    redis_client.delete(test_key)
    print(f"   ✓ Deleted")
    
except Exception as e:
    print(f"   ✗ Test failed: {e}")

print(f"\n4. Get all active devices (with data in last 60s)...")
active_devices = []
for key in redis_client.scan_iter("latest:device*"):
    device_id = key.split('device')[1]
    data = redis_client.get(key)
    if data:
        reading = json.loads(data)
        active_devices.append({
            'device_id': device_id,
            'temperature': reading.get('temperature'),
            'humidity': reading.get('humidity'),
            'timestamp': reading.get('timestamp')
        })

print(f"   Active devices: {len(active_devices)}")
for device in sorted(active_devices, key=lambda x: x['device_id']):
    print(f"   - Device {device['device_id']}: {device['temperature']}°C, {device['humidity']}%")

print(f"\n5. Redis info...")
info = redis_client.info('memory')
print(f"   Used memory: {info['used_memory_human']}")
print(f"   Peak memory: {info['used_memory_peak_human']}")

stats = redis_client.info('stats')
print(f"   Total commands: {stats['total_commands_processed']}")

print("\n" + "=" * 60)
print("Redis Test Complete!")
print("=" * 60)
