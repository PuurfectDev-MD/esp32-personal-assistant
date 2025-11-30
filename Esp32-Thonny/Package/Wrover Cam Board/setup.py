import network
import time

BROKER_IP = "192.168.1.216"


SSID = "Manoj"
PASSWORD = "manish25"


focus = False

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

ip_address = connect_wifi()

