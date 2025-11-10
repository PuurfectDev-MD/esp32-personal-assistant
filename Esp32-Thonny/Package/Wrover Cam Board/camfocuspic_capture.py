import camera
import network
import picoweb
import time
import gc
from umqtt.simple import MQTTClient
import ubinascii
import setup
from esp32_comm 


IMAGE_FROM_ESP = "image/esp"

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
    setup_camera()
    
    if not esp32_comm.client:
        esp32_comm.connect_mqtt()
    
    print("✅ SYSTEM READY!")
    
    last_capture = 0
    capture_interval = 10000
    
    while True:
        try:
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, last_capture) > capture_interval:
                picture = capture_image()
                image_text = picture_to_text(picture)
                esp32_comm.send_to_mqtt(IMAGE_FROM_ESP, image_text)
                last_capture = current_time
                
                del image_text
                gc.collect()
            
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)