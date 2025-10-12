import time
from machine import Pin
import utime
import ujson
import urequests

from API_KEYS import Open_router_api_key as open_router_api

API_KEY = open_router_api

URL = "https://openrouter.ai/api/v1/chat/completions"



# Ask GPT-3.5 Turbo
def ask_gpt(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    body = ujson.dumps({
        "model": "openai/gpt-3.5-turbo",
        "messages" : [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. "
                "The user's name is Manish. "
                "Always answer in less than 120 words."
                "Keep the answers information packed but concise"
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
     
    })
    
    response = urequests.post(URL, headers=headers, data=body)
    
    if response.status_code == 200:
        try:
            return response.json()["choices"][0]["message"]["content"]
        except Exception:
            return "Error: Unexpected response format"
    else:
        print(f"Error {response.status_code}: {response.text}")
        return f"Error: {response.status_code}"
