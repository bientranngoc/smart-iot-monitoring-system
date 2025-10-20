"""
Clean duplicate readings in MongoDB and add unique index.
Run: docker exec -it iot-app python scripts/clean_duplicates.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_iot.settings')
django.setup()

from monitoring.models import ReadingClient
from pymongo import ASCENDING

print("=" * 60)
print("MongoDB Cleanup: Remove Duplicates & Add Index")
print("=" * 60)

client = ReadingClient()
client._connect()
collection = client._collection

print(f"\n1. Current statistics:")
total_before = collection.count_documents({})
print(f"   Total readings: {total_before}")

# Count by device
pipeline = [
    {"$group": {"_id": "$device_id", "count": {"$sum": 1}}},
    {"$sort": {"_id": 1}}
]
by_device = list(collection.aggregate(pipeline))
print(f"   Readings by device:")
for item in by_device:
    print(f"     - Device {item['_id']}: {item['count']} readings")

print(f"\n2. Finding duplicates (same device_id + timestamp)...")
# Find duplicates
duplicate_pipeline = [
    {
        "$group": {
            "_id": {"device_id": "$device_id", "timestamp": "$timestamp"},
            "ids": {"$push": "$_id"},
            "count": {"$sum": 1}
        }
    },
    {"$match": {"count": {"$gt": 1}}}
]

duplicates = list(collection.aggregate(duplicate_pipeline))
print(f"   Found {len(duplicates)} groups of duplicates")

if duplicates:
    print(f"\n3. Removing duplicates (keeping first occurrence)...")
    removed_count = 0
    for dup in duplicates:
        # Keep first ID, remove others
        ids_to_remove = dup['ids'][1:]
        result = collection.delete_many({"_id": {"$in": ids_to_remove}})
        removed_count += result.deleted_count
        device_id = dup['_id']['device_id']
        timestamp = dup['_id']['timestamp']
        print(f"   ✓ Removed {result.deleted_count} duplicates for device {device_id} at {timestamp}")
    
    print(f"\n   Total duplicates removed: {removed_count}")
else:
    print(f"   ✓ No duplicates found!")

print(f"\n4. Creating unique compound index (device_id, timestamp)...")
try:
    result = collection.create_index(
        [("device_id", ASCENDING), ("timestamp", ASCENDING)],
        unique=True,
        background=True,
        name="idx_device_timestamp_unique"
    )
    print(f"   ✓ Index created: {result}")
except Exception as e:
    if 'already exists' in str(e).lower():
        print(f"   ✓ Index already exists")
    else:
        print(f"   ✗ Failed to create index: {e}")

print(f"\n5. Listing all indexes:")
indexes = collection.list_indexes()
for idx in indexes:
    print(f"   - {idx['name']}: {idx.get('key', {})}")
    if idx.get('unique'):
        print(f"     (UNIQUE)")

print(f"\n6. Final statistics:")
total_after = collection.count_documents({})
print(f"   Total readings: {total_after}")
print(f"   Removed: {total_before - total_after}")

by_device_after = list(collection.aggregate(pipeline))
print(f"   Readings by device:")
for item in by_device_after:
    print(f"     - Device {item['_id']}: {item['count']} readings")

print("\n" + "=" * 60)
print("Cleanup Complete!")
print("=" * 60)
print("\nNext duplicates will be automatically rejected by unique index.")
