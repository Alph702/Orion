import time
import sounddevice as sd
import soundfile as sf
import io
import asyncio
from edge_tts import Communicate
from gtts import gTTS
import pyttsx3
from groq import Groq
from dotenv import load_dotenv
import os
import tempfile

# Load environment variables from .env
load_dotenv(dotenv_path='../.env')

groq_api = os.getenv('GroqAPI')
if not groq_api:
    raise ValueError("❌ GroqAPI environment variable is not set in .env file.")

class OrionTTS:
    def __init__(self, engine="edge"):  # Options: gtts, edge, pyttsx3
        self.engine = engine.lower()

    async def speak(self, text: str):
        
        if self.engine == "gtts":
            await self._speak_gtts(text)
        elif self.engine == "edge":
            await self._speak_edge_tts(text)
        elif self.engine == "pyttsx3":
            self._speak_offline(text)
        elif self.engine == "groq":
            self._speak_groq(text)
        else:
            print("Unknown TTS engine.")
        
    async def _speak_edge_tts(self, text):
        
        start_time = time.time()
        communicate = Communicate(text=text, voice="en-GB-RyanNeural")  # Avoid "format" param
        audio_stream = io.BytesIO()

        # Collect audio data chunks
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])

        # Rewind to start
        audio_stream.seek(0)
        end_time = time.time()
        print(f"TTS operation took {end_time - start_time:.2f} seconds.")
        # Decode and play the audio
        try:
            data, samplerate = sf.read(audio_stream, dtype='int16')
            sd.play(data, samplerate)
            sd.wait()
        except Exception as e:
            print("Playback failed:", e)

    async def _speak_gtts(self, text):
        start_time = time.time()
        tts = gTTS(text)
        stream = io.BytesIO()
        tts.write_to_fp(stream)
        stream.seek(0)
        data, samplerate = sf.read(stream, dtype='int16')
        end_time = time.time()
        print(f"TTS operation took {end_time - start_time:.2f} seconds.")
        sd.play(data, samplerate)
        sd.wait()

    def _speak_offline(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    
    def _speak_groq(self, text):
        start_time = time.time()
        client = Groq(api_key=groq_api)

        # Create a temporary file and write audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_path = temp_audio.name
            temp_audio.write(
                client.audio.speech.create(
                    model="playai-tts",
                    voice="Atlas-PlayAI",
                    response_format="wav",
                    input=text,
                ).read()
            )

        end_time = time.time()
        print(f"TTS operation took {end_time - start_time:.2f} seconds.")
        # Direct stream read without fully loading into memory
        with sf.SoundFile(temp_path) as f:
            sd.play(f.read(dtype='float32'), f.samplerate)
            sd.wait()
        os.remove(temp_path)

# 🧪 Example usage
async def main():
    tts = OrionTTS(engine="groq")  # Change to 'gtts', 'pyttsx3', or 'groq' as needed
    while True:
        user = input("> ")
        await tts.speak("Hello! This is Orion. I will now speak in short chunks, just like a human assistant.")
        if user.lower() in ["exit", "quit", "stop"]:
            print("👋 Exit requested by voice.")
            break

if __name__ == "__main__":
    asyncio.run(main())
