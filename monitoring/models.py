from django.db import models
from django.conf import settings
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import datetime

from pymongo import MongoClient
from pymongo.errors import PyMongoError

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'  

class Device(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'devices'

@dataclass
class Reading:
    device_id: int
    temperature: float
    humidity: float
    timestamp: datetime.datetime

    def to_dict(self) -> Dict[str, Any]:
        # Let pymongo handle datetime objects directly
        return asdict(self)


class ReadingClient:
    def __init__(self, uri: Optional[str] = None, db_name: Optional[str] = None, collection_name: str = "readings"):
        self.uri = uri or getattr(settings, "MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = db_name or getattr(settings, "MONGODB_DB_NAME", "iot")
        self.collection_name = collection_name
        self._client: Optional[MongoClient] = None
        self._collection = None

    def _connect(self):
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
        self._connect()
        query: Dict[str, Any] = {"device_id": device_id}
        if since is not None:
            query["timestamp"] = {"$gte": since}
        cursor = self._collection.find(query).sort("timestamp", -1).limit(limit)
        return list(cursor)