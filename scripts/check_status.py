#!/usr/bin/env python
"""Check current sensor readings and alerts"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_iot.settings')
django.setup()

from monitoring.models import ZoneSensor, BuildingAlert, Zone

print("="*60)
print("SENSOR READINGS")
print("="*60)
sensors = ZoneSensor.objects.filter(is_active=True).select_related('zone')
for s in sensors:
    time_str = s.latest_reading_time.strftime("%Y-%m-%d %H:%M:%S") if s.latest_reading_time else "Never"
    print(f"{s.zone.name:20s} | {s.sensor_type:12s} | {s.latest_reading:>6} | {time_str}")

print("\n" + "="*60)
print("ACTIVE ALERTS")
print("="*60)
alerts = BuildingAlert.objects.filter(acknowledged=False).select_related('zone')
print(f"Total: {alerts.count()}")
for a in alerts:
    print(f"\n[{a.severity}] {a.zone.name}")
    print(f"  Type: {a.alert_type}")
    print(f"  Title: {a.title}")
    print(f"  Message: {a.message}")
    print(f"  Sensor Value: {a.sensor_value}")
    print(f"  Created: {a.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

print("\n" + "="*60)
print("ZONES")
print("="*60)
zones = Zone.objects.all()
for z in zones:
    print(f"\n{z.name} ({z.zone_type})")
    print(f"  Status: {z.status}")
    print(f"  Target Temp: {z.target_temperature}°C")
    print(f"  Sensors: {z.sensors.count()}")
    print(f"  Cameras: {z.cameras.count()}")
