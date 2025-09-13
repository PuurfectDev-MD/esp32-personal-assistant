from machine import DAC, Pin
import time

dac = DAC(Pin(25))  # Use GPIO 25

def play_wav(filename):
    try:
        with open(filename, 'rb') as f:
            f.read(44)  # Skip WAV header

            while True:
                data = f.read(1024)
                if not data:
                    break
                for b in data:
                    dac.write(b)        # Write value to DAC
                    time.sleep_us(125)  # 8000 Hz sample rate
    except Exception as e:
        print("Error:", e)

play_wav("apocalyspe.wav")
