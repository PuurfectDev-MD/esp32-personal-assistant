import network
import urequests
import time

# ====== Wi-Fi Credentials ======
WIFI_SSID = "Manish"
WIFI_PASS = "passwordMANISH24"

# ====== Google Calendar API Settings ======
CALENDAR_ID = "manish.dhakal2020@gmail.com" 
API_KEY = "AIzaSyCAEVwduzMjVHNJi0voS1kDUCcg-XYY7Rg"  

# Get events from 2025-01-01 to 2025-12-31
TIME_MIN = "2025-01-01T00:00:00Z"
TIME_MAX = "2025-12-31T23:59:59Z"

URL = (
    f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events"
    f"?key={API_KEY}"
    f"&timeMin={TIME_MIN}&timeMax={TIME_MAX}"
    f"&singleEvents=true&orderBy=startTime"
)

# ====== Connect to Wi-Fi ======
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    print("Connecting to Wi-Fi...", end="")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\n✅ Connected:", wlan.ifconfig())

# ====== Fetch & Print Events ======
def get_calendar_events():
    try:
        print("\nFetching events...")
        response = urequests.get(URL)
        data = response.json()
        response.close()

        events = data.get("items", [])
        print(f"Total events found: {len(events)}\n")

        for event in events:
            summary = event.get("summary", "No title")
            start = event.get("start", {}).get("dateTime", event.get("start", {}).get("date", ""))
            end = event.get("end", {}).get("dateTime", event.get("end", {}).get("date", ""))
            print(f"📅 {start} → {end}  |  {summary}")

    except Exception as e:
        print("❌ Error fetching events:", e)

# ====== Main Program ======
connect_wifi()



while True:
    user_in = input("Enter Y/N :").strip().upper()
    
    if user_in == "Y":
        get_calendar_events() 
    
