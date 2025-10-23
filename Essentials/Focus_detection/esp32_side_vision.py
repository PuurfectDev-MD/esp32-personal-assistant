# optimized_stream_final_fixed.py - Complete with all fixes
import camera
import network
import picoweb
import time
import gc
from umqtt.simple import MQTTClient
import ubinascii

BROKER_IP = " 192.168.121.168"   # broker IP

IMAGE_FROM_ESP = "image/esp"
IMAGE_FROM_BROKER = "image/broker"


# WiFi Configuration
SSID = "imternet"
PASSWORD = "connecttest"

client = None


def on_message(topic, msg):
    topic = topic.decode()
    msg= msg.decode()

    if topic == IMAGE_FROM_BROKER:
        print("Image recieved on esp32")




def connect_mqtt():
    """Connect to MQTT broker"""
    global client
    try:
        client = MQTTClient("esp32_vision", BROKER_IP)
        client.set_callback(on_message)
        client.connect()
        client.subscribe(IMAGE_FROM_BROKER)
        print("✅ MQTT Connected and subscribed")
        return client
    except Exception as e:
        print(f"❌ MQTT connection failed: {e}")
        return False
    


def send_to_mqtt(topic, message):
    client.publish(topic, message)
    print("Image Sent")



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


def picture_to_text(picture):
        image_size = len(picture)
        if image_size > 200000:  # ~200KB to be safe
            print("⚠️ Image too large, reducing quality...")
            camera.quality(8)  # Lower quality
            picture = camera.capture()

        print("🔄 Converting to Base64...")
        image_base64 = ubinascii.b2a_base64(picture).decode('utf-8').strip()


        del picture
        gc.collect()

        return image_base64



def capture_image():
    picture =  camera.capture()  # Returns binary JPEG data
    print("Image Captured")
    return picture

def main():
    global client
    setup_camera()
    ip_address = connect_wifi()

    if not ip_address:
        print("Cannot run without internet")
        return

    client = connect_mqtt()

    if not client:
        print("cannot run with client")
        return
    
    print("\n✅ SYSTEM READY!")
    print("📡 Waiting for MQTT messages...")
    print("🔄 Auto-capturing images every 5 seconds...")
    

  
    last_capture = 0
    capture_interval = 10000 

    while True:
        try:
            client.check_msg()
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, last_capture) > capture_interval:
                picture = capture_image()
                image_text =  picture_to_text(picture)
                send_to_mqtt(IMAGE_FROM_ESP, image_text)
                last_capture = current_time
                print()
                del image_text
                gc.collect()
    
            time.sleep(0.1)

        except Exception as e:
            print(f"❌ Main loop error: {e}")
            print("🔄 Reconnecting...")
            time.sleep(5)
            client = connect_mqtt()
    
main()




