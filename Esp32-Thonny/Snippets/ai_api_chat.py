import network
import time
import ujson
import urequests


from API_KEYS import Open_router_api_key as open_router_api

# Wi-Fi credentials
SSID = "Manish"
PASSWORD = "passwordMANISH24"

# OpenRouter API key
API_KEY = open_router_api

URL = "https://openrouter.ai/api/v1/chat/completions"

# Connect to Wi-Fi
def connect_wifi(ssid, pwd, timeout=15):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(ssid, pwd)
        t0 = time.ticks_ms()
        while not wlan.isconnected():
            time.sleep(0.2)
            if time.ticks_diff(time.ticks_ms(), t0) > timeout * 1000:
                raise RuntimeError("WiFi connect timeout")
    print("Connected, IP:", wlan.ifconfig())

# Ask GPT-3.5 Turbo
def ask_gpt(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    body = ujson.dumps({
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    })
    
    response = urequests.post(URL, headers=headers, data=body)
    
    if response.status_code == 200:
        try:
            return response.json()["choices"][0]["message"]["content"]
        except Exception:
            return "Error: Unexpected response format"
    else:
        print(f"Error {response.status_code}: {response.text}")
        return f"Error: {response.status_code}"

# Main loop
connect_wifi(SSID, PASSWORD)

while True:
    user_input = input("Enter prompt for GPT-3.5 Turbo: ")
    print("Asking GPT-3.5 Turbo...")
    print(ask_gpt(user_input))
