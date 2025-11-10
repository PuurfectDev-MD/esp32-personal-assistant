#for focus
import ui_module
import time
import utime
import machine
import setup
from setup import display, rtc, font, font2, rtc_power, spi, touch, colors, arcadepix
import ui_module
import esp32_comm_to_cam as camboard
focused = False
focused_time = (None, None)
question_button = setup.yellow_button
timer_time = (0,0)


WHITE   = 0xFFFF
BLACK   = 0x0000

def begin_focus():
    camboard.send_message("begin focus")
    print("Message Being focus sent. Focus mode started")
    timer_time = timer()
       

def timer(t=None):
    global timer_time
    global focused
    start_seconds = utime.time()
    
    
    while focused:
        current_seconds = utime.time()
        elapsed = current_seconds-start_seconds
        
        minutes = elapsed // 60
        seconds = elapsed % 60
        
        display.draw_text(190, 105, f"{minutes:02d} : {seconds:02d}", font, BLACK, WHITE)
        timer_time = (minutes,seconds)
        
        
        
           # Check for stop button
        coords = touch.get_touch()
        if coords is not None:
            x, y = coords
            if ui_module.detect_circle_button_touch(230, 120, 80, x, y):
                camboard.send_message("end focus")
                focused = False
                break
        if question_button ==1:
            pass
            #draws a mic
            #send a message to MQTT to listen
            # --- MQTT sends the text to speech output
            # sends it to the ai api and gets the response
            
        time.sleep(1)
    print("Focus Period-ended")   
    return timer_time  #when the stop button is pressed return elasped time





focused = True
ui_module.focus_ui()
print("Beigning camera feed")
begin_focus()



