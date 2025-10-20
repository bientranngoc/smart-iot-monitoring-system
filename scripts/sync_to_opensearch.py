"""
Script to sync MongoDB readings to OpenSearch/Elasticsearch

This creates an index and syncs all readings from MongoDB to OpenSearch
for advanced search capabilities.
"""

import os
import sys
import django

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_iot.settings')
django.setup()

from opensearchpy import OpenSearch
from monitoring.models import ReadingClient
from datetime import datetime

# OpenSearch connection
client = OpenSearch(
    hosts=[{'host': 'opensearch', 'port': 9200}],
    use_ssl=False,
    verify_certs=False,
    http_compress=True,
    timeout=30
)

INDEX_NAME = 'sensor-readings'

def create_index():
    """Create OpenSearch index with mapping"""
    if client.indices.exists(index=INDEX_NAME):
        print(f"✓ Index '{INDEX_NAME}' already exists")
        return
    
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
    
    client.indices.create(index=INDEX_NAME, body=mapping)
    print(f"✓ Created index '{INDEX_NAME}'")


def sync_readings():
    """Sync all readings from MongoDB to OpenSearch"""
    reading_client = ReadingClient()
    reading_client._connect()
    
    # Get all readings from MongoDB
    readings = list(reading_client._collection.find({}).sort('timestamp', -1))
    
    print(f"Found {len(readings)} readings in MongoDB")
    
    # Bulk insert to OpenSearch
    actions = []
    for reading in readings:
        doc = {
            "device_id": reading['device_id'],
            "temperature": reading['temperature'],
            "humidity": reading['humidity'],
            "timestamp": reading['timestamp'].isoformat() if isinstance(reading['timestamp'], datetime) else reading['timestamp']
        }
        
        # Use MongoDB _id as OpenSearch document ID
        actions.append({
            "index": {
                "_index": INDEX_NAME,
                "_id": str(reading['_id'])
            }
        })
        actions.append(doc)
    
    if actions:
        from opensearchpy.helpers import bulk
        success, failed = bulk(client, actions, raise_on_error=False)
        print(f"✓ Indexed {success} documents")
        if failed:
            print(f"⚠️ Failed: {failed}")
    else:
        print("No readings to sync")


def search_readings(device_id=None, limit=10):
    """Test search functionality"""
    query = {"match_all": {}}
    
    if device_id:
        query = {"term": {"device_id": device_id}}
    
    result = client.search(
        index=INDEX_NAME,
        body={
            "query": query,
            "size": limit,
            "sort": [{"timestamp": {"order": "desc"}}]
        }
    )
    
    print(f"\n{'='*60}")
    print(f"Search Results (limit={limit})")
    print(f"{'='*60}")
    print(f"Total hits: {result['hits']['total']['value']}")
    
    for hit in result['hits']['hits']:
        doc = hit['_source']
        print(f"Device {doc['device_id']}: {doc['temperature']}°C, {doc['humidity']}% @ {doc['timestamp']}")


if __name__ == "__main__":
    print("🚀 Syncing MongoDB → OpenSearch\n")
    
    try:
        # 1. Create index
        create_index()
        
        # 2. Sync data
        sync_readings()
        
        # 3. Test search
        print(f"\n{'='*60}")
        print("Testing search...")
        print(f"{'='*60}")
        search_readings(limit=5)
        
        print("\n✅ Sync completed successfully!")
        print(f"\nYou can now query OpenSearch:")
        print(f"  curl 'http://localhost:9200/{INDEX_NAME}/_search?pretty'")
        print(f"  curl 'http://localhost:9200/{INDEX_NAME}/_count?pretty'")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
