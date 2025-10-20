#!/usr/bin/env python
"""
Test phone camera connection with MediaMTX
"""
import subprocess
import sys

def test_phone_rtsp(phone_ip, phone_port=8080):
    """Test if phone RTSP stream is accessible"""
    rtsp_url = f"rtsp://{phone_ip}:{phone_port}/h264_pcm.sdp"
    
    print(f"🔍 Testing RTSP stream from phone camera...")
    print(f"   URL: {rtsp_url}")
    print(f"   This will take 5-10 seconds...\n")
    
    # Use ffprobe to check stream
    cmd = [
        'docker', 'exec', 'iot-mediamtx',
        'ffprobe', 
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,codec_name,r_frame_rate',
        '-of', 'default=noprint_wrappers=1',
        rtsp_url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print("✅ Phone camera stream is accessible!")
            print(f"\n📊 Stream Info:")
            print(result.stdout)
            print("\n🎉 You can now update the database with this phone IP!")
            print(f"   Run: docker exec iot-app python scripts/update_phone_camera.py")
            return True
        else:
            print("❌ Cannot access phone camera stream")
            print(f"\n🔍 Error Details:")
            print(result.stderr)
            print("\n💡 Troubleshooting:")
            print("   1. Check if IP Webcam app is running on phone")
            print("   2. Check if phone shows 'Server running' status")
            print("   3. Make sure phone and PC are on SAME WiFi network")
            print(f"   4. Try opening in browser: http://{phone_ip}:{phone_port}")
            print(f"   5. Test ping: ping {phone_ip}")
            return False
    except subprocess.TimeoutExpired:
        print("⏱️  Timeout - Connection took too long")
        print("\n💡 This usually means:")
        print("   1. Phone and PC are NOT on the same WiFi network")
        print("   2. Phone IP address changed (check app again)")
        print("   3. Firewall blocking RTSP port 8080")
        print("   4. IP Webcam app is not running")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("❌ Missing phone IP address!")
        print("\nUsage:")
        print("   python scripts/test_phone_camera.py <phone_ip>")
        print("\nExample:")
        print("   python scripts/test_phone_camera.py 192.168.1.105")
        print("\n📱 To find your phone IP:")
        print("   1. Open IP Webcam app on phone")
        print("   2. Scroll down and tap 'Start Server'")
        print("   3. Look at the URL shown (e.g., http://192.168.1.105:8080)")
        print("   4. Use the IP part (192.168.1.105)")
        sys.exit(1)
    
    phone_ip = sys.argv[1]
    phone_port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    
    print("=" * 70)
    print("📱 Phone Camera Connection Test")
    print("=" * 70)
    print()
    
    success = test_phone_rtsp(phone_ip, phone_port)
    
    print("\n" + "=" * 70)
    if success:
        print("✅ TEST PASSED - Phone camera is ready!")
    else:
        print("❌ TEST FAILED - Please fix issues above")
    print("=" * 70)
    
    sys.exit(0 if success else 1)
