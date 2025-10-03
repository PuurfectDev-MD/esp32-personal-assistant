# main.py
import time
from machine import Pin
import utime
from setup import display, rtc, font, font2, rtc_power, spi, touch
import ui_module
import calendar_module as cal
import alarm_test
import assistant_module
import schedule_track_sys


WHITE   = 0xFFFF
BLACK   = 0x0000
RED     = 0xF800
GREEN   = 0x07E0

working=  False
main_button = Pin(13, Pin.IN, Pin.PULL_UP)  # active LOW

time.sleep(1)
print(main_button.value())

while not working: 
    if main_button.value() == 0:
        print(main_button.value())
        working = True
        print(f"Device activated, Working :{working}")
        
    
  
  
print("touch initialized")
rtc_power.value(1)

last_update = 0

ui_module.home()
cal.connect_wifi()

    

while working:
    #print(main_button.value())
  

    coords = touch.get_touch()
    if coords is not None:  #if touch is detected
        x, y = coords
        print(f"x : {x}, y: {y}")
        
        menu_select = ui_module.panel_element_select(x,y)
        
        
        if ui_module.detect_circle_button_touch(25, 220, 20, x, y):
            if not ui_module.side_panel_open:
                ui_module.side_panel()
                ui_module.side_panel_open = True
            else:
                #display.fill_hrect(0, 0, 200, 240, 0x0000)  # BLACK
                ui_module.home()
                ui_module.side_panel_button()    
                ui_module.side_panel_open = False
        
        if menu_select != 0:
            if menu_select == 1:
                ui_module.today_schedule()
               
            if menu_select ==2:
                assistant_module.assistant_begin()
        
                
    else:
        x,y =0,0
       
   


    # Update RTC clock display every 30s
    ui_module.update_time()
    
    
    if main_button.value() == 0:  # pressed -  to turn off the device
        working = False
        print("Working =", working)
        display.fill_hrect(0, 0, 320, 240, BLACK)
        time.sleep(0.3) 
        
    time.sleep(0.2)







