#!/usr/bin/env python
"""
Update ZoneCamera with real phone camera URL
"""
import os
import sys
import django

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_iot.settings')
django.setup()

from monitoring.models import ZoneCamera

def list_available_zones():
    """Show all available zones with cameras"""
    print("\n📍 Available Zones with Cameras:")
    print("=" * 60)
    for i, camera in enumerate(ZoneCamera.objects.select_related('zone').all(), 1):
        print(f"{i}. {camera.zone.name}")
        print(f"   Floor: {camera.zone.floor}")
        print(f"   Camera: {camera.name}")
        print(f"   Current RTSP: {camera.rtsp_url}")
        print(f"   MediaMTX Path: {camera.mediamtx_path}")
        print()

def update_camera_for_zone(zone_name, phone_ip, phone_port=8080, username='', password='', app_type='ip_webcam'):
    """
    Update camera RTSP URL for a specific zone
    
    Args:
        zone_name: Tên zone (VD: "Server Room", "Main Lobby")
        phone_ip: IP của điện thoại (VD: "192.168.1.105")
        phone_port: Port của camera app (default: 8080)
        username: Username nếu đã set trong app (optional)
        password: Password nếu đã set trong app (optional)
        app_type: 'ip_webcam', 'droidcam', hoặc 'ivcam'
    """
    try:
        # Tìm camera của zone
        camera = ZoneCamera.objects.filter(zone__name__icontains=zone_name).first()
        
        if not camera:
            print(f"❌ Không tìm thấy camera cho zone: {zone_name}")
            list_available_zones()
            return False
        
        # Build RTSP URL based on app type
        if app_type == 'ip_webcam':
            path = 'h264_pcm.sdp'
        elif app_type == 'droidcam':
            path = 'video'
        elif app_type == 'ivcam':
            path = 'stream'
        else:
            path = 'h264_pcm.sdp'  # default
        
        if username and password:
            rtsp_url = f"rtsp://{username}:{password}@{phone_ip}:{phone_port}/{path}"
        else:
            rtsp_url = f"rtsp://{phone_ip}:{phone_port}/{path}"
        
        # Update camera
        old_url = camera.rtsp_url
        camera.rtsp_url = rtsp_url
        camera.save()
        
        print("\n" + "=" * 70)
        print("✅ Camera Updated Successfully!")
        print("=" * 70)
        print(f"\n📍 Zone: {camera.zone.name} (Floor {camera.zone.floor})")
        print(f"📹 Camera: {camera.name}")
        print(f"\n🔗 URLs:")
        print(f"   RTSP (input):  {rtsp_url}")
        print(f"   HLS (output):  {camera.hls_url}")
        print(f"   WebRTC:        {camera.webrtc_url}")
        print(f"\n📝 MediaMTX Path: {camera.mediamtx_path}")
        print(f"\n⚙️  Old RTSP: {old_url}")
        
        print("\n" + "=" * 70)
        print("📋 NEXT STEPS:")
        print("=" * 70)
        print("1. Make sure IP Webcam app is running on phone")
        print("2. Restart MediaMTX to apply changes:")
        print("   → docker-compose restart mediamtx")
        print("3. Check MediaMTX logs:")
        print("   → docker logs iot-mediamtx --tail 20")
        print("4. Test stream in browser:")
        print(f"   → http://localhost:8889/{camera.mediamtx_path}/")
        print("5. View in Smart Building Dashboard:")
        print(f"   → http://localhost:8000/api/zones/{camera.zone.id}/status/")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("📱 Update Phone Camera Configuration")
    print("=" * 70)
    
    if len(sys.argv) < 3:
        print("\n❌ Missing required arguments!")
        print("\nUsage:")
        print('   python scripts/update_phone_camera.py "<zone_name>" <phone_ip> [port] [app_type]')
        print("\nExamples:")
        print('   python scripts/update_phone_camera.py "Server Room" 192.168.1.105')
        print('   python scripts/update_phone_camera.py "Main Lobby" 192.168.1.106 8080 ip_webcam')
        print('   python scripts/update_phone_camera.py "Parking Lot" 192.168.1.107 4747 droidcam')
        
        print("\n📱 App Types:")
        print("   - ip_webcam (Android) - Default")
        print("   - droidcam (Android/iOS)")
        print("   - ivcam (iOS)")
        
        list_available_zones()
        sys.exit(1)
    
    zone_name = sys.argv[1]
    phone_ip = sys.argv[2]
    phone_port = int(sys.argv[3]) if len(sys.argv) > 3 else 8080
    app_type = sys.argv[4] if len(sys.argv) > 4 else 'ip_webcam'
    
    print(f"\n📝 Configuration:")
    print(f"   Zone: {zone_name}")
    print(f"   Phone IP: {phone_ip}")
    print(f"   Port: {phone_port}")
    print(f"   App Type: {app_type}")
    print()
    
    success = update_camera_for_zone(zone_name, phone_ip, phone_port, app_type=app_type)
    
    sys.exit(0 if success else 1)
