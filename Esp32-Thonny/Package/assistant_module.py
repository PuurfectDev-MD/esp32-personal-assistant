import time
from umqtt.simple import MQTTClient
import machine
from machine import Pin
import network
import utime
from setup import display, rtc, font, font2, rtc_power, spi, touch, WIFI_SSID, WIFI_PASS, Sprite
from setup import BROKER_IP, CLIENT_ID, JARVIS_RESPONSE, CONTROL_TOPIC, AI_RESPONSE , AI_REQUEST
import ui_module

import calendar_module as cal
import ai_module


# LED pin
led = machine.Pin(2, machine.Pin.OUT)

# Assistant led
assistant_led = machine.Pin(14, machine.Pin.OUT)
assistant_led(0)

WHITE   = 0xFFFF
BLACK   = 0x0000
RED     = 0xF800
GREEN   = 0x07E0

working=  False
ai_mode = False
main_button = Pin(13, Pin.IN, Pin.PULL_UP)  # active LOW



def sub_cb(topic, msg):
    topic = topic.decode()
    msg = msg.decode()
    print("📩 Message received:", msg)

    if topic == CONTROL_TOPIC:
        if msg.lower() == "led on":
            led.value(1)
        elif msg.lower() == "led off":
            led.value(0)
        elif msg.lower() == "connect ai":
            global ai_mode
            ai_mode = True
            connect_response = ai_module.ask_gpt("Introduce yourself with a greeting in short.")
            ui_module.display_ai_response(f"AI: {connect_response}")
            print("ESP32 got AI's response")
            client.publish(AI_RESPONSE, connect_response)

    elif topic == AI_REQUEST:
        ui_module.display_ai_response(f"You: {msg}")
        ai_response = ai_module.ask_gpt(msg)
        ui_module.display_ai_response(f"AI: {ai_response}")
        client.publish(AI_RESPONSE, ai_response)
        
        

        
# Connect/reconnect MQTT
def connect_mqtt():  # secures a conenction with the broker
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
            #cal.speakEvents("Say Jarvis or Hey Jarvis to wake")  
            return client
        
        except Exception as e:
            print("⚠️ MQTT connection failed, retrying...", e)
            time.sleep(3)
            

def talk_to_assistant():
    global client
    try:
        client.check_msg()    #checks for msg 
        time.sleep(0.1)
    except Exception as e:
        print("⚠️ MQTT lost, reconnecting...", e)
        client = connect_mqtt()

    

def active_listening():
    assistant_led(1)
    mic_sprite = Sprite("images/mic84-106.raw", 84, 106, display, 120, 80)
    mic_sprite.draw()
    print("Sprite drawn - Mic on")
    time.sleep(0.1)
    print("Listening..")
    client.publish(b"jarvis/control", b"wake")
    while main_button.value() == 1:
        talk_to_assistant()
        
    print("Assistant OFf")
    mutemic = Sprite("images/micmute84-106.raw", 84, 106, display, 120, 80)
    mutemic.draw()
    assistant_led(0)
    client.publish(b"jarvis/control", b"sleep")
    time.sleep(1)
    
    

def assistant_begin():
    display.clear()
    display.fill_hrect(0, 0, 320, 240, BLACK)
  
    client = connect_mqtt()
    print("Connected to mqtt")
    print("Assistant on")
    active_listening()
    while not ai_mode:  # this seems not right
        if main_button.value() == 0:
            print("Assistant on")
            active_listening()
        
    while ai_mode:
         aimode_ui()
         








