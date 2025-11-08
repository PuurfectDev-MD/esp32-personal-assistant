from comm_config import BROKER_IP, CLIENT_ID, JARVIS_RESPONSE, CONTROL_TOPIC, WIFI_PASS, WIFI_SSID
from comm_config import AI_REQUEST, AI_RESPONSE
from umqtt.simple import MQTTClient
import network
import time
import machine




def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
    print("Connected to WiFi:", wlan.ifconfig())

# Callback
def sub_cb(topic, msg):
    print("Message received:", msg.decode())
    if msg.decode().lower() == "on":
        led.value(1)
    elif msg.decode().lower() == "off":
        led.value(0)

def communication_init(callbackfunc):
    connect_wifi()
    
    # Connect/reconnect MQTT
    global client
    while True:
        try:
            client = MQTTClient(CLIENT_ID, BROKER_IP)  
            client.set_callback(sub_cb)  #after a msg is recieved it calls this function
            client.connect()
            client.subscribe(JARVIS_RESPONSE)
            client.subscribe(CONTROL_TOPIC)
            client.subscribe(AI_REQUEST)
            print("✅ MQTT connected & subscribed") 
            return client
        
        except Exception as e:
            print("⚠️ MQTT connection failed, retrying...", e)
            time.sleep(3)





