# Script to sync MongoDB to OpenSearch (local version)
# Run this from host machine where you can access both MongoDB and OpenSearch

import pymongo
from opensearchpy import OpenSearch
from datetime import datetime

# MongoDB connection
mongo_client = pymongo.MongoClient("mongodb://root:root@localhost:27017/")
mongo_db = mongo_client["iot"]
readings_collection = mongo_db["readings"]

# OpenSearch connection  
os_client = OpenSearch(
    hosts=["http://localhost:9200"],
    use_ssl=False,
    verify_certs=False
)

INDEX_NAME = "sensor-readings"

# Create index
if not os_client.indices.exists(index=INDEX_NAME):
    mapping = {
        "mappings": {
            "properties": {
                "device_id": {"type": "integer"},
                "temperature": {"type": "float"},
                "humidity": {"type": "float"},
                "timestamp": {"type": "date"}
            }
        }
    }
    os_client.indices.create(index=INDEX_NAME, body=mapping)
    print(f"✓ Created index '{INDEX_NAME}'")
else:
    print(f"✓ Index '{INDEX_NAME}' already exists")

# Sync readings
readings = list(readings_collection.find({}).sort('timestamp', -1))
print(f"Found {len(readings)} readings in MongoDB")

count = 0
for reading in readings:
    doc = {
        "device_id": reading['device_id'],
        "temperature": reading['temperature'],
        "humidity": reading['humidity'],
        "timestamp": reading['timestamp'].isoformat() if isinstance(reading['timestamp'], datetime) else reading['timestamp']
    }
    
    os_client.index(
        index=INDEX_NAME,
        id=str(reading['_id']),
        body=doc
    )
    count += 1

print(f"✓ Indexed {count} documents")

print(f"\n✅ Done! Now you can run:")
print(f'  curl "http://localhost:9200/{INDEX_NAME}/_search?pretty"')
print(f'  curl "http://localhost:9200/{INDEX_NAME}/_count?pretty"')
