from machine import Pin, SPI, I2C
import time
import ujson
import utime
from ili9341 import Display
from xglcd_font import XglcdFont
from xpt2046 import Touch
from ds3231 import DS3231
import setup
from setup import display, rtc, font, font2, rtc_power, spi, touch, colors, arcadepix, bally, Sprite
import alarm_test
import assistant_module
import schedule_track_sys

saved_time = []



rtc_power.value(1)  # Power ON at start
last_update = 0


focus_begin = False
menu_element_offset = 40
side_panel_open = False
no_side_panel_elements = 4

side_panel_elements = [
    (26, 195, 130, 5),
    (26, 133, 130, 60),
    (30, 83, 130, 40),
    (30, 20, 130, 35)
]


home_icons = [
    (26, 191, 45,5),
    (158, 191, 8,5),
    (246, 191, 8,9),
    (257, 137, 40,65),
    (26,23, 57, 100)  #For focus
    ]
NONE = 0
TO_DO = 1
CHAT = 2
STATS = 3
ALARM = 4


WHITE   = 0xFFFF
BLACK   = 0x0000
RED     = 0xF800
GREEN   = 0x07E0


offset= 15
cols = 4  # Number of columns
rows = 3  # Number of rows
rect_width = (display.width- offset) // cols  
rect_height = display.height // rows


max_width_text = rect_width
Hpriority_c = 27
mid_priority_c = 26
low_priority_c = 25

priority_colors = {
    "High": Hpriority_c,
    "Mid": mid_priority_c,
    "Low": low_priority_c
}



def detect_circle_button_touch(centreX, centreY, radius, Touchx, Touchy):
    sqrdistance = (Touchx - centreX)**2 + (Touchy - centreY)**2
    return sqrdistance <= radius**2

def detect_rect_touch(x0, y0, w, h, tx, ty):
    if tx >= x0  and tx <= x0+w:
        if ty >= y0  and ty <= y0+h:
            return True
        else:
            return False
    else:
        return False


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
    
    color_t = RED # for building/testing purposes
    display.draw_rectangle(30, 55, 90,30, color_t)
    display.draw_rectangle(30, 55 + menu_element_offset, 90,30, color_t)
    display.draw_rectangle(30, 55 + menu_element_offset*2, 90,30, color_t)
    display.draw_rectangle(30, 55 + menu_element_offset*3, 90,30, color_t)
    
    #items
    display.draw_text(10, 60, ">  To do", font, RED, background=WHITE)
    display.draw_text(10, 60 + (menu_element_offset), ">  Chat", font, RED, background=WHITE)
    display.draw_text(10, 60 + (menu_element_offset*2), ">  Stats", font, RED, background=WHITE)
    display.draw_text(10, 60 + (menu_element_offset*3), ">  Alarm", font, RED, background=WHITE)
    
def panel_element_select(touchx, touchy):
    for i, (x0, y0, w, h) in enumerate(side_panel_elements):
        if detect_rect_touch(x0, y0, w, h, touchx, touchy):
            print(f"{i+1} option selected")
            return i+1
    return NONE

def home_option_select(touchx, touchy):
    for i, (x0, y0, w, h) in enumerate(home_icons):
        if detect_rect_touch(x0, y0,w,h ,touchx, touchy):
            print(f"{i+1}Option selected in icon menu")
            return i+1
    return NONE
            


def get_current_time(retries=3):
    global saved_time
    """Reads from RTC and updates time/date display"""
    for attempt in range(retries):
        try:
            time_tuple = rtc.get_time()
            if time_tuple:
                year, month, day, hour, minute, second = time_tuple[:6]
                print(f"RTC Time: {year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}")
                saved_time = time_tuple
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
    if now:
        return now
    else:
        return saved_time



def home():
    global last_update
    global saved_time
    display.clear()
    display.fill_hrect(0, 0, 320, 240, BLACK)
    
    time_values = read_rtc_time()
    print("Time:", time_values)
    saved_time = time_values
    # Draw to TFT
    if time_values:
        draw_clock(time_values)
    last_update = utime.ticks_ms()


    # Draw initial button
    side_panel_button()
    
    calendar_sprite = Sprite("images/calendar64-64.raw", 64, 64, display, 20, 60)
    calendar_sprite.draw()
    
    schedeule_sprite = Sprite("images/schedule64-64.raw", 64, 64, display, 90, 60)
    schedeule_sprite.draw()
    
    micicon_sprite = Sprite("images/micicon64-64.raw", 64, 64, display, 160, 60)
    micicon_sprite.draw()
    
    alarm_sprite = Sprite("images/alarmclock64-64.raw", 64, 64, display, 230, 60)
    alarm_sprite.draw()
    
    focus_sprite = Sprite("images/focus_logo64-64.raw", 64, 64, display, 20, 140)
    focus_sprite.draw()

    
    


def draw_clock(t):
    display.draw_text(220, 12, f"{t[3]:02d} : {t[4]:02d}", font, WHITE, background=BLACK)
    display.draw_text(220, 32, f"{t[1]:02d}/{t[2]:02d}", font, WHITE, background=BLACK)


def update_time():
    global last_update
    global saved_time
    if utime.ticks_diff(utime.ticks_ms(), last_update) >= 30000:  # 30s passed
        t = read_rtc_time()
        print("Time:", t)
        #alarm_test.check_alarm(t)   # for alarm
        
        schedule_track_sys.check_for_tasks()
        schedule_track_sys.notification_cooldown()
        
        saved_time = t
      # Draw to TFT
        if t:
           draw_clock(t)
        last_update = utime.ticks_ms()



def to_do_screen():
    
    display.clear()  #clear everything
    side_panel_open = False
    display.draw_text(45, 20, "Events List", font2, RED)
    
    t = read_rtc_time()     # get the time
    print("Time:", t)

    if t:
       draw_clock(t)
    last_update = utime.ticks_ms()
        
    side_panel_button()


def get_task_status(task_number):
    with open("tasks.json", "r") as f:     
        data = ujson.load(f)
        
    tasks = data["tasks"]
    task = tasks[task_number]
    status = task.get("completed").upper()
    
    if status == "YES":
        return True
    else:
        return False




def draw_schedule_cells():

    with open("tasks.json", "r") as f:
        data = ujson.load(f)
        
    tasks = data["tasks"]

    task_number = len(tasks)
    print(f"task_number  = {task_number}")
    task_slot_used = 0
    non_task_color = 9

    for row in range(rows): 
        for col in range(cols):  
            x = col * rect_width  
            y = row * rect_height  

            # Skip the very first slot
            if row == 0 and col == 0:
                continue

            if task_slot_used < task_number:   # Only for actual tasks
                task = tasks[task_slot_used]
                priority = task.get("priority", "Low")   
                cell_color = priority_colors.get(priority, low_priority_c)  

                # Draw cell background first
                display.fill_rectangle(x+17, y, rect_width - 1, rect_height - 1,
                                       colors[cell_color])

                

                # Draw task text
                text = task["task"]
                time_start = task["time"]
                time_end = task["time_end"]

                if len(text) * 7 > max_width_text:
                    chars_fit = max_width_text // 7
                    text = text[:chars_fit - 3] + "..."

                display.draw_text(x+20, y+60, text, arcadepix, BLACK, colors[cell_color])
                display.draw_text(x+20, y+5, "Time", arcadepix, BLACK, colors[cell_color])
                display.draw_text(x+20, y+20, f"{time_start} to", arcadepix, BLACK, colors[cell_color])
                display.draw_text(x+20, y+30, time_end, arcadepix, BLACK, colors[cell_color])
                
                # Draw alarm clock sprite **once per task cell**
                alarm_sprite = Sprite("images/clock12-12.raw", 12, 12, display, x+52, y+2)
                alarm_sprite.draw()

                # Draw status circle
                if get_task_status(task_slot_used):
                    display.fill_circle(x+82, y+7, 5, GREEN)
                else:
                    display.fill_circle(x+82, y+7, 5, BLACK)

             
                task_slot_used += 1

            else:  # Fill empty cells
                display.fill_rectangle(x+17, y, rect_width - 1, rect_height - 1,
                                       colors[non_task_color])





def today_schedule():
    global side_panel_open
    schedule = "SCHEDULE"
    display.clear()
    side_panel_button()
    side_panel_open = False
    
    for i in range(len(schedule)):
        display.draw_text(5, 45 + (i*22), schedule[i], setup.espresso_dolce , WHITE)
        
    draw_schedule_cells()
        
    
    
    
def aimode_ui():
    #draw a small mic at the top right of the screen
    #with the same mute and unmute fuctionality
    display.fill_hrect(0, 0, 320, 240, BLACK) #clear
    
    assistant_module.assistant_led(1)
    mic_sprite = Sprite("images/mic84-106.raw", 84, 106, display, 120, 80)
    mic_sprite.draw()
    time.sleep(0.1)
    print("Listening.. for ai query")
    display.draw_text(270, 210, "Listening...", arcadepix, WHITE)
    display.draw_text(80,40, "AI MODE", arcadepix, WHITE) 
 
    while main_button.value() == 1:
        assistant_module.talk_to_assistant()
        
    display.draw_text(270, 210, "Muted", arcadepix, WHITE)
    print("AI OFf")
    mutemic = Sprite("images/micmute84-106.raw", 84, 106, display, 120, 80)
    mutemic.draw()
    assistant_module.assistant_led(0)
    client.publish(b"jarvis/control", b"sleep")
    time.sleep(0.4)
    
        
def display_ai_response(response):
    display.fill_hrect(0, 0, 320, 240, BLACK)
    x, y= 10, 20
    max_width = 300
    line_height = 20
    
    for i,word in enumerate(response.split()):
        word_len = len(word) * 12
        if x + word_len > max_width:
            x = 10
            y +=line_height
        if  y > 210:
            display.fill_hrect(0,0,320,240, BLACK)
            x,y = 10,20
        
        display.draw_text(x, y, word, font, WHITE)
        x = x+word_len + 15
        time.sleep(0.05)



def task_notification(task, time):
    name= task["task"]
    priority = task["priority"]
    endtime = task["time_end"]
    endhour, endminute = map(int, task_startt.split(":"))  # coverting string to time format
    # ui elements
    display.fill_hrect(0,0,320,240, BLACK)
    print("Notification display")
    #timer until the task finishes *full screen
    #option to quit
    #option to skip
    
    


def task_reminder(task,font):
    
    name = task["task"]
    starthour, startmin = map(int, task["time"].split(":"))
    endhour, endmin = map(int, task["time_end"].split(":"))
    
    display.fill_hrect(10,170, display.width -10, 60, WHITE)
    display.draw_text(25, 180,name, font, RED, WHITE)
    display.draw_text(40, 205, f"> {starthour}:{startmin}", font, RED, WHITE)
    display.draw_text(120, 205, f" to {endhour}:{endmin}", font, RED, WHITE)
    display.fill_circle(display.width-15,200 , 12, RED)
    

def clear_notification():
    display.fill_hrect(10,170, display.width -10, 60, BLACK)
    
    

      





