# hardware.py
from machine import Pin, SPI, I2C
from ili9341 import Display
from xpt2046 import Touch
from ds3231 import DS3231
from xglcd_font import XglcdFont

# SPI and I2C setup
spi = SPI(2, baudrate=10000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)

# Display and Touch
display = Display(spi, cs=Pin(5), dc=Pin(27), rst=Pin(4), width=320, height=240, rotation=270)
touch = Touch(spi, cs=Pin(12), width=320, height=240)

# RTC
rtc = DS3231(i2c)
rtc_power = Pin(33, Pin.OUT)

# Fonts
font = XglcdFont('Unispace12x24.c', 12, 24)
font2 = XglcdFont('Robotron7x11.c', 7, 11)
