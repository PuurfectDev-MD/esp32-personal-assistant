import network
import socket
import time
import _thread
import machine
from machine import Pin
from umqtt.simple import MQTTClient
import ubinascii

# Global variables
received_msg = None
client = None
sock = None

def init_communication():
    global sock, client
    
    # WiFi connection
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("imternet", "connecttest")
    
    while not wlan.isconnected():
        time.sleep(0.5)
    
    my_ip = wlan.ifconfig()[0]
    print('My IP:', my_ip)
    
    # UDP setup
    other_esp_ip = '192.168.22.207'
    port = 1234
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))
    
    # Start UDP listener
    _thread.start_new_thread(receive_messages, ())
    
    # MQTT setup
    connect_mqtt()

def receive_messages():
    global received_msg
    print("Listening for messages...")
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            received_msg = data.decode()
            print(f"Received from {addr[0]}: {received_msg}")
        except:
            pass

def get_received_message():
    global received_msg
    msg = received_msg
    received_msg = None  # Clear after reading
    return msg

def send_message(message):
    if sock:
        sock.sendto(message.encode(), ('192.168.22.207', 1234))
        print(f"Sent: {message}")

def connect_mqtt():
    global client
    try:
        client = MQTTClient("esp32_vision", "192.168.121.168")
        client.connect()
        print("✅ MQTT Connected")
        return client
    except Exception as e:
        print(f"❌ MQTT connection failed: {e}")
        return None

def send_to_mqtt(topic, message):
    if client:
        client.publish(topic, message)
        print("Image Sent")