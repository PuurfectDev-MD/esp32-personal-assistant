# main.py
import time
from machine import Pin
import utime
from setup import display, rtc, font, font2, rtc_power, spi, touch
import ui_module
import calendar_module as cal
import assistant_module as assistant


alarms = []

def set_alarm(alarm_time):
    global alarms
    hour, minute = alarm_time[:2]
    alarms.append([hour, minute])
    print("Alarm succesfully set")
    
def check_alarm():
    