#!/usr/bin/env python
"""
Script to create Smart Building sample data
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_iot.settings')
django.setup()

from monitoring.models import (
    Building, Zone, ZoneSensor, ZoneCamera, 
    HVACControl, Device, User
)
from django.contrib.auth.models import User as AuthUser

def create_sample_building():
    """Tạo sample data cho Smart Building"""
    
    print("🏢 Creating Smart Building Sample Data...")
    print("=" * 60)
    
    # Get or create manager (use Django's auth user)
    manager, created = AuthUser.objects.get_or_create(
        username='building_manager',
        defaults={
            'first_name': 'Building',
            'last_name': 'Manager',
            'email': 'manager@abctower.com',
            'is_staff': True
        }
    )
    if created:
        manager.set_password('manager123')
        manager.save()
        print(f"✅ Created manager user: {manager.username}")
    else:
        print(f"ℹ️  Using existing manager: {manager.username}")
    
    # Create building
    building, created = Building.objects.get_or_create(
        name='ABC Office Tower',
        defaults={
            'address': '123 Nguyen Hue, Q1, TPHCM',
            'floors': 10,
            'total_area': 5000.0,
            'manager': manager
        }
    )
    if created:
        print(f"✅ Created building: {building.name}")
    else:
        print(f"ℹ️  Building already exists: {building.name}")
    
    # Create zones for Floor 1
    print("\n📍 Creating zones...")
    
    lobby, _ = Zone.objects.get_or_create(
        building=building,
        name='Main Lobby',
        floor=1,
        defaults={
            'zone_type': 'LOBBY',
            'area': 200.0,
            'target_temperature': 24.0,
            'temp_min': 22.0,
            'temp_max': 26.0,
            'target_humidity': 60.0,
            'humidity_min': 40.0,
            'humidity_max': 70.0
        }
    )
    print(f"  ✓ {lobby.name} (Floor {lobby.floor})")
    
    server_room, _ = Zone.objects.get_or_create(
        building=building,
        name='Server Room',
        floor=1,
        defaults={
            'zone_type': 'SERVER',
            'area': 50.0,
            'target_temperature': 20.0,
            'temp_min': 18.0,
            'temp_max': 22.0,
            'target_humidity': 50.0,
            'humidity_min': 40.0,
            'humidity_max': 60.0
        }
    )
    print(f"  ✓ {server_room.name} (Floor {server_room.floor})")
    
    parking, _ = Zone.objects.get_or_create(
        building=building,
        name='Parking Lot',
        floor=0,
        defaults={
            'zone_type': 'PARKING',
            'area': 500.0,
            'target_temperature': 30.0,
            'temp_min': 25.0,
            'temp_max': 35.0,
            'target_humidity': 70.0,
            'humidity_min': 50.0,
            'humidity_max': 90.0
        }
    )
    print(f"  ✓ {parking.name} (Floor {parking.floor})")
    
    # Office zones
    office_floor5, _ = Zone.objects.get_or_create(
        building=building,
        name='Office Floor 5',
        floor=5,
        defaults={
            'zone_type': 'OFFICE',
            'area': 400.0,
            'target_temperature': 24.0,
            'temp_min': 22.0,
            'temp_max': 26.0
        }
    )
    print(f"  ✓ {office_floor5.name} (Floor {office_floor5.floor})")
    
    print(f"\n✅ Total zones created: {Zone.objects.filter(building=building).count()}")
    
    # Get existing devices
    print("\n🔌 Linking sensors to zones...")
    devices = Device.objects.all()[:4]  # Get first 4 devices
    
    if devices.count() < 4:
        print("⚠️  Warning: Need at least 4 devices. Creating sample devices...")
        # Create sample user if needed
        sample_user, _ = User.objects.get_or_create(username='smart_building')
        
        # Create devices
        for i in range(1, 5):
            Device.objects.get_or_create(
                id=100 + i,
                defaults={
                    'name': f'Building Sensor {i}',
                    'user': sample_user
                }
            )
        devices = Device.objects.filter(id__gte=101, id__lte=104)
    
    # Create sensors for each zone
    sensor_count = 0
    
    # Lobby sensors
    if devices.count() >= 1:
        ZoneSensor.objects.get_or_create(
            zone=lobby,
            device=devices[0],
            defaults={
                'sensor_type': 'TEMPERATURE',
                'location_description': 'Lobby Center - Ceiling mounted'
            }
        )
        sensor_count += 1
        print(f"  ✓ {lobby.name} - Temperature Sensor")
    
    # Server Room sensors
    if devices.count() >= 2:
        ZoneSensor.objects.get_or_create(
            zone=server_room,
            device=devices[1],
            defaults={
                'sensor_type': 'TEMPERATURE',
                'location_description': 'Server Rack Area - Near AC intake'
            }
        )
        sensor_count += 1
        print(f"  ✓ {server_room.name} - Temperature Sensor")
    
    # Parking sensors
    if devices.count() >= 3:
        ZoneSensor.objects.get_or_create(
            zone=parking,
            device=devices[2],
            defaults={
                'sensor_type': 'TEMPERATURE',
                'location_description': 'Parking Entrance - Wall mounted'
            }
        )
        sensor_count += 1
        print(f"  ✓ {parking.name} - Temperature Sensor")
    
    # Office sensors
    if devices.count() >= 4:
        ZoneSensor.objects.get_or_create(
            zone=office_floor5,
            device=devices[3],
            defaults={
                'sensor_type': 'TEMPERATURE',
                'location_description': 'Office Center - Above workstations'
            }
        )
        sensor_count += 1
        print(f"  ✓ {office_floor5.name} - Temperature Sensor")
    
    print(f"\n✅ Total sensors linked: {sensor_count}")
    
    # Create cameras
    print("\n📹 Creating cameras...")
    camera_count = 0
    
    # Lobby camera
    ZoneCamera.objects.get_or_create(
        mediamtx_path='lobby_main',
        defaults={
            'zone': lobby,
            'name': 'Lobby Main Camera',
            'camera_type': 'ENTRANCE',
            'rtsp_url': 'rtsp://admin:password@192.168.1.101:554/stream1',
            'position_description': 'Above main entrance, wide angle view',
            'recording_enabled': True,
            'retention_days': 30
        }
    )
    camera_count += 1
    print(f"  ✓ {lobby.name} - Main Camera")
    
    # Server Room camera
    ZoneCamera.objects.get_or_create(
        mediamtx_path='server_room',
        defaults={
            'zone': server_room,
            'name': 'Server Room Camera',
            'camera_type': 'SECURITY',
            'rtsp_url': 'rtsp://admin:password@192.168.1.102:554/stream1',
            'position_description': 'Corner view of all server racks',
            'recording_enabled': True,
            'retention_days': 90  # Longer retention for compliance
        }
    )
    camera_count += 1
    print(f"  ✓ {server_room.name} - Security Camera")
    
    # Parking camera
    ZoneCamera.objects.get_or_create(
        mediamtx_path='parking_lot',
        defaults={
            'zone': parking,
            'name': 'Parking Lot Camera',
            'camera_type': 'PARKING',
            'rtsp_url': 'rtsp://admin:password@192.168.1.103:554/stream1',
            'position_description': 'Entrance gate, license plate view',
            'recording_enabled': True,
            'retention_days': 7
        }
    )
    camera_count += 1
    print(f"  ✓ {parking.name} - Parking Camera")
    
    # Office camera
    ZoneCamera.objects.get_or_create(
        mediamtx_path='office_floor5',
        defaults={
            'zone': office_floor5,
            'name': 'Office Floor 5 Camera',
            'camera_type': 'MONITORING',
            'rtsp_url': 'rtsp://admin:password@192.168.1.105:554/stream1',
            'position_description': 'Overview of office space',
            'recording_enabled': True,
            'retention_days': 14
        }
    )
    camera_count += 1
    print(f"  ✓ {office_floor5.name} - Monitoring Camera")
    
    print(f"\n✅ Total cameras created: {camera_count}")
    
    # Create HVAC controls
    print("\n❄️  Creating HVAC systems...")
    hvac_count = 0
    
    # Lobby HVAC
    HVACControl.objects.get_or_create(
        zone=lobby,
        defaults={
            'mode': 'AUTO',
            'set_temperature': 24.0,
            'fan_speed': 50
        }
    )
    hvac_count += 1
    print(f"  ✓ {lobby.name} - HVAC System (AUTO mode)")
    
    # Server Room HVAC (critical - always on)
    HVACControl.objects.get_or_create(
        zone=server_room,
        defaults={
            'mode': 'AUTO',
            'set_temperature': 20.0,
            'fan_speed': 70  # Higher fan speed for server room
        }
    )
    hvac_count += 1
    print(f"  ✓ {server_room.name} - HVAC System (AUTO mode, high priority)")
    
    # Office HVAC (scheduled)
    HVACControl.objects.get_or_create(
        zone=office_floor5,
        defaults={
            'mode': 'SCHEDULE',
            'set_temperature': 24.0,
            'fan_speed': 50
        }
    )
    hvac_count += 1
    print(f"  ✓ {office_floor5.name} - HVAC System (SCHEDULE mode)")
    
    print(f"\n✅ Total HVAC systems created: {hvac_count}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 Smart Building Setup Complete!")
    print("=" * 60)
    print(f"Building: {building.name}")
    print(f"Address: {building.address}")
    print(f"Total Floors: {building.floors}")
    print(f"Total Zones: {building.total_zones}")
    print(f"Sensors: {ZoneSensor.objects.filter(zone__building=building).count()}")
    print(f"Cameras: {ZoneCamera.objects.filter(zone__building=building).count()}")
    print(f"HVAC Systems: {HVACControl.objects.filter(zone__building=building).count()}")
    print("\n📊 Next Steps:")
    print("1. Start MQTT publishing: docker exec -it iot-app python scripts/publish.py")
    print("2. Check API: http://localhost:8000/api/buildings/1/overview/")
    print("3. View zones: http://localhost:8000/api/zones/")
    print("4. Monitor alerts: http://localhost:8000/api/building-alerts/active/")
    print("\n✨ Ready for Smart Building monitoring!")

if __name__ == '__main__':
    try:
        create_sample_building()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
