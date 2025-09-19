# Personal Assistant Project

This project combines **ESP32 hardware** (running MicroPython) with a **Python server** on my laptop.


#Functionalities:
 > Schedule Tracker
 > Prodcutivity Statistics
 > Calnder api integrations to streamline daily routines
 > Alarms
 > Personal Assistant
 > AI conversation - (GPT 3.5 mini currently in use)

## Structure
- `Esp32 Flash` → These are the content of the flash - excluding the main package(code)
- `Esp32- Thonny` → 
         Library : The necessary libraries
         Package : Upload the entire folder to flash of esp32 to run the system
         Snippets: Individual functionalities broken up 
         Test: For testing and improvement purposes

- `Essentials` → 
         Assistant : For speech communcation - to access the mic of the PC
         Audio Type conversion : Server to covert mp3 into .wav for esp32 to play it from the board.
- `README.md` → this file (documentation)



## To begin virtual environment:
In cmd - cd '{path of the main folder}'
         ./{name of the virtual env folder}/Scripts/Activate.ps1

## To being the MQTT broker:
cmd : mosquitto -c "C:\\Program Files\\mosquitto\\mosquitto.conf" -v
*** -v means verbose, so you’ll see connection logs.
