import asyncio
import edge_tts
import sounddevice as sd
import soundfile as sf
import io    

async def speak(text):
    tts = edge_tts.Communicate(text, "en-US-NancyMultilingualNeural")
    audio_data = b""
    
    async for chunk in tts.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    
    # Play directly from memory
    with io.BytesIO(audio_data) as f:
        data, samplerate = sf.read(f)
        sd.play(data, samplerate)
        sd.wait()


def init_speak(text):
    asyncio.run(speak(text))