import assistant_module

client = None

def init_mqtt():
    global client
    client = assistant_module.connect_mqtt()
    print("Connected to MQTT")
    return client
