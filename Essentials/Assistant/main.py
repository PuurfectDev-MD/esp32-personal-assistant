import pyttsx3
import time
import datetime
import speech_recognition as sr

import paho.mqtt.client as mqtt

# MQTT Settings
BROKER_IP = "192.168.0.116"   # your PC broker IP
TOPIC = "jarvis/responses"
CONTROL_TOPIC = "jarvis/control"

listening = False



r = sr.Recognizer()
keywords = [("jarvis", 1), ("hey jarvis", 1), ("wake up", 1), ("Maya",1)]

rate =100  # voice speed
engine = pyttsx3.init()
voices = engine.getProperty('voices')  #get the different voices
engine.setProperty('voice', voices[0].id) #selection and setting of the voice
engine.setProperty('rate', rate+50) #setting the rate




def on_message(client, userdata, msg):
    global listening
    print(f"📩 Control message: {msg.payload.decode()}")
    if msg.topic == CONTROL_TOPIC and msg.payload.decode() == "wake":
        print("⚡ Wake command received from ESP32")
        listening = True
    if msg.topic ==CONTROL_TOPIC and msg.payload.decode() == "sleep":
        listening = False


def send_to_mqtt(message):
    client.publish(TOPIC, message)
    print(f"📤 Sent to MQTT: {message}")



def Speak(text):
    print(f"Jarvis: {text}")
    engine.say(text)
    time.sleep(2)
    engine.runAndWait()
  

def recognize_main():
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Listening for commands...")
        audio = r.listen(source, phrase_time_limit=6)
    try:
        data = r.recognize_google(audio).lower()
        print(f"You: {data}")

        if "how are you" in data:
            Speak("I am fine, sir!")
            time.sleep(1)
        elif "hello" in data:
            hour = datetime.datetime.now().hour
            if 0 <= hour < 12:
                Speak("Good morning, sir")

            elif 12 <= hour < 18:
                Speak("Good afternoon, sir")
            else:
                Speak("Good evening, sir")
        elif "led" in data and "on" in data:
            print("You: LED On")
            send_to_mqtt("LED on")
            Speak("The LED is on sir.")
            
        elif "led" in data and "off" in data:
            print("You: LED off")
            send_to_mqtt("LED off")
            Speak("The LED is off sir.")
        elif "chantal" in data and "think" in data:
            print("You want to know about her?")
            Speak("Chantal is smart and pretty. Did u not know that?")

        elif "end conversation" in data:
            Speak("Ending our chat. Have a nice day, sir")
            raise SystemExit
        else:
            Speak("I'm sorry sir, I did not understand your request")
            

    except sr.UnknownValueError:
        print("Jarvis did not understand your request")
        Speak("Sorry, I didn't catch that.")
    
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")



def wakeupCall():
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Say Jarvis...")
        audio = r.listen(source)
    try:
        speech_as_text= r.recognize_sphinx(audio, keyword_entries=keywords)
        print(f" You: {speech_as_text}")
        if "jarvis" in speech_as_text or "hey jarvis" in speech_as_text or "wake up" in speech_as_text:
          Speak("Yes sir?")
          recognize_main()  #main repeating loop after call

    except sr.UnknownValueError:
           pass
    


# ---------- MQTT SETUP ----------
client = mqtt.Client(client_id="jarvis_pc")
client.on_message = on_message
client.connect(BROKER_IP, 1883, 60)
client.subscribe(CONTROL_TOPIC)
client.loop_start()


while True:
    if listening:
        wakeupCall()
    time.sleep(0.2)