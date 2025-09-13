import machine
import math
import time

dac = machine.DAC(machine.Pin(25))

# Parameters for the tone
frequency = 440  # Frequency in Hz (A4 note)
duration = 3    # Duration in seconds
sample_rate = 8000  # Samples per second (DAC update rate)
amplitude = 127  # Max amplitude for DAC (0-255)

# Number of samples per wave cycle
samples_per_cycle = int(sample_rate / frequency)

for i in range(duration * sample_rate):
    # Generate a sine wave value between 0 and 255
    angle = 2 * math.pi * (i % samples_per_cycle) / samples_per_cycle
    value = int((math.sin(angle) + 1) * (amplitude / 2))
    dac.write(value)
    time.sleep_us(int(1_000_000 / sample_rate))

# Turn off DAC output
dac.write(0)
