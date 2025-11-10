BROKER_IP = " 192.168.121.168"


# WiFi Configuration
SSID = "imternet"
PASSWORD = "connecttest"


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