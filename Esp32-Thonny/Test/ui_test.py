from machine import Pin, SPI, I2C
import time
import utime
from ili9341 import Display
from xglcd_font import XglcdFont
from xpt2046 import Touch
from ds3231 import DS3231

spi = SPI(2, baudrate=10000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))

# RTC Power control pin
rtc_power = Pin(33, Pin.OUT)  # GPIO15 as power source
rtc_power.value(1)  # Power ON at start


i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
rtc = DS3231(i2c)

rtc.set_time((2025, 8, 13, 16, 11, 0, 1))
side_panel_open = False

WHITE   = 0xFFFF
BLACK   = 0x0000
RED     = 0xF800
GREEN   = 0x07E0

font = XglcdFont('Unispace12x24.c', 12, 24)
font2 = XglcdFont('Robotron7x11.c', 7, 11)

menu_element_offset = 40


display = Display(spi,
                  cs=Pin(5),
                  dc=Pin(27),
                  rst=Pin(4),
                  width=320,
                  height=240,
                  rotation=270)


touch = Touch(spi,
              cs=Pin(12),
              width=320,
              height=240)

display.clear()
display.fill_hrect(0, 0, 320, 240, BLACK)


def side_panel_button():
    display.fill_circle(25, 25, 20, BLACK)
    display.draw_line(15,35,35,35, WHITE)
    display.draw_line(15,36,35,36, WHITE)
    display.draw_line(15,25,35,25, WHITE)
    display.draw_line(15,26,35,26, WHITE)
    display.draw_line(15,15,35,15, WHITE)
    display.draw_line(15,16,35,16, WHITE)

def side_panel():
    display.fill_hrect(1, 1, 200, 239, WHITE) #background
    display.draw_rectangle(0, 0, 201, 240, BLACK) #border
    side_panel_button() #button on top
    
    
    #items
    display.draw_text(10, 60, ">  To do", font, RED, background=WHITE)
    display.draw_text(10, 60 + (menu_element_offset*1), ">  Chat", font, RED, background=WHITE)
    display.draw_text(10, 60 + (menu_element_offset*2), ">  Statistics", font, RED, background=WHITE)
    display.draw_text(10, 60 + (menu_element_offset*3), ">  Alarm", font, RED, background=WHITE)
    


def detect_circle_button_touch(centreX, centreY, radius, Touchx, Touchy):
    sqrdistance = (Touchx - centreX)**2 + (Touchy - centreY)**2
    return sqrdistance <= radius**2

def detect_rect_touch(x0, y0, w, h, tx, ty):
    return x0 <= tx <= x0 + w and y0 <= ty <= y0 + h


def get_current_time(retries=3):
    """Reads from RTC and updates time/date display"""
    for attempt in range(retries):
        try:
            time_tuple = rtc.get_time()
            if time_tuple:
                year, month, day, hour, minute, second = time_tuple[:6]
                print(f"RTC Time: {year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}")
                return time_tuple
        except OSError as e:
            print(f"RTC read error (attempt {attempt+1}/{retries}):", e)
            time.sleep(0.1)
    print("Failed to get RTC time after retries.")
    return None


def read_rtc_time():
    rtc_power.value(1)  # Power ON
    utime.sleep_ms(50)  # Give time to stabilize
    now = get_current_time()
    rtc_power.value(0)  # Power OFF after reading
    return now




t = read_rtc_time()
print("Time:", t)
# Draw to TFT
if t:
    display.draw_text(220, 12, f"{t[3]:02d} : {t[4]:02d}", font, WHITE, background=BLACK)
    display.draw_text(220, 32, f"{t[1]:02d}/{t[2]:02d}", font, WHITE, background=BLACK)
last_update = utime.ticks_ms()


# Draw initial button
side_panel_button()
        



while True:
    # --- TOUCH DETECTION ---
    coords = touch.get_touch()
    if coords is not None:
        x, y = coords
        print(f"x : {x}, y: {y}")
    else:
        x, y = 0, 0

    if detect_circle_button_touch(25, 220, 20, x, y):
        if not side_panel_open:
            side_panel()
            side_panel_open = True
        else:
            display.fill_hrect(0, 0, 200, 240, BLACK)
            side_panel_button()    
            side_panel_open = False

    if utime.ticks_diff(utime.ticks_ms(), last_update) >= 30000:  # 30s passed
        t = read_rtc_time()
        print("Time:", t)
      # Draw to TFT
        if t:
            display.draw_text(220, 12, f"{t[3]:02d} : {t[4]:02d}", font, WHITE, background=BLACK)
            display.draw_text(220, 32, f"{t[1]:02d}/{t[2]:02d}", font, WHITE, background=BLACK)
        last_update = utime.ticks_ms()

    time.sleep(0.5)


