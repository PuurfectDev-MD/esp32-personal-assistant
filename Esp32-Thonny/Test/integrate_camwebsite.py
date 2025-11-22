import machine
import usocket as socket
import time
import network
from html_content import html

WIFI_SSID = "imternet"
WIFI_PASS = "connecttest"

led = machine.Pin(2, machine.Pin.OUT)
led.value(0)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    time.sleep(0.5)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    print("Connecting to Wi-Fi...", end="")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\n✅ Connected:", wlan.ifconfig())

connect_wifi()

# HTML WITHOUT favicon link
# html = '''<!DOCTYPE html>
# <html>
# <head>
#     <title>ESP32 Control Panel</title>
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <style>
#         body { font-family: Arial; background: #f0f0f0; margin: 0; padding: 20px; }
#         .container { background: white; padding: 20px; border-radius: 10px; max-width: 400px; margin: 0 auto; }
#         .btn { padding: 10px 15px; margin: 5px; border: none; border-radius: 5px; color: white; cursor: pointer; }
#         .on { background: #4CAF50; }
#         .off { background: #f44336; }
#     </style>
# </head>
# <body>
#     <div class="container">
#         <h2>ESP32 Control Panel</h2>
#         <form>
#             <p>LED 1: 
#                 <button name="LED1" value="ON" class="btn on">ON</button>
#                 <button name="LED1" value="OFF" class="btn off">OFF</button>
#             </p>
#             <p>LED 2: 
#                 <button name="LED2" value="ON" class="btn on">ON</button>
#                 <button name="LED2" value="OFF" class="btn off">OFF</button>
#             </p>
#         </form>
#     </div>
# </body>
# </html>'''



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(1)
print("Server started!")


def begin_https():
    while True:
        try:
            connection, address = s.accept()
            print(f"\nConnection from: {address}")
            
            request = connection.recv(1024)
            
            if not request:
                connection.close()
                continue
                
            request_str = request.decode('utf-8')
            print(f"Request: {request_str.splitlines()[0]}")  #prints the first line of the request
            
            # Handle favicon requests 
            if "favicon.ico" in request_str:
                print("🖼️ Favicon request - sending 204")
                connection.send('HTTP/1.1 204 No Content\r\n\r\n')
                #sends 204 no header,\r\n for space for the content, \r\n as blank line in body 
                connection.close()
                continue
            
            # Handle button presses
            if "GET /?LED1=ON" in request_str:
                print("💡 LED1 ON")
                led.value(1)
            elif "GET /?LED1=OFF" in request_str:
                print("💡 LED1 OFF")
                led.value(0)
            

            # send to the brower -request succeded, html file is being sent and sends the html file 
            connection.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + html)
            connection.close()
            
        except Exception as e:
            print(f"Error: {e}")
            try:
                connection.close()
            except:
                pass
