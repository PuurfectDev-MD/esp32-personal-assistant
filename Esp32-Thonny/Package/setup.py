import network # for wifi
import urequests  # for web interaction
import time
import machine

from machine import Pin, SPI, I2C  
from ili9341 import Display, color565  #for the SPI display
from xpt2046 import Touch
from xglcd_font import XglcdFont   

import utime   # for the clock
from ds3231 import DS3231



# WiFi credentials
WIFI_SSID = "Manish"
WIFI_PASS = "passwordMANISH24"

# MQTT broker
BROKER_IP = "192.168.0.116"
CLIENT_ID = "esp32_client"
JARVIS_RESPONSE = "jarvis/responses"
CONTROL_TOPIC   = "jarvis/control"
AI_RESPONSE     = "ai/responses"
AI_REQUEST      = "ai/requests"

# ======= Server Configurable Variables =======
TTS_SERVER_IP = "192.168.0.116"
TTS_SERVER_PORT = 5000



# ====== Google Calendar API Settings ======
CALENDAR_ID = "manish.dhakal2020@gmail.com" 
API_KEY = "AIzaSyCAEVwduzMjVHNJi0voS1kDUCcg-XYY7Rg"
BASE_URL = "https://www.googleapis.com/calendar/v3/calendars"



# Single SPI bus for both display and touch
spi = SPI(2, baudrate=10000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))

# Display
display = Display(spi,
                  cs=Pin(5),
                  dc=Pin(27),
                  rst=Pin(4),
                  width=320,
                  height=240,
                  rotation=270)

# Touch (same SPI bus, different CS)
touch = Touch(spi, cs=Pin(12), width=320, height=240)


#for the clock
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
rtc = DS3231(i2c)
# RTC Power control pin
rtc_power = Pin(33, Pin.OUT)  # GPIO15 as power source


font = XglcdFont('Unispace12x24.c', 12, 24)
font2 = XglcdFont('Robotron7x11.c', 7, 11)
espresso_dolce = XglcdFont('fonts/EspressoDolce18x24.c', 18, 24)
bally = XglcdFont('fonts/Bally7x9.c', 7, 9)
arcadepix = XglcdFont('fonts/ArcadePix9x11.c', 9, 11)

colors = {
    0: 0xF800,  # Red
    1: 0x07E0,  # Green
    2: 0x001F,  # Blue
    3: 0xFFE0,  # Yellow
    4: 0xF81F,  # Fuchsia
    5: 0x07FF,  # Aqua
    6: 0x8000,  # Maroon
    7: 0x0400,  # Dark green
    8: 0x0010,  # Navy
    9: 0x0410,  # Teal
    10: 0x8010,  # Purple
    11: 0x8400,  # Olive
    12: 0xFC00,  # Orange
    13: 0xF810,  # Deep pink
    14: 0x87E0,  # Chartreuse
    15: 0x07F0,  # Spring green
    16: 0x801F,  # Indigo
    17: 0x041F,  # Dodger blue
    18: 0x87FF,  # Cyan
    19: 0xF81F,  # Pink (same as fuchsia)
    20: 0xFFE0,  # Light yellow
    21: 0xF810,  # Light coral
    22: 0x87E0,  # Light green
    23: 0x841F,  # Light slate blue
    24: 0xFFFF,  # White
    25: 0xFF19, #light orange
    26: 0xFF13, #light yellow
    27: 0xFC10, #light red
}



class Sprite:
    """Memory-efficient Sprite handler for ILI9341 display with scaling support (streamed)."""

    def __init__(self, path, raw_width, raw_height, display, x=0, y=0, scale=1):
        """
        Args:
            path (str): Path to sprite .raw file (RGB565).
            raw_width, raw_height (int): Original dimensions of raw image.
            display (Display): ILI9341 display object.
            x, y (int): Initial position.
            scale (float/int): Scale factor for drawing.
        """
        self.display = display
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.scale = scale
        self.raw_width = raw_width
        self.raw_height = raw_height
        self.path = path  # keep path instead of storing entire buffer

        # Scaled width/height
        self.w = int(raw_width * scale)
        self.h = int(raw_height * scale)

    def move_to(self, x, y):
        """Move sprite to absolute position."""
        self.prev_x = self.x
        self.prev_y = self.y
        self.x = x
        self.y = y

    def move(self, dx, dy):
        """Move sprite relative to current position."""
        self.move_to(self.x + dx, self.y + dy)

    def clear(self, bg_color=0):
        """Erase sprite at previous position."""
        self.display.fill_rectangle(self.prev_x, self.prev_y, self.w, self.h, bg_color)

    def draw(self, bg_color=None):
        """Draw sprite by streaming from file instead of loading fully into RAM."""
        try:
            with open(self.path, "rb") as f:
                for row in range(self.raw_height):
                    row_data = f.read(self.raw_width * 2)  # one row (RGB565, 2 bytes per pixel)

                    if not row_data:
                        break  # end of file unexpectedly

                    if self.scale == 1:
                        # draw line directly (fast path)
                        self.display.draw_sprite(
                            row_data, self.x, self.y + row, self.raw_width, 1
                        )
                    else:
                        # slow path: scale each pixel
                        for col in range(self.raw_width):
                            offset = col * 2
                            pixel = int.from_bytes(row_data[offset:offset+2], "big")
                            self.display.fill_rectangle(
                                self.x + int(col * self.scale),
                                self.y + int(row * self.scale),
                                int(self.scale),
                                int(self.scale),
                                pixel
                            )

        except OSError as e:
            print(f"❌ Error drawing sprite {self.path}: {e}")


