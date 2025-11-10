import setup
import time
import esp32_comm
import camfocuspic_capture as feedcapture

# Initialize communication first
esp32_comm.init_communication()

print("🚀 System starting...")

while True:
    # Check for new messages
    message = esp32_comm.get_received_message()
    
    if message.lower() == "begin focus":
        print("🎯 Starting focus mode...")
        feedcapture.main()
        
    time.sleep(0.5)