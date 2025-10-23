# optimized_stream_final_fixed.py - Complete with all fixes
import camera
import network
import picoweb
import time
import gc

# WiFi Configuration
SSID = "imternet"
PASSWORD = "connecttest"

def setup_camera():
    """Optimized camera setup"""
    print("🚀 Setting up camera...")
    camera.deinit()
    
    camera.init(0, 
                d0=4, d1=5, d2=18, d3=19, d4=36, d5=39, d6=34, d7=35,
                format=camera.JPEG,
                framesize=camera.FRAME_QVGA,
                xclk_freq=camera.XCLK_20MHz,
                href=23, vsync=25, reset=-1, pwdn=-1,
                sioc=27, siod=26, xclk=21, pclk=22,
                fb_location=camera.PSRAM)
    
    camera.quality(15)
    camera.flip(1)
    camera.mirror(1)
    print("✅ Camera ready")

def connect_wifi():
    """Connect to WiFi"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"📡 Connecting to {SSID}...")
        wlan.connect(SSID, PASSWORD)
        for i in range(10):
            if wlan.isconnected():
                break
            time.sleep(1)
    
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print(f"✅ Connected! IP: {ip}")
        return ip
    return None

def index_page(req, resp):
    """Web interface"""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Camera Stream</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 15px;
            max-width: 500px;
            margin: 0 auto;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        h1 {
            margin-bottom: 10px;
            font-size: 2.2em;
        }
        .subtitle {
            opacity: 0.9;
            margin-bottom: 20px;
        }
        img {
            width: 100%;
            max-width: 400px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        .fps-display {
            position: fixed;
            top: 15px;
            right: 15px;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            font-size: 14px;
        }
        .status {
            background: rgba(255, 255, 255, 0.2);
            padding: 10px;
            border-radius: 8px;
            margin: 15px 0;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎥 ESP32 Camera</h1>
        <div class="subtitle">Live Stream - Phone Hotspot</div>
        
        <div class="status">
            <strong>Status:</strong> Streaming | 
            <strong>Resolution:</strong> 320x240 | 
            <strong>Target:</strong> 3-4 FPS
        </div>
        
        <img src="/stream" id="videoFeed" alt="Live Camera Feed">
    </div>
    
    <div class="fps-display" id="fpsCounter">FPS: --</div>
    
    <script>
        let frameCount = 0;
        let lastTime = Date.now();
        const video = document.getElementById('videoFeed');
        const fpsElement = document.getElementById('fpsCounter');
        
        // FPS counter
        video.onload = function() {
            frameCount++;
            const currentTime = Date.now();
            if (currentTime - lastTime >= 1000) {
                const fps = frameCount;
                fpsElement.textContent = 'FPS: ' + fps;
                frameCount = 0;
                lastTime = currentTime;
            }
        };
        
        // Auto-reconnect on error
        video.onerror = function() {
            console.log('Stream disconnected, reconnecting...');
            setTimeout(() => {
                video.src = '/stream?t=' + new Date().getTime();
            }, 2000);
        };
        
        // Prevent context menu on right-click
        video.oncontextmenu = function(e) {
            e.preventDefault();
            return false;
        };
    </script>
</body>
</html>"""
    yield from picoweb.start_response(resp)
    yield from resp.awrite(html)

def video_stream(req, resp):
    """Optimized video stream with all fixes"""
    yield from picoweb.start_response(resp, "multipart/x-mixed-replace; boundary=frame")
    
    print("🎬 Starting optimized stream...")
    print("💡 Expected: 3-4 FPS stable streaming")
    
    frame_count = 0
    start_time = time.time()
    last_performance_check = start_time
    
    while True:
        try:
            # 1. Capture frame
            frame_start = time.time()
            frame = camera.capture()
            frame_count += 1
            
            # 2. Send frame immediately
            yield from resp.awrite(
                b'--frame\r\n' +
                b'Content-Type: image/jpeg\r\n\r\n' + 
                frame + 
                b'\r\n'
            )
            
            # 3. Performance monitoring - LESS FREQUENT (every 30 frames)
            current_time = time.time()
            if frame_count % 30 == 0:  # Reduced from 20 to 30
                elapsed_total = current_time - start_time
                actual_fps = frame_count / elapsed_total
                print(f"📊 Frame {frame_count}: {actual_fps:.1f} FPS")
                last_performance_check = current_time
            
            # 4. Memory management - LESS AGGRESSIVE (every 40 frames)
            if frame_count % 40 == 0:  # Reduced frequency
                gc.collect()
            
            # 5. Stable timing - USE PROVEN SETTING
            processing_time = time.time() - frame_start
            target_delay = 0.18  # ~5.5 FPS target (accounts for network overhead)
            sleep_time = max(0.05, target_delay - processing_time)
            time.sleep(sleep_time)
            
        except Exception as e:
            # Handle disconnections gracefully
            error_msg = str(e)
            if "EOF" in error_msg or "closed" in error_msg:
                # Normal client disconnection
                break
            else:
                print(f"⚠️ Stream error: {e}")
                time.sleep(0.5)
                break
    
    print("🔌 Client disconnected")
    gc.collect()

# Application routes
ROUTES = [
    ("/", index_page),
    ("/stream", video_stream),
]

def main():
    print("=" * 50)
    print("🚀 ESP32 OPTIMIZED CAMERA STREAM")
    print("   With all performance fixes applied")
    print("=" * 50)
    
    # Initialize hardware
    setup_camera()
    ip_address = connect_wifi()
    
    if ip_address:
        print("\n✅ SYSTEM READY!")
        print(f"🌐 Open in browser: http://{ip_address}")
        print("📊 Expected performance: 3-4 FPS")
        print("🎯 Stable streaming without slowdown")
        print("=" * 50)
        
        # Start web server
        app = picoweb.WebApp(__name__, ROUTES)
        app.run(debug=0, host="0.0.0.0", port=80)  # debug=0 for max performance
        
    else:
        print("❌ Failed to connect to WiFi")
        print("   Please check your WiFi credentials")

# Run the application
if __name__ == "__main__":
    main()

