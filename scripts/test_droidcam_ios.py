#!/usr/bin/env python
"""
Test DroidCam OBS connection from iOS device
"""
import socket
import sys

def test_droidcam_rtsp(phone_ip, phone_port=4747):
    """Test if DroidCam RTSP stream is accessible"""
    rtsp_url = f"rtsp://{phone_ip}:{phone_port}/video"
    
    print(f"🔍 Testing DroidCam OBS (iOS) connection...")
    print(f"   URL: {rtsp_url}")
    print(f"   Testing TCP connection to port {phone_port}...\n")
    
    # Test 1: TCP connection to RTSP port
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((phone_ip, phone_port))
        sock.close()
        
        if result == 0:
            print("✅ DroidCam OBS port is accessible!")
            print(f"   iPhone {phone_ip}:{phone_port} is reachable")
            
            # Test 2: Try RTSP handshake
            print(f"\n🔍 Testing RTSP handshake...")
            try:
                rtsp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                rtsp_sock.settimeout(5)
                rtsp_sock.connect((phone_ip, phone_port))
                
                # Send RTSP OPTIONS request
                request = f"OPTIONS {rtsp_url} RTSP/1.0\r\nCSeq: 1\r\n\r\n"
                rtsp_sock.send(request.encode())
                
                # Receive response
                response = rtsp_sock.recv(1024).decode('utf-8', errors='ignore')
                rtsp_sock.close()
                
                if 'RTSP/1.0' in response and '200' in response:
                    print("✅ RTSP handshake successful!")
                    print(f"\n📊 RTSP Server Info:")
                    for line in response.split('\r\n')[:5]:
                        if line:
                            print(f"   {line}")
                    
                    print("\n🎉 iPhone camera is ready!")
                    print(f"\n📝 Next step: Update database with this iPhone IP")
                    print(f'   Run: docker exec iot-app python scripts/update_phone_camera.py "Main Lobby" {phone_ip} 4747 droidcam')
                    return True
                else:
                    print("⚠️  Port is open but RTSP response unexpected")
                    print(f"   Response: {response[:200]}")
                    print("\n💡 This might still work with MediaMTX")
                    print(f'   Try: docker exec iot-app python scripts/update_phone_camera.py "Main Lobby" {phone_ip} 4747 droidcam')
                    return True
                    
            except Exception as e:
                print(f"⚠️  RTSP handshake error: {e}")
                print("\n� Port is open, so DroidCam OBS is likely running")
                print(f'   Try updating: docker exec iot-app python scripts/update_phone_camera.py "Main Lobby" {phone_ip} 4747 droidcam')
                return True
        else:
            print("❌ Cannot connect to DroidCam OBS")
            print(f"   Connection to {phone_ip}:{phone_port} failed")
            print("\n💡 Troubleshooting:")
            print("   1. Check if DroidCam OBS app is running on iPhone")
            print("   2. Look at app - should show 'WiFi IP' and camera preview")
            print("   3. Make sure iPhone and PC are on SAME WiFi network")
            print(f"   4. Test ping: ping {phone_ip}")
            print(f"   5. Check iPhone firewall/restrictions")
            print("   6. Try restarting the DroidCam OBS app")
            return False
            
    except socket.timeout:
        print("⏱️  Timeout - Connection took too long")
        print("\n💡 This usually means:")
        print("   1. iPhone and PC are NOT on the same WiFi network")
        print("   2. iPhone IP address changed (check app again)")
        print("   3. Firewall blocking port 4747")
        print("   4. DroidCam OBS app is not running")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("\n💡 Debug info:")
        print(f"   IP: {phone_ip}")
        print(f"   Port: {phone_port}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("❌ Missing iPhone IP address!")
        print("\nUsage:")
        print("   python scripts/test_droidcam_ios.py <iphone_ip>")
        print("\nExample:")
        print("   python scripts/test_droidcam_ios.py 192.168.1.110")
        print("\n📱 To find your iPhone IP:")
        print("   1. Open DroidCam OBS app on iPhone")
        print("   2. Look at the screen - it shows 'WiFi IP'")
        print("   3. Example: WiFi IP: 192.168.1.110")
        print("   4. Use that IP (192.168.1.110)")
        sys.exit(1)
    
    phone_ip = sys.argv[1]
    phone_port = 4747  # DroidCam uses port 4747
    
    print("=" * 70)
    print("📱 DroidCam OBS (iOS) Connection Test")
    print("=" * 70)
    print()
    
    success = test_droidcam_rtsp(phone_ip, phone_port)
    
    print("\n" + "=" * 70)
    if success:
        print("✅ TEST PASSED - iPhone camera is ready!")
        print("\n📋 Next Steps:")
        print(f'1. Update database: docker exec iot-app python scripts/update_phone_camera.py "Main Lobby" {phone_ip} 4747 droidcam')
        print("2. Restart MediaMTX: docker-compose restart mediamtx")
        print("3. Test stream: http://localhost:8889/lobby_main/")
    else:
        print("❌ TEST FAILED - Please fix issues above")
    print("=" * 70)
    
    sys.exit(0 if success else 1)
