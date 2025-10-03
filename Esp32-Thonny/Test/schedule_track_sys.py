import time
from machine import Pin
import utime
from setup import display, rtc, font, font2, rtc_power, spi, touch
import ui_module
import calendar_module as cal
import assistant_module as assistant
import ujson

import alarm_test

last_notification_time = None

def subtract_minutes(time_tuple, minutes_to_subtract):
    hour, minute = time_tuple
    total_minutes = hour * 60 + minute - minutes_to_subtract
   
    total_minutes %= 24 * 60  
    
    new_hour = total_minutes // 60
    new_minute = total_minutes % 60
    return (new_hour, new_minute)

def check_for_tasks():
    global last_notification_time
    with open("tasks.json", "r") as f:
        data = ujson.load(f)
        for event in data["tasks"]:
            task_name = event["task"]
            task_priority = event["priority"]
            task_startt = event["time"]
            task_endt = event["time_end"]
            task_status = event["completed"]
            
            taskhour, taskminute = map(int, task_startt.split(":"))  # coverting string to time format
            task_early_remindert = subtract_minutes((taskhour,taskminute), 30) #task time -30 min
            
            reminder_hour, reminder_minute = task_early_remindert
            currenthour, currentminute = map(int,ui_module.saved_time[3:5]) # current time
            
            
            if (currenthour, currentminute) == (reminder_hour, reminder_minute) and task_status != "Yes":
                ui_module.task_reminder(event, ui_module.font)
                last_notification_time = (currenthour, currentminute)
                
                # reminder 
            if (currenthour, currentminute) == (taskhour, taskminute) and task_status != "Yes":
                ui_module.task_reminder(event, ui_module.font)
                last_notification_time = (currenthour, currentminute)
                #notification to begin task


def notification_cooldown():
    global last_notification_time
    currenthour, currentmin = map(int, ui_module.saved_time[3:5])
    
    if last_notification_time:
        cooldownhour, cooldownmin = alarm_test.add_minutes(last_notification_time,1)
        if (currenthour, currentmin) >= (cooldownhour, cooldownmin):
            ui_module.clear_notification()
            last_notification_time = None
    

