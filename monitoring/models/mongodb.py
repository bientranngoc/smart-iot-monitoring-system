"""
MongoDB models - Reading dataclass and ReadingClient
"""

from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import datetime

from django.conf import settings
from pymongo import MongoClient
from pymongo.errors import PyMongoError


@dataclass
class Reading:
    """Sensor reading data structure"""
    device_id: int
    temperature: float
    humidity: float
    timestamp: datetime.datetime

    def to_dict(self) -> Dict[str, Any]:
        # Let pymongo handle datetime objects directly
        return asdict(self)


class ReadingClient:
    """MongoDB client for sensor readings"""
    
    def __init__(self, uri: Optional[str] = None, db_name: Optional[str] = None, collection_name: str = "readings"):
        self.uri = uri or getattr(settings, "MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = db_name or getattr(settings, "MONGODB_DB_NAME", "iot")
        self.collection_name = collection_name
        self._client: Optional[MongoClient] = None
        self._collection = None

    def _connect(self):
        """Establish MongoDB connection and create indexes"""
        if self._client is None:
            self._client = MongoClient(self.uri)
            self._collection = self._client[self.db_name][self.collection_name]
            # Create unique compound index to prevent duplicates
            try:
                self._collection.create_index(
                    [("device_id", 1), ("timestamp", 1)],
                    unique=True,
                    background=True
                )
            except Exception:
                pass  # Index already exists

    def insert_reading(self, reading: Reading) -> Optional[str]:
        """Insert a sensor reading into MongoDB"""
        try:
            self._connect()
            doc = reading.to_dict()
            res = self._collection.insert_one(doc)
            return str(res.inserted_id)
        except PyMongoError as e:
            import logging
            # DuplicateKeyError is expected for duplicate readings, just log debug
            if 'duplicate key error' in str(e).lower():
                logging.debug(f"Duplicate reading ignored: device_id={reading.device_id}, timestamp={reading.timestamp}")
                return None
            logging.error(f"PyMongoError in insert_reading: {e}")
            return None
        except Exception as e:
            import logging
            logging.error(f"Unexpected error in insert_reading: {e}")
            return None

    def find_readings(self, device_id: int, limit: int = 100, since: Optional[datetime.datetime] = None) -> List[Dict[str, Any]]:
        """Find sensor readings for a device"""
        self._connect()
        query: Dict[str, Any] = {"device_id": device_id}
        if since is not None:
            query["timestamp"] = {"$gte": since}
        cursor = self._collection.find(query).sort("timestamp", -1).limit(limit)
        return list(cursor)
