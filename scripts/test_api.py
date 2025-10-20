"""
Test script for API endpoints

Run this script after starting the Django development server:
python manage.py runserver

Or inside Docker:
docker exec -it iot-app python manage.py runserver 0.0.0.0:8000
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2, default=str)}")
    except:
        print(f"Response: {response.text}")


def test_api_endpoints():
    """Test all API endpoints"""
    
    print("\n🚀 Testing IoT Monitoring API Endpoints\n")
    
    # 1. Test Users
    print("\n📋 Testing Users Endpoints...")
    response = requests.get(f"{BASE_URL}/users/")
    print_response("GET /api/users/", response)
    
    # 2. Test Devices
    print("\n📱 Testing Devices Endpoints...")
    response = requests.get(f"{BASE_URL}/devices/")
    print_response("GET /api/devices/", response)
    
    devices = response.json() if response.status_code == 200 else []
    
    if devices:
        device_id = devices[0]['id']
        
        # 3. Test Device Readings
        print(f"\n📊 Testing Device Readings for device {device_id}...")
        response = requests.get(f"{BASE_URL}/devices/{device_id}/readings/", params={"limit": 5})
        print_response(f"GET /api/devices/{device_id}/readings/?limit=5", response)
        
        # 4. Test Device Latest
        print(f"\n⚡ Testing Latest Reading for device {device_id}...")
        response = requests.get(f"{BASE_URL}/devices/{device_id}/latest/")
        print_response(f"GET /api/devices/{device_id}/latest/", response)
    else:
        print("\n⚠️ No devices found in database. Skipping device-specific tests.")
    
    # 5. Test Readings List
    print("\n📈 Testing Readings List...")
    response = requests.get(f"{BASE_URL}/readings/", params={"limit": 10})
    print_response("GET /api/readings/?limit=10", response)
    
    # 6. Test Latest All
    print("\n🌐 Testing Latest All Devices...")
    response = requests.get(f"{BASE_URL}/readings/latest_all/")
    print_response("GET /api/readings/latest_all/", response)
    
    # 7. Test Statistics
    print("\n📊 Testing Statistics...")
    response = requests.get(f"{BASE_URL}/readings/stats/")
    print_response("GET /api/readings/stats/", response)
    
    # 8. Test Legacy Endpoint
    if devices:
        device_id = devices[0]['id']
        print(f"\n🔙 Testing Legacy Endpoint for device {device_id}...")
        response = requests.get(f"{BASE_URL}/latest/{device_id}/")
        print_response(f"GET /api/latest/{device_id}/", response)
    
    print("\n\n✅ API endpoint testing completed!")


def test_create_device():
    """Test creating a new device"""
    print("\n➕ Testing Device Creation...")
    
    # First, get a user ID
    response = requests.get(f"{BASE_URL}/users/")
    if response.status_code == 200 and response.json():
        user_id = response.json()[0]['id']
        
        # Create a new device
        new_device = {
            "name": f"Test Sensor {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "user": user_id
        }
        
        response = requests.post(
            f"{BASE_URL}/devices/",
            json=new_device,
            headers={"Content-Type": "application/json"}
        )
        print_response("POST /api/devices/", response)
    else:
        print("⚠️ No users found. Cannot create device.")


if __name__ == "__main__":
    try:
        test_api_endpoints()
        test_create_device()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to the API server.")
        print("Make sure Django development server is running:")
        print("  python manage.py runserver")
        print("  OR")
        print("  docker exec -it iot-app python manage.py runserver 0.0.0.0:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
