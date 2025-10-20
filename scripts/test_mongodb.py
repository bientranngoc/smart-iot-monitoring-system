"""
Test MongoDB connection and ReadingClient
Run: docker exec -it iot-app python scripts/test_mongodb.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_iot.settings')
django.setup()

from monitoring.models import Reading, ReadingClient
from datetime import datetime
from django.conf import settings

print("=" * 60)
print("MongoDB Connection Test")
print("=" * 60)

# Show settings
print(f"\nSettings:")
print(f"  MONGODB_URI: {settings.MONGODB_URI}")
print(f"  MONGODB_DB_NAME: {settings.MONGODB_DB_NAME}")

# Test connection
print(f"\n1. Testing ReadingClient connection...")
client = ReadingClient()
print(f"   URI: {client.uri}")
print(f"   DB: {client.db_name}")
print(f"   Collection: {client.collection_name}")

# Try to connect
try:
    client._connect()
    print(f"   ✓ Connected to MongoDB!")
    
    # Get collection stats
    stats = client._collection.database.command("dbstats")
    print(f"   ✓ Database: {stats.get('db')}")
    print(f"   ✓ Collections: {stats.get('collections')}")
    
except Exception as e:
    print(f"   ✗ Connection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test insert
print(f"\n2. Testing insert_reading()...")
try:
    reading = Reading(
        device_id=999,
        temperature=25.5,
        humidity=60.0,
        timestamp=datetime.utcnow()
    )
    
    inserted_id = client.insert_reading(reading)
    
    if inserted_id:
        print(f"   ✓ Insert successful! ID: {inserted_id}")
    else:
        print(f"   ✗ Insert returned None")
        
except Exception as e:
    print(f"   ✗ Insert failed: {e}")
    import traceback
    traceback.print_exc()

# Test query
print(f"\n3. Testing find_readings()...")
try:
    readings = client.find_readings(device_id=999, limit=5)
    print(f"   ✓ Found {len(readings)} readings for device_id=999")
    
    if readings:
        print(f"   Sample: {readings[0]}")
        
except Exception as e:
    print(f"   ✗ Query failed: {e}")
    import traceback
    traceback.print_exc()

# Count all readings
print(f"\n4. Total readings in MongoDB...")
try:
    total = client._collection.count_documents({})
    print(f"   ✓ Total readings: {total}")
    
    # Group by device_id
    pipeline = [
        {"$group": {"_id": "$device_id", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    result = list(client._collection.aggregate(pipeline))
    
    if result:
        print(f"   Readings by device:")
        for r in result:
            print(f"     - Device {r['_id']}: {r['count']} readings")
    
except Exception as e:
    print(f"   ✗ Count failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("MongoDB Test Complete!")
print("=" * 60)
