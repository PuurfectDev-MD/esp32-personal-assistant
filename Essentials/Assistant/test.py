import pyttsx3  # library for text to speech
import time
import datetime
import speech_recognition as sr # for speech recognition
import paho.mqtt.client as mqtt
from tts import init_speak

# MQTT Settings
BROKER_IP = "192.168.0.116"   # broker IP
JARVIS_TOPIC = "jarvis/responses"
CONTROL_TOPIC = "jarvis/control"
AI_RESPONSE = "ai/responses"
AI_REQUEST = "ai/requests"

listening = False
ai_mode= False
speaking_queue = False

r = sr.Recognizer()  #keeps the laptops mic as the source for the audio
keywords = [("jarvis", 1), ("hey jarvis", 1), ("wake up", 1), ("Maya",1)]  # wake up words



def on_message(client, userdata, msg):  # when the broker recieves a message
    global listening, speaking_queue
    topic = msg.topic
    payload = msg.payload.decode()
    print(f"📩 Message received on {topic}: {payload}")

    if topic == CONTROL_TOPIC:  #identifies which topic/stream the data is received from
        if payload == "wake":
            print("⚡ Wake command received from ESP32")
            listening = True
        elif payload == "sleep":
            listening = False

    elif topic == AI_RESPONSE:
        Speak(payload)  # speak AI response immediately
        speaking_queue = False


def send_to_mqtt(topic, message):  #to send data to a stream in the broker
    client.publish(topic, message)
    print(f"📤 Sent to MQTT: {message}")



def Speak(text):  # uses text to speech lib
    init_speak(text)
    print(f"Jarvis: {text}")
  

def recognize_main():  #to recognize commands using the audio source
    global listening
    global ai_mode
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Listening for commands...")
        audio = r.listen(source, phrase_time_limit=10)
    try:
        data = r.recognize_google(audio).lower()
        print(f"You: {data}")

        if "how are you" in data:
            Speak("I am fine, sir!")
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
            send_to_mqtt(CONTROL_TOPIC,"LED on")
            Speak("The LED is on sir.")
            
        elif "led" in data and "off" in data:
            print("You: LED off")
            send_to_mqtt(CONTROL_TOPIC,"LED off")
            Speak("The LED is off sir.")
        elif "chantal" in data and "think" in data:
            print("You want to know about her?")
            Speak("Chantal is smart and pretty. Did u not know that?")
            
        elif "connect" in data and "ai" in data:
            print("Connecting with AI")
            Speak("Connecting with AI sir. Give me a moment.")
            send_to_mqtt(CONTROL_TOPIC,"Connect AI")
           
            listening = False
            ai_mode = True

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



def wakeupCall():   # to wake the assistant up
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Say Jarvis...")
        audio = r.listen(source)  #listens to the mic
    try:
        speech_as_text= r.recognize_sphinx(audio, keyword_entries=keywords)  # matches the decoded speech to the keywords
        print(f" You: {speech_as_text}")
        if "jarvis" in speech_as_text or "hey jarvis" in speech_as_text or "wake up" in speech_as_text:
          Speak("Yes sir?")
          time.sleep(0.6)
          recognize_main()  #main command detection function
    except sr.UnknownValueError:
           pass
    


# ---------- MQTT SETUP ----------
client = mqtt.Client(client_id="jarvis_pc")   
client.on_message = on_message  #after a message is recieved - this function is automatically called
client.connect(BROKER_IP, 1883, 60)
client.subscribe(JARVIS_TOPIC)
client.subscribe(CONTROL_TOPIC)
client.subscribe(AI_RESPONSE) 
client.loop_start()  


while True:
    if listening  and not ai_mode: #only listens to the wakeup call if not speaking
        wakeupCall()
    if ai_mode :  # for ai conversations until ended 
        while ai_mode and not speaking_queue:
            print("Listening for ai query")
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source, phrase_time_limit=6)
            try:
                data = r.recognize_google(audio).lower()
                print(f" You: {data}")

                
                if "go back" in data or "end chat" in data or "close chat" in data:
                    print("Closing connection with AI")
                    Speak("Closing connection with AI")
                    send_to_mqtt(CONTROL_TOPIC, "Assistant mode")
                    ai_mode = False
                    listening= True

                else:
                    send_to_mqtt(AI_REQUEST, data)
                    speaking_queue = True

                
            except sr.UnknownValueError:
                pass

    time.sleep(0.2)

