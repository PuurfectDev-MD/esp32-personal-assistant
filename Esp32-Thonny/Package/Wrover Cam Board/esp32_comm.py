import network
import socket
import time
import _thread
import machine
from machine import Pin
from umqtt.simple import MQTTClient
import ubinascii
import setup
from setup  import  SSID, PASSWORD

VISION_RESULTS = "vision/results"

client = None


def init_communication():
    global client
    
    # WiFi connection
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    
    # MQTT setup
    connect_mqtt()



def connect_mqtt():
    global client
    try:
        client = MQTTClient("esp32_vision", setup.BROKER_IP)
        client.connect()
        client.set_callback(callback)
        client.subscribe(VISION_RESULTS)
        
        print("✅ MQTT Connected")
        return client
    except Exception as e:
        print(f"❌ MQTT connection failed: {e}")
        return None

def send_to_mqtt(topic, message):
    if client:
        client.publish(topic, message)
        print("Message Sent")


def callback(topic, msg):
    topic = topic.decode()
    msg = msg.decode()
    print("📩 Message received:", msg)
    
    print(f"Topic: {topic} --- Message: {msg}")
    
    

def check_mqtt_vision_results():
    while:
        try:
            if client:
                client.check_msg()
        time.sleep(0.1)
        except Exception as e:
            print(f"MQTT message handler error {e}")
            time.sleep(1)
    

