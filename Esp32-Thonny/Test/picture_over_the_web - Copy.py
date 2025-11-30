import camera
import network
import time
import gc
import machine
import usocket as socket
import _thread
from umqtt.simple import MQTTClient
from html_content import html
CLIENT_NAME = "eps32_wrover"


WIFI_SSID = "imternet"
WIFI_PASS = "connecttest"

current_image = None
image_lock = _thread.allocate_lock()


led = machine.Pin(2, machine.Pin.OUT)
led.value(0)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    time.sleep(0.5)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    print("Connecting to Wi-Fi...", end="")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\n✅ Connected:", wlan.ifconfig())






def setup_camera():
    """Optimized camera setup"""
    print("🚀 Setting up camera...")
    try:
        camera.deinit()
        time.sleep(1)
    except:
        pass
    
    # Camera configuration for ESP32-WROVER
    camera.init(0, 
                d0=4, d1=5, d2=18, d3=19, d4=36, d5=39, d6=34, d7=35,
                format=camera.JPEG,
                framesize=camera.FRAME_QVGA,  # 320x240 - smaller for MQTT
                xclk_freq=camera.XCLK_20MHz,
                href=23, vsync=25, reset=-1, pwdn=-1,
                sioc=27, siod=26, xclk=21, pclk=22,
                fb_location=camera.PSRAM)
    
    # Lower quality for smaller images (better for MQTT)
    camera.quality(12)
    camera.flip(1)
    camera.mirror(1)
    print("✅ Camera ready")



def capture_image():
    picture =  camera.capture()  # Returns binary JPEG data
    print("Image Captured")
    return picture


def update_camera_image():
    """Update the global image in background"""
    global current_image
    while True:
        try:
            new_image = capture_image()
            with image_lock:
                current_image = new_image
            gc.collect()
            time.sleep(10)  # Update every 10 seconds
        except Exception as e:
            print(f"Camera error: {e}")
            time.sleep(5)



def begin_https():
    
    #beings the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 80))
    s.listen(1)
    print("Server started!")
    while True:
        try:
            connection, address = s.accept()
            print(f"\nConnection from: {address}")
            
            request = connection.recv(1024)
            
            if not request:
                connection.close()
                continue
                
            request_str = request.decode('utf-8')
            print(f"Request: {request_str.splitlines()[0]}")  #prints the first line of the request
            
            # Handle favicon requests 
            if "favicon.ico" in request_str:
                print("🖼️ Favicon request - sending 204")
                connection.send('HTTP/1.1 204 No Content\r\n\r\n')
                #sends 204 no header,\r\n for space for the content, \r\n as blank line in body 
                connection.close()
                continue
            
            # Handle button presses
            if "GET /?LED1=ON" in request_str:
                print("💡 LED1 ON")
                led.value(1)
            elif "GET /?LED1=OFF" in request_str:
                print("💡 LED1 OFF")
                led.value(0)
            
            if "GET /image" in request_str:
                with image_lock:  # ← ACQUIRE lock
                    if current_image:
                        connection.send('HTTP/1.1 200 OK\r\n')
                        connection.send('Content-Type: image/jpeg\r\n')
                        connection.send('Content-Length: {}\r\n'.format(len(current_image)))
                        connection.send('Cache-Control: no-cache\r\n')
                        connection.send('Connection: close\r\n\r\n')
                        connection.sendall(current_image)
                        print(f"✅ Image sent ({len(current_image)} bytes)")
                
                    else:
                        connection.send('HTTP/1.1 404 Not Found\r\n\r\nNo image available')
                # ← RELEASE lock automatically here
                
                connection.close()  # ← Close connection after image
                continue  # ← Skip HTML sending
                    
            # send to the brower -request succeded, html file is being sent and sends the html file 
            connection.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + html)
            connection.close()
            
        except Exception as e:
            print(f"Error: {e}")
            try:
                connection.close()
            except:
                pass
            
            
            
            





connect_wifi()
setup_camera()
_thread.start_new_thread(update_camera_image,())
_thread.start_new_thread(begin_https,())




while True:
    time.sleep(1)

