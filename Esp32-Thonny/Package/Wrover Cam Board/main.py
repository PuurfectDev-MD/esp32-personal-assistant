import setup
from setup import focus
import time
import esp32_comm
import camfocuspic_capture as feedcapture
import machine

# Initialize communication first
esp32_comm.init_communication()

print("🚀 System starting...")
led = machine.Pin(2, machine.Pin.OUT)


while True:
    # Check for new messages
    message = esp32_comm.get_received_message()
    
    if message == "begin focus":
        led.value(1)
        focus = True
        print("🎯 Starting focus mode...")
        feedcapture.main()
        print("Focus Period Ended")
        
    time.sleep(0.5)
