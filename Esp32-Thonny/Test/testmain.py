import network # for wifi
import urequests  # for web interaction
import time
import machine

from machine import Pin, SPI, I2C  
from ili9341 import Display   #for the SPI display
from xglcd_font import XglcdFont   

import utime   # for the clock
from ds3231 import DS3231



# Setup SPI for display
spi = SPI(2, baudrate=40000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))

# colors in RGB565 format
RED     = 0xF800
GREEN   = 0x07E0
BLUE    = 0x001F
YELLOW  = 0xFFE0
CYAN    = 0x07FF
MAGENTA = 0xF81F
WHITE   = 0xFFFF
BLACK   = 0x0000


# Initialize display 
display = Display(spi,
                  cs=Pin(5),
                  dc=Pin(27),
                  rst=Pin(4),
                  rotation=0)

display.clear()

font = XglcdFont('Unispace12x24.c', 12, 24)
font2 = XglcdFont('Robotron7x11.c', 7, 11)

display.draw_text(50, 140, 'Hello Manish!', font, RED)

#set up for clock
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)

rtc = DS3231(i2c)
# rtc.set_time((2025, 8, 11, 14, 13, 0, 1))   --- this can reset the time



# ======= Server Configurable Variables =======
TTS_SERVER_IP = "192.168.0.116"
TTS_SERVER_PORT = 5000

# ====== Wi-Fi Credentials ======
WIFI_SSID = "Manish"
WIFI_PASS = "passwordMANISH24"

# ====== Google Calendar API Settings ======
CALENDAR_ID = "manish.dhakal2020@gmail.com" 
API_KEY = "AIzaSyCAEVwduzMjVHNJi0voS1kDUCcg-XYY7Rg"
BASE_URL = "https://www.googleapis.com/calendar/v3/calendars"


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
    
    time_tuple = rtc.get_time()
    print("RTC get_time() raw output:", time_tuple)
    
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



# Plays the text by the encoded text based on the events    
def speakEvents(text):
     encoded_text = url_encode(text)  #converts the raw text into URL form 
     tts_url = f"http://{TTS_SERVER_IP}:{TTS_SERVER_PORT}/speak?text={encoded_text}"  #sets up an url
     response = urequests.get(tts_url, stream =True) # sends the url to the web
     play_wav_stream(response) # plays the wav file

    
    
    
def get_calendar_events_today():
    try:
        today_list = []
        time_min, time_max = get_today_time_range()
        
        urlForToday = (
        f"{BASE_URL}/{CALENDAR_ID}/events"
        f"?key={API_KEY}"
        f"&timeMin={time_min}&timeMax={time_max}"
        f"&singleEvents=true&orderBy=startTime"
    )
        
        try:
            todayresponse = urequests.get(urlForToday, timeout =5)
        except Exception as e:
            print("HTTPS failed", e)
            return []
        
        data = todayresponse.json()
        todayresponse.close()
        
        events =data.get("items", [])
        todayEvents = len(events)
        
        print(f"{todayEvents} events found for today")
        
        if todayEvents == 0:
            return []
        
        for event in events:
            summary = event.get("summary", "No title")
            start_dt = event.get("start", {}).get("dateTime", None)
            end_dt = event.get("end", {}).get("dateTime", None)

            start_Time = ""
            end_Time = ""
            
            if start_dt:
                # Example: '2025-04-01T15:00:00+04:00'
                
                start_Time = start_dt[11:16] 
                print("Start time:", start_Time)
                
            if end_dt:
                end_Time = end_dt[11:16]
                print("End time:", end_Time)
                
            today_list.append((summary, start_Time, end_Time))
            print(f"📅 {start_dt} → {end_dt}  |  {summary}")
        return today_list
        
        
    except Exception as d:
        print("Error getting events", d)
        return []
        
        
        
        
        
   
def get_calendar_events():
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
    display.clear()
    display.draw_text(15, 10, "Events List", font, RED)
    for i, (summary, start_Time, end_Time) in enumerate(events):
        display.draw_text(15, 50 + (i * 40), f"{i}: {summary}", font2, GREEN)

        # Speak events titles and times
        speakEvents(summary)
        
        if start_Time or end_Time:
            display.draw_text(45, 70 + (i * 40), f" {start_Time} >> {end_Time}", font2, WHITE)
            speakEvents(f"Starts at {start_Time} and ends at {end_Time}")
  
            
            


# ====== Main Program ======
connect_wifi()



while True:
    
    user_in = input("Enter command :").strip().upper()
    if user_in == "CALENDAR":
        events = get_calendar_events()
        process_events(events)
    if user_in == "CALENDAR FOR TODAY":
        today_events = get_calendar_events_today()
        
        if len(today_events) == 0:
            display.clear()
            display.draw_text(45, 150, "NO EVENT!", font, GREEN)
            speakEvents(f"No events for today sir")
            print("No events")
        else:
            process_events(today_events)
            
