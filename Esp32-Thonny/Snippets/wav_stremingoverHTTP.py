import network
import urequests
import machine
import time

# Wi-Fi setup
ssid = 'Manish'
password = 'passwordMANISH24'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    time.sleep(0.5)
print('Connected to WiFi:', wlan.ifconfig())

# Simple URL encoder for MicroPython
def url_encode(text):
    encoded = ""
    safe_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.~"
    for c in text:
        if c in safe_chars:
            encoded += c
        elif c == " ":
            encoded += "%20"
        else:
            encoded += "%%%02X" % ord(c)
    return encoded

# DAC setup
dac = machine.DAC(machine.Pin(25))

def play_wav_stream(resp):
    header = resp.raw.read(44)  # skip WAV header
    while True:
        chunk = resp.raw.read(1024)
        if not chunk:
            break
        for b in chunk:
            dac.write(b)
            time.sleep_us(20)
    resp.close()

# ======= Server Configurable Variables =======
TTS_SERVER_IP = "192.168.0.117"
TTS_SERVER_PORT = 5000

# Main loop
while True:
    text = input("Enter text to speak (or 'exit' to quit): ").strip()
    if text.lower() == "exit":
        break

    encoded_text = url_encode(text)
    tts_url = f"http://{TTS_SERVER_IP}:{TTS_SERVER_PORT}/speak?text={encoded_text}"

    print(f"Requesting TTS for: {text}")
    response = urequests.get(tts_url, stream =True)
    play_wav_stream(response)
