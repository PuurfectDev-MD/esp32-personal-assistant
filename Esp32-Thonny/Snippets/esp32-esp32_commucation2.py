import network
import socket
import time
import _thread
import machine
from machine import Pin

led = machine.Pin(2, machine.Pin.OUT)

# WiFi setup
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("imternet", "connecttest")

while not wlan.isconnected():
    time.sleep(0.5)

my_ip = wlan.ifconfig()[0]
print('My IP:', my_ip)

other_esp_ip = '192.168.22.207'  # Esp32 main board IP
port = 1234

# Setup UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', port))

def receive_messages():
    print("Listening for messages...")
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            message = data.decode()
            print(f"Received from {addr[0]}: {message}")
        except:
            pass

def send_message(message):
    sock.sendto(message.encode(), (other_esp_ip, port))
    print(f"Sent: {message}")

# Start receiving in background
_thread.start_new_thread(receive_messages, ())

# Now both can send and receive!
while True:
    led.value(0)
    send_message("Hello from " + my_ip)
    time.sleep(1)
    led.value(1)
    time.sleep(1)
