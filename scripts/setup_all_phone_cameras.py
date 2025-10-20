#!/usr/bin/env python
"""
Setup all phone cameras at once for Smart Building
"""
import os
import sys
import django

sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_iot.settings')
django.setup()

from monitoring.models import ZoneCamera

# ⚠️ CONFIGURE YOUR PHONE CAMERAS HERE
CAMERAS = [
    {
        'zone': 'Server Room',
        'ip': '192.168.1.105',  # ⚠️ Change this!
        'port': 8080,
        'type': 'ip_webcam',  # ip_webcam, droidcam, ivcam
        'username': '',  # Optional
        'password': '',  # Optional
    },
    {
        'zone': 'Main Lobby',
        'ip': '192.168.1.106',  # ⚠️ Change this!
        'port': 8080,
        'type': 'ip_webcam',
        'username': '',
        'password': '',
    },
    {
        'zone': 'Parking Lot',
        'ip': '192.168.1.107',  # ⚠️ Change this!
        'port': 4747,  # DroidCam uses port 4747
        'type': 'droidcam',
        'username': '',
        'password': '',
    },
    {
        'zone': 'Office Floor 5',
        'ip': '192.168.1.108',  # ⚠️ Change this!
        'port': 8080,
        'type': 'ip_webcam',
        'username': '',
        'password': '',
    }
]

def get_rtsp_url(config):
    """Generate RTSP URL based on app type"""
    ip = config['ip']
    port = config['port']
    app_type = config['type']
    username = config.get('username', '')
    password = config.get('password', '')
    
    # Determine path based on app
    if app_type == 'ip_webcam':
        path = 'h264_pcm.sdp'
    elif app_type == 'droidcam':
        path = 'video'
    elif app_type == 'ivcam':
        path = 'stream'
    else:
        path = 'h264_pcm.sdp'
    
    # Build URL with optional auth
    if username and password:
        return f"rtsp://{username}:{password}@{ip}:{port}/{path}"
    else:
        return f"rtsp://{ip}:{port}/{path}"

def setup_all_cameras():
    """Update all cameras with phone IPs"""
    print("=" * 70)
    print("🚀 Smart Building - Phone Camera Setup")
    print("=" * 70)
    print()
    
    updated_count = 0
    failed_count = 0
    
    for i, config in enumerate(CAMERAS, 1):
        print(f"\n[{i}/{len(CAMERAS)}] Setting up: {config['zone']}")
        print("-" * 70)
        
        try:
            camera = ZoneCamera.objects.filter(zone__name__icontains=config['zone']).first()
            
            if not camera:
                print(f"   ❌ Camera not found for zone: {config['zone']}")
                failed_count += 1
                continue
            
            rtsp_url = get_rtsp_url(config)
            old_url = camera.rtsp_url
            camera.rtsp_url = rtsp_url
            camera.save()
            
            print(f"   ✅ Updated successfully!")
            print(f"   📍 Zone: {camera.zone.name} (Floor {camera.zone.floor})")
            print(f"   📱 Phone: {config['ip']}:{config['port']} ({config['type']})")
            print(f"   🔗 RTSP: {rtsp_url}")
            print(f"   📺 HLS: {camera.hls_url}")
            print(f"   🎥 MediaMTX Path: {camera.mediamtx_path}")
            
            updated_count += 1
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed_count += 1
    
    print("\n" + "=" * 70)
    print("📊 SETUP SUMMARY")
    print("=" * 70)
    print(f"✅ Successfully updated: {updated_count}/{len(CAMERAS)} cameras")
    if failed_count > 0:
        print(f"❌ Failed: {failed_count}/{len(CAMERAS)} cameras")
    
    if updated_count > 0:
        print("\n" + "=" * 70)
        print("📋 NEXT STEPS:")
        print("=" * 70)
        print("1. Make sure ALL phone camera apps are running")
        print("   → Check each phone shows 'Server running' or 'Connected'")
        print()
        print("2. Restart MediaMTX to apply changes:")
        print("   → docker-compose restart mediamtx")
        print()
        print("3. Wait 10 seconds, then check MediaMTX logs:")
        print("   → docker logs iot-mediamtx --tail 30")
        print("   → Look for: '[RTSP] [path xxx] source ready'")
        print()
        print("4. Test all streams in browser:")
        print("   → http://localhost:8889/")
        print("   → Click on each camera path (server_room, lobby_main, etc.)")
        print()
        print("5. Check Smart Building API:")
        print("   → http://localhost:8000/api/buildings/1/overview/")
        print("   → Should show all camera HLS URLs")
        print()
        print("6. Run test to trigger alerts:")
        print("   → docker exec iot-app python scripts/test_smart_building.py")
        print("=" * 70)
    
    return updated_count > 0

if __name__ == '__main__':
    print("\n⚠️  Before running this script:")
    print("   1. Edit CAMERAS list in this file with your phone IPs")
    print("   2. Make sure all phones are connected to SAME WiFi")
    print("   3. Make sure camera apps are installed and running")
    print()
    input("Press ENTER to continue or CTRL+C to abort...")
    print()
    
    success = setup_all_cameras()
    
    sys.exit(0 if success else 1)
