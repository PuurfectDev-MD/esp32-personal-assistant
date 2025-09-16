from PIL import Image

# --- Configuration ---
input_file = "alarmclock.png"     # Your PNG image
output_file = "alarmclock64-64.raw"    # Output raw file
width = 64               # Target width
height = 64               # Target height

# --- Open and resize image ---
img = Image.open(input_file).convert("RGB")
img = img.resize((width, height))

# --- Convert to RGB565 ---
raw_data = bytearray()
for y in range(height):
    for x in range(width):
        r, g, b = img.getpixel((x, y))
        # RGB565 conversion
        rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        raw_data.append((rgb565 >> 8) & 0xFF)  # high byte
        raw_data.append(rgb565 & 0xFF)         # low byte

# --- Save to raw file ---
with open(output_file, "wb") as f:
    f.write(raw_data)

print(f"Saved RGB565 raw file: {output_file} ({len(raw_data)} bytes)")



