import paho.mqtt.client as mqtt


BROKER_IP = "192.168.0.116"   # broker IP

IMAGE_ESP_info = "image/esp"
IMAGE_BROKER_TOPIC = "image/broker"


def on_message(client, userdata, msg):
    topic = msg.topic()
    payload = msg.payload.decode()
    
    if topic == IMAGE_ESP_info:
        print("Recieved info of picture")
        
        
client = mqtt.Client(clientid= "esp32_vision")
client.on_message = on_message()
client.connect()
client.subscribe(IMAGE_ESP_info)


