import MySQLdb
import pymongo
import redis
import asyncio
from confluent_kafka import Producer
import paho.mqtt.client as mqtt
from opensearchpy import OpenSearch

# MySQL
conn = MySQLdb.connect(host='iot-mysql', user='user', password='Mk@123456', database='smart_iot', port=3306)
print("MySQL OK")

# MongoDB
client = pymongo.MongoClient('mongodb://root:root@localhost:27017/')
print("MongoDB OK")

# Redis
r = redis.Redis(host='iot-redis', port=6379)
r.ping()
print("Redis OK")

# Kafka
producer = Producer({'bootstrap.servers': 'iot-kafka:9092'})
print("Kafka OK")

# OpenSearch
os_client = OpenSearch('http://iot-opensearch:9200')
print("OpenSearch OK:", os_client.ping())

# MQTT
client = mqtt.Client()
client.connect('iot-mosquitto', 1883)
print("MQTT OK")