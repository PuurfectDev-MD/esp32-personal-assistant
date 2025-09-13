from flask import Flask, request, send_file
from gtts import gTTS
import subprocess

app = Flask(__name__)
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"

@app.route('/speak')
def speak():
    text = request.args.get('text', '')
    if not text:
        return 'No text provided', 400

    mp3_path = "speech.mp3"
    wav_path = "speech.wav"

    # Generate MP3
    tts = gTTS(text=text, lang='en')
    tts.save(mp3_path)

    # Convert MP3 to WAV
    command = [FFMPEG_PATH, '-y', '-i', mp3_path, '-ar', '16000', '-ac', '1', wav_path]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Serve WAV file
    return send_file(wav_path, mimetype='audio/wav')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
