"""
Celery tasks for IoT data processing

Handles MQTT and Kafka message processing using services layer.
"""

import json
import logging
from datetime import datetime

from celery import shared_task
from celery.signals import worker_ready
from django.utils import timezone

from monitoring.models import Device, User, Reading, ReadingClient, ZoneSensor
from monitoring.services import (
    cache_latest_reading,
    check_building_thresholds,
    auto_control_hvac
)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def handle_payload(payload: str):
    """
    Process sensor reading payload from Kafka
    
    Steps:
    1. Parse JSON payload
    2. Ensure User and Device exist in MySQL
    3. Store Reading in MongoDB
    4. Cache latest reading in Redis
    5. Index to OpenSearch
    6. Check Smart Building thresholds
    7. Auto-control HVAC
    """
    logger.info("=== handle_payload CALLED === payload: %s", payload)

    try:
        data = json.loads(payload)
        logger.info("Parsed JSON data: %s", data)
    except Exception:
        logger.warning("Skip invalid JSON: %s", payload)
        return

    # Normalize timestamp
    ts = data.get('timestamp')
    if ts:
        try:
            # If publisher sends ISO-string
            ts = datetime.fromisoformat(ts)
        except Exception:
            ts = timezone.now()
    else:
        ts = timezone.now()

    # ============ MYSQL (ORM 'default') ============
    # Ensure a default user exists
    user, created_user = User.objects.get_or_create(username='default_user')
    logger.info("User get_or_create: username=%s, id=%s, created=%s", 
                 user.username, user.id, created_user)

    # Create or get a Device
    device_name = f"Device {data.get('device_id')}"
    device, created_device = Device.objects.get_or_create(
        name=device_name,
        defaults={'user': user},
    )
    logger.info("Device get_or_create: name=%s, id=%s, created=%s", 
                 device.name, device.id, created_device)

    # ============ MONGODB ============
    # Persist reading via pymongo-backed ReadingClient
    try:
        # Normalize device_id to int when possible
        raw_device_id = data.get('device_id')
        try:
            device_id_val = int(raw_device_id)
        except Exception:
            device_id_val = 0

        reading = Reading(
            device_id=device_id_val,
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            timestamp=ts,
        )
        client = ReadingClient()
        inserted_id = client.insert_reading(reading)
        logger.info("MongoDB insert result: inserted_id=%s", inserted_id)
        
        if inserted_id is None:
            logger.error("Failed to insert reading into MongoDB for payload: %s", payload)
        else:
            # ============ REDIS CACHE ============
            # Cache latest reading after successful MongoDB insert
            cache_latest_reading(data['device_id'], data, ttl=60)
            
            # ============ OPENSEARCH ============
            # Index to OpenSearch after successful MongoDB insert
            try:
                from opensearchpy import OpenSearch
                os_client = OpenSearch(
                    hosts=[{'host': 'opensearch', 'port': 9200}],
                    use_ssl=False,
                    verify_certs=False
                )
                
                doc_id = f"{device_id_val}_{ts.isoformat()}"
                doc_body = {
                    'device_id': device_id_val,
                    'temperature': data.get('temperature'),
                    'humidity': data.get('humidity'),
                    'timestamp': ts.isoformat()
                }
                
                os_client.index(
                    index='sensor-readings',
                    id=doc_id,
                    body=doc_body
                )
                logger.info("✓ Indexed to OpenSearch: %s", doc_id)
            except Exception as e:
                logger.warning("Failed to index to OpenSearch: %s", e)
                
    except Exception:
        logger.exception("Failed to persist reading")
    
    # ============ SMART BUILDING LOGIC ============
    try:
        # Check if this device belongs to a Smart Building zone
        zone_sensor = ZoneSensor.objects.filter(
            device__id=device.id,
            is_active=True
        ).select_related('zone').first()
        
        if zone_sensor:
            logger.info("Device belongs to Smart Building zone: %s", zone_sensor.zone.name)
            
            # Update sensor latest reading
            if zone_sensor.sensor_type == 'TEMPERATURE':
                zone_sensor.latest_reading = data.get('temperature')
            elif zone_sensor.sensor_type == 'HUMIDITY':
                zone_sensor.latest_reading = data.get('humidity')
            
            zone_sensor.latest_reading_time = ts
            zone_sensor.save()
            logger.info("✓ Updated zone sensor reading: %s = %s", 
                        zone_sensor.sensor_type, zone_sensor.latest_reading)
            
            # Check thresholds and create alerts if needed
            alerts_count = check_building_thresholds(
                zone_sensor, 
                data.get('temperature'), 
                data.get('humidity')
            )
            if alerts_count > 0:
                logger.info("Created %d alert(s)", alerts_count)
            
            # Auto-control HVAC if zone has HVAC system
            hvac_controlled = auto_control_hvac(zone_sensor.zone)
            if hvac_controlled:
                logger.info("✓ HVAC auto-control executed")
            
    except Exception as e:
        logger.warning("Smart Building processing failed: %s", e)


@shared_task
def ping():
    """Health check task"""
    return "ok"


# Import stream runners
from monitoring.streams.runner import start_streams_once

@worker_ready.connect
def _boot_streams(**_kwargs):
    """Start MQTT and Kafka streams when Celery worker is ready"""
    start_streams_once()

@shared_task
def mqtt_subscribe_task():
    """Manually start MQTT subscriber (with lock to prevent duplicates)"""
    return start_streams_once()

@shared_task
def kafka_consumer_task():
    """Manually start Kafka consumer (with lock to prevent duplicates)"""
    return start_streams_once()
