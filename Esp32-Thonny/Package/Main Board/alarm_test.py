import time
from machine import Pin
import utime
from setup import display, rtc, font, font2, rtc_power, spi, touch

import ui_module
import calendar_module as cal
import assistant_module as assistant


alarms = [(19,41)]

def set_alarm(alarm_time):
    global alarms
    hour, minute = alarm_time[:2]
    
    if (hour, minute) in alarms:
        print("Alarm already present")
    else:
        alarms.append((hour, minute))
        print("Alarm succesfully set")
        
   
    
def check_alarm(time):
    year, month, day, hour, minute, second = time[:6]
    
    for alarm in alarms:
        if (hour, minute) == alarm:
            print("Alarm time detected and sound is enabled")
            #produces an alarm sound
            return alarm
    
def add_minutes(time_tuple, minutes_to_add):
    hour, minute = time_tuple
    total_minutes = hour * 60 + minute + minutes_to_add
   
    total_minutes %= 24 * 60  
    
    new_hour = total_minutes // 60
    new_minute = total_minutes % 60
    return (new_hour, new_minute)


def snooze(time_to_snooze):
    new_time = add_minutes(time_to_snooze,5)
    alarms.remove(time_to_snooze)
    alarms.append(new_time)
    
def delete_alarm(time_to_delete):
    alarms.remove(time_to_delete)
    print("Alarm succesfully deleted")
    
    
  




