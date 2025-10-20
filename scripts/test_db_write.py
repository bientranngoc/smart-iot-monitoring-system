"""
Test script to diagnose why data is not being written to MySQL.
Run this inside the Docker container:
  docker exec -it iot-app python scripts/test_db_write.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_iot.settings')
django.setup()

from monitoring.models import User, Device, Reading, ReadingClient
from django.db import connection
import json
from datetime import datetime

def test_database_connection():
    """Test if we can connect to MySQL"""
    print("=" * 60)
    print("TEST 1: Database Connection")
    print("=" * 60)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            print(f"✓ Connected to database: {db_name}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✓ Tables in database: {[t[0] for t in tables]}")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_user_creation():
    """Test creating a User"""
    print("\n" + "=" * 60)
    print("TEST 2: User Creation")
    print("=" * 60)
    try:
        # Delete test user if exists
        User.objects.filter(username='test_user').delete()
        
        user, created = User.objects.get_or_create(username='test_user')
        print(f"✓ User created: {user.username} (id={user.id}, created={created})")
        
        # Verify in database
        count = User.objects.filter(username='test_user').count()
        print(f"✓ User count in DB: {count}")
        return user
    except Exception as e:
        print(f"✗ User creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_device_creation(user):
    """Test creating a Device"""
    print("\n" + "=" * 60)
    print("TEST 3: Device Creation")
    print("=" * 60)
    if not user:
        print("✗ Skipping device test (no user)")
        return None
    
    try:
        # Delete test device if exists
        Device.objects.filter(name='Test Device 99').delete()
        
        device, created = Device.objects.get_or_create(
            name='Test Device 99',
            defaults={'user': user}
        )
        print(f"✓ Device created: {device.name} (id={device.id}, created={created})")
        
        # Verify in database
        count = Device.objects.filter(name='Test Device 99').count()
        print(f"✓ Device count in DB: {count}")
        
        # List all devices
        all_devices = Device.objects.all()
        print(f"✓ Total devices in DB: {all_devices.count()}")
        for d in all_devices:
            print(f"  - Device: {d.name} (id={d.id}, user={d.user.username})")
        
        return device
    except Exception as e:
        print(f"✗ Device creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_handle_payload():
    """Test the actual handle_payload function"""
    print("\n" + "=" * 60)
    print("TEST 4: handle_payload() Function")
    print("=" * 60)
    
    from monitoring.tasks import handle_payload
    
    # Sample payload like what publish.py sends
    payload = json.dumps({
        "device_id": 42,
        "temperature": 25.5,
        "humidity": 60.0,
        "timestamp": datetime.now().isoformat()
    })
    
    print(f"Payload: {payload}")
    
    try:
        # Clear existing data for device 42
        User.objects.filter(username='default_user').delete()
        Device.objects.filter(name='Device 42').delete()
        
        print("\nCalling handle_payload()...")
        handle_payload(payload)
        
        # Check results
        print("\nChecking results...")
        user_exists = User.objects.filter(username='default_user').exists()
        print(f"✓ default_user exists: {user_exists}")
        
        device_exists = Device.objects.filter(name='Device 42').exists()
        print(f"✓ Device 42 exists: {device_exists}")
        
        if device_exists:
            device = Device.objects.get(name='Device 42')
            print(f"✓ Device details: id={device.id}, user={device.user.username}")
        
        # List all users and devices
        print(f"\nAll users: {list(User.objects.values_list('username', flat=True))}")
        print(f"All devices: {list(Device.objects.values_list('name', flat=True))}")
        
    except Exception as e:
        print(f"✗ handle_payload() failed: {e}")
        import traceback
        traceback.print_exc()

def test_transaction_and_autocommit():
    """Test Django transaction settings"""
    print("\n" + "=" * 60)
    print("TEST 5: Transaction Settings")
    print("=" * 60)
    
    from django.conf import settings
    from django.db import transaction
    
    print(f"ATOMIC_REQUESTS: {settings.DATABASES['default'].get('ATOMIC_REQUESTS', False)}")
    print(f"AUTOCOMMIT: {settings.DATABASES['default'].get('AUTOCOMMIT', True)}")
    print(f"In transaction: {transaction.get_autocommit()}")
    print(f"Connection autocommit: {connection.connection.get_autocommit_mode() if hasattr(connection.connection, 'get_autocommit_mode') else 'N/A'}")

if __name__ == "__main__":
    print("Starting database diagnostics...\n")
    
    # Run tests
    if test_database_connection():
        test_transaction_and_autocommit()
        user = test_user_creation()
        test_device_creation(user)
        test_handle_payload()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTICS COMPLETE")
    print("=" * 60)
