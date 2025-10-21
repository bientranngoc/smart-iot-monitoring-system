"""
Cache service - Redis operations for sensor data caching
"""

import json
import logging
import redis
from typing import Optional, Dict, Any, List
from django.conf import settings

logger = logging.getLogger(__name__)

# Redis client singleton
_redis_client = None


def get_redis_client() -> redis.Redis:
    """Get or create Redis client"""
    global _redis_client
    if _redis_client is None:
        redis_host = getattr(settings, 'REDIS_HOST', 'iot-redis')
        redis_port = getattr(settings, 'REDIS_PORT', 6379)
        _redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=0,
            decode_responses=True
        )
    return _redis_client


def cache_latest_reading(device_id: int, data: Dict[str, Any], ttl: int = 60) -> bool:
    """
    Cache latest sensor reading to Redis
    
    Args:
        device_id: Device ID
        data: Sensor reading data (dict)
        ttl: Time to live in seconds (default: 60)
        
    Returns:
        True if cached successfully, False otherwise
    """
    try:
        client = get_redis_client()
        cache_key = f"latest:device{device_id}"
        cache_value = json.dumps(data)
        client.set(cache_key, cache_value, ex=ttl)
        logger.info("✓ Cached to Redis: %s", cache_key)
        return True
    except Exception as e:
        logger.warning("Failed to cache to Redis: %s", e)
        return False


def get_latest_reading(device_id: int) -> Optional[Dict[str, Any]]:
    """
    Get latest reading from Redis cache
    
    Args:
        device_id: Device ID
        
    Returns:
        Sensor reading data dict or None if not found
    """
    try:
        client = get_redis_client()
        cache_key = f"latest:device{device_id}"
        cached_data = client.get(cache_key)
        
        if cached_data:
            data = json.loads(cached_data)
            ttl = client.ttl(cache_key)
            data['status'] = 'online' if ttl > 0 else 'offline'
            return data
        return None
    except Exception as e:
        logger.error("Failed to get from Redis: %s", e)
        return None


def get_all_latest_readings() -> List[Dict[str, Any]]:
    """
    Get all latest readings from Redis cache
    
    Returns:
        List of sensor reading dicts
    """
    try:
        client = get_redis_client()
        results = []
        
        for key in client.scan_iter("latest:device*"):
            cached_data = client.get(key)
            if cached_data:
                data = json.loads(cached_data)
                ttl = client.ttl(key)
                data['status'] = 'online' if ttl > 0 else 'offline'
                results.append(data)
        
        results.sort(key=lambda x: x.get('device_id', 0))
        return results
    except Exception as e:
        logger.error("Failed to get all from Redis: %s", e)
        return []


def clear_device_cache(device_id: int) -> bool:
    """
    Clear cached data for a device
    
    Args:
        device_id: Device ID
        
    Returns:
        True if cleared successfully, False otherwise
    """
    try:
        client = get_redis_client()
        cache_key = f"latest:device{device_id}"
        client.delete(cache_key)
        logger.info("✓ Cleared Redis cache: %s", cache_key)
        return True
    except Exception as e:
        logger.error("Failed to clear Redis cache: %s", e)
        return False
