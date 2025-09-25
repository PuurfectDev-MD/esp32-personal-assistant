import network # for wifi
import urequests  # for web interaction
import time
import machine
import ujson
from machine import Pin, SPI, I2C  
from ili9341 import Display
from xglcd_font import XglcdFont   

import utime
from ds3231 import DS3231


from setup import display, rtc, font, font2, rtc_power, spi, touch, i2c
from setup import WIFI_SSID, WIFI_PASS, TTS_SERVER_IP, TTS_SERVER_PORT
from setup import CALENDAR_ID, API_KEY, BASE_URL
import ui_module

# DAC setup
dac = machine.DAC(machine.Pin(25))

# colors in RGB565 format
RED     = 0xF800
GREEN   = 0x07E0
BLUE    = 0x001F
YELLOW  = 0xFFE0
CYAN    = 0x07FF
MAGENTA = 0xF81F
WHITE   = 0xFFFF
BLACK   = 0x0000



# Get events from 2025-01-01 to 2025-12-31
TIME_MIN = "2025-01-01T00:00:00Z"
TIME_MAX = "2025-12-31T23:59:59Z"

URL = (
    f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events"
    f"?key={API_KEY}"
    f"&timeMin={TIME_MIN}&timeMax={TIME_MAX}"
    f"&singleEvents=true&orderBy=startTime"
)

def get_today_time_range():

    time_tuple = ui_module.saved_time
    print("RTC get_time() raw output: for get_today_time_range", time_tuple)

    if not time_tuple or len(time_tuple) < 6:
        print("⚠️ saved_time empty or invalid, using fallback")
        time_tuple = (2025,8,18,0,0,0,0,0)
    
    # Safely unpack the first 7 elements or fewer
    year = time_tuple[0]
    month = time_tuple[1]
    day = time_tuple[2]
    hour = time_tuple[3]
    minute = time_tuple[4]
    second = time_tuple[5]
    weekday = time_tuple[6] if len(time_tuple) > 6 else 1  # default weekday=1
    

    # date to YYYY-MM-DD
    date_str = "%04d-%02d-%02d" % (year, month, day)

    time_min = f"{date_str}T00:00:00Z" #beginning of the day
    time_max = f"{date_str}T23:59:59Z" #end of the day

    return time_min, time_max


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
    
    
    
# Simple URL encoder for MicroPython to convert the text in URL form
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



# Plays the text by the encoded text based on the events    
def speakEvents(text):
     encoded_text = url_encode(text)  #converts the raw text into URL form 
     tts_url = f"http://{TTS_SERVER_IP}:{TTS_SERVER_PORT}/speak?text={encoded_text}"  #sets up an url
     response = urequests.get(tts_url, stream =True) # sends the url to the web
     play_wav_stream(response) # plays the wav file



def add_to_todo(events_of_the_day):
    with open("tasks.json", "r") as f:
        data = ujson.load(f)
    for summary, start_time, end_time in events_of_the_day:
        new_to_do = {
                    "task": summary,
                    "time": start_time,
                    "time_end": end_time,
                    "priority": "Mid",
                    "completed": "No"
                    }

        exists = any(
        task["task"] == summary and 
        task["time"] == start_time and 
        task["time_end"] == end_time
        for task in data["tasks"]
        )

        if exists:
            print("Already in the tasks")
            continue
        
        data["tasks"].append(new_to_do)
        print("Tasks added")
    with open("tasks.json", "w") as f:
        ujson.dump(data, f)


    
def get_calendar_events_today(max_retries=3, timeout_sec=10):
    today_list = []
    time_min, time_max = get_today_time_range()

    url_for_today = (
        f"{BASE_URL}/{CALENDAR_ID}/events"
        f"?key={API_KEY}"
        f"&timeMin={time_min}&timeMax={time_max}"
        f"&singleEvents=true&orderBy=startTime"
    )

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Fetching events, attempt {attempt}...")
            response = urequests.get(url_for_today, timeout=timeout_sec)
            data = response.json()
            response.close()

            events = data.get("items", [])
            print(f"{len(events)} events found for today")

            if not events:
                return []

            for event in events:
                summary = event.get("summary", "No title")
                start_dt = event.get("start", {}).get("dateTime", None)
                end_dt = event.get("end", {}).get("dateTime", None)

                start_time = start_dt[11:16] if start_dt else ""
                end_time = end_dt[11:16] if end_dt else ""

                print(f"📅 {start_dt} → {end_dt} | {summary}")
                today_list.append((summary, start_time, end_time))

            # Add events to tasks.json
            add_to_todo(today_list)
            return today_list

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                print("Retrying in 2 seconds...")
                time.sleep(2)
            else:
                print("All attempts failed. Returning empty list.")
                return []

        
   
def get_calendar_events(): #for a year
    try:
        event_list = []
        print("\nFetching events...")
        
        try:
          calresponse = urequests.get(URL, timeout=5)
        except Exception as d:
            print("❌ HTTP request failed:", d)
            return []
             
        data = calresponse.json()
        print("Got data")
        calresponse.close()

        events = data.get("items", [])
        print(f"Total events found: {len(events)}\n")

        for event in events:
            summary = event.get("summary", "No title")       
            start_dt = event.get("start",{}).get("dateTime", None)
            end_dt = event.get("end",{}).get("dateTime", None)
            
            start_Time = ""
            end_Time = ""
            
            if start_dt:
                # Example: '2025-04-01T15:00:00+04:00'
                
                start_Time = start_dt[11:16] 
                print("Start time:", start_Time)
                
            if end_dt:
                end_Time = end_dt[11:16]
                print("End time:", end_Time)
                
            
            print(f"📅 {start_dt} → {end_dt}  |  {summary}")
            
            event_list.append((summary, start_Time, end_Time))
        return event_list
  

    except Exception as e:
        print("❌ Error fetching events:", e)
        return []
    
    

def process_events(events):
    for i, (summary, start_Time, end_Time) in enumerate(events):
        display.draw_text(15, 70 + (i * 40), f"{i}: {summary}", font2, GREEN)

        # Speak events titles and times
        speakEvents(summary)
        
        if start_Time or end_Time:
            display.draw_text(45, 90 + (i * 40), f" {start_Time} >> {end_Time}", font2, WHITE)
            speakEvents(f"Starts at {start_Time} and ends at {end_Time}")
  
            
            



    
    
            

