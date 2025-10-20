#!/usr/bin/env python
"""
Test MediaMTX stream status and list available paths
"""
import requests
import json

def check_mediamtx_status():
    """Check MediaMTX API status"""
    try:
        print("🔍 Checking MediaMTX status...\n")
        
        # Check API health (use container name from within Docker network)
        api_url = "http://iot-mediamtx:9997/v3/config/global/get"
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ MediaMTX API is running")
            print(f"   URL: http://localhost:9997\n")
        else:
            print(f"⚠️  MediaMTX API returned status {response.status_code}\n")
    except Exception as e:
        print(f"❌ Cannot connect to MediaMTX API: {e}\n")
        return False
    
    # Check paths
    try:
        paths_url = "http://iot-mediamtx:9997/v3/paths/list"
        response = requests.get(paths_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            print(f"📹 Available Streams: {len(items)} path(s)")
            print("=" * 70)
            
            for item in items:
                name = item.get('name', 'unknown')
                ready = item.get('ready', False)
                num_readers = item.get('numReaders', 0)
                source_ready = item.get('sourceReady', False)
                
                status = "🟢 READY" if ready and source_ready else "🔴 WAITING"
                
                print(f"\n  Path: {name}")
                print(f"  Status: {status}")
                print(f"  Readers: {num_readers}")
                print(f"  Source Ready: {'Yes' if source_ready else 'No'}")
                
                if name != 'all_others':
                    print(f"  HLS URL: http://localhost:8889/{name}/index.m3u8")
                    print(f"  View URL: http://localhost:8889/{name}/")
                    print(f"  RTSP URL: rtsp://localhost:8554/{name}")
            
            print("\n" + "=" * 70)
            return True
        else:
            print(f"❌ Cannot get paths: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking paths: {e}")
        return False

def test_hls_stream(path='lobby_main'):
    """Test if HLS stream is accessible"""
    print(f"\n🧪 Testing HLS stream for '{path}'...")
    
    hls_url = f"http://iot-mediamtx:8889/{path}/index.m3u8"
    
    try:
        response = requests.get(hls_url, timeout=5)
        if response.status_code == 200:
            print(f"✅ HLS stream is accessible!")
            print(f"   URL: {hls_url}")
            print(f"   Content-Type: {response.headers.get('Content-Type')}")
            
            # Show first few lines of playlist
            lines = response.text.split('\n')[:10]
            print(f"\n   Playlist preview:")
            for line in lines:
                if line.strip():
                    print(f"   {line}")
            
            return True
        else:
            print(f"⚠️  HLS stream returned HTTP {response.status_code}")
            print(f"   This usually means:")
            print(f"   1. Source camera (iPhone) is not connected")
            print(f"   2. DroidCam OBS app is not running")
            print(f"   3. iPhone is sleeping or WiFi disconnected")
            return False
    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout - MediaMTX is waiting for source")
        print(f"   Make sure DroidCam OBS app is running on iPhone")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("📺 MediaMTX Stream Status Check")
    print("=" * 70)
    print()
    
    # Check MediaMTX status
    if check_mediamtx_status():
        # Test HLS stream
        test_hls_stream('lobby_main')
    
    print("\n" + "=" * 70)
    print("💡 Tips:")
    print("   - View stream: http://localhost:8889/lobby_main/")
    print("   - MediaMTX API: http://localhost:9997/")
    print("   - Check logs: docker logs iot-mediamtx --tail 20")
    print("=" * 70)
