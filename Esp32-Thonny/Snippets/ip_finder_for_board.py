#main board ip : 192.168.22.207
#camera board ip : 192.168.22.29

import network
import time

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("imternet","connecttest" )

print("Connecting to WiFi...")

# Wait for connection
timeout = 0
while not wlan.isconnected():
    time.sleep(1)
    timeout += 1
    if timeout > 10:
        print("Failed to connect to WiFi")
        break

if wlan.isconnected():
    ip_info = wlan.ifconfig()
    print("=" * 30)
    print("Connected to WiFi!")
    print("My IP Address:", ip_info[0])
    print("Subnet Mask:", ip_info[1])
    print("Gateway:", ip_info[2])
    print("DNS:", ip_info[3])
    print("=" * 30)
else:
    print("Not connected to WiFi")