import network
import socket
from machine import Pin
from calendar_module import connect_wifi

# Set up Access Point
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="ESP32-Server", password="12345678")  # your WiFi name and password

print("Access Point Created")
print("SSID:", ap.config('essid'))
print("IP Address:", ap.ifconfig()[0])

# LED setup
led = Pin(2, Pin.OUT)

# HTML page
html = """<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Web Server</title>
</head>
<body>
    <h1>Hello from ESP32!</h1>
    <p>Connect to the ESP32 AP and open this page.</p>
</body>
</html>
"""

connect_wifi()

# Create socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    print("Got a connection from", addr)
    request = conn.recv(1024)
    print("Request:", request)

    # Send HTTP response
    conn.send("HTTP/1.1 200 OK\n")
    conn.send("Content-Type: text/html\n")
    conn.send("Connection: close\n\n")
    conn.sendall(html)
    conn.close()
