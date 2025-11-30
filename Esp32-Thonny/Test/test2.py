import paho.mqtt.client as mqtt
import sys
import os
import time
import base64
import cv2
import numpy as np
import json
from pathlib import Path
from ultralytics import YOLO
import gc

BROKER_IP = "192.168.137.214"   # broker IP

IMAGE_FROM_ESP = "image/esp"
VISION_RESULTS = "vision/results"



def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode('utf-8') 

    if topic == IMAGE_FROM_ESP:
        print("Image recieved on broker")
        timestamp = int(time.time())
        complete_path = f"vision_img\\detection_{timestamp}\\image0.jpg"
        image = decode_base64_image(payload)

        if image == None:
            print("Failed decoding image")
            return
        
        results = model.predict(
            image, save = True,
              conf = 0.4,
               project="vision_img",
               name = f"detection_{timestamp}"
              )
        detection_results = process_detection_results(results)
        print(detection_results)

         # Convert and send image
        image_to_esp = image_to_mqtt_text(complete_path)
        if image_to_esp:
            send_to_mqtt(VISION_RESULTS, image_to_esp)
            print("✅ Processed image sent to ESP32")
        else:
            print("❌ Failed to convert image to MQTT text")




client = mqtt.Client(client_id="vision_pc") 
client.on_message = on_message

try:
    client.connect(BROKER_IP, 1883, 60)
    client.subscribe(IMAGE_FROM_ESP)
    print("✅ Connected to MQTT broker")
    print("🖥️ PC Vision System Ready")
    print("📡 Waiting for images from ESP32...")
except Exception as e:
    print(f"❌ MQTT connection failed: {e}")





try:
    # Method 1: Direct absolute path (simplest)
    model_path = r"D:\study_detect\runs\detect\train\weights\best.pt"
    model = YOLO(model_path)
    
except Exception as e:
    print(f"❌ Model loading failed: {e}")
    model = None






def decode_base64_image(image_base64):
    """
    Convert base64 string back to OpenCV image
    """
    try:
        # Decode base64 string to bytes
        image_bytes = base64.b64decode(image_base64)
        
        # Convert bytes to numpy array
        np_arr = np.frombuffer(image_bytes, np.uint8)
        
        # Decode JPEG to OpenCV image
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if image is not None:
            print(f"✅ Image decoded: {image.shape}")
            return image
        else:
            print("❌ Failed to decode image")
            return None
    
    except Exception as e:
        print(f"❌ Error decoding image: {e}")
        return None
            

def process_detection_results(results):
    pen_detected = None

    for result in results:
        # Check if there are any detections in this result
        if result.boxes is not None and len(result.boxes) > 0:
            # Access the boxes directly
            boxes = result.boxes
            # Get confidence scores
            confidences = boxes.conf
            
            for conf in confidences:
                confidence = float(conf)
                if confidence > 0.4:
                    pen_detected = True
                    return pen_detected
    
    return pen_detected



def send_to_mqtt(topic, message):
    client.publish(topic, message)



def main():
    while True:
            client.loop(timeout=1.0)
            time.sleep(0.1)




def image_to_mqtt_text(image_path):
    """
    Convert JPEG image to base64 text for MQTT transmission
    
    Args:
        image_path: Path to the JPEG image file
    
    Returns:
        JSON string ready for MQTT
    """
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            return json.dumps({"error": "Image file not found", "path": image_path})
        
        # Read the image file as binary
        with open(image_path, 'rb') as image_file:
            image_binary = image_file.read()
        
        # Convert to base64
        image_base64 = base64.b64encode(image_binary).decode('utf-8')

       # Manual cleanup
        del image_binary  # Delete the large variable
        gc.collect()      # Force garbage collection
        

        print(f"✅ Image converted to text")
        return image_base64
        
    except Exception as e:
        print("Error in image conversion")
        


main()