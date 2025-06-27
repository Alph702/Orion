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
import pygame
from pathlib import Path

# Load environment variables from .env
load_dotenv(dotenv_path='../.env')

groq_api = os.getenv('GroqAPI')
if not groq_api:
    raise ValueError("❌ GroqAPI environment variable is not set in .env file.")

class OrionTTS:
    def __init__(self, engine="pyttsx3"):  # Options: gtts, edge, pyttsx3
        self.engine = engine.lower()
        pygame.mixer.init()
        self.lock = asyncio.Lock()
    
    def _isruning(self):
        with open("Brain\\Data\\TTS_runing.orion", 'r') as f:
            return bool(f.read())
    
    def _stop(self):
        with open("Brain\\Data\\TTS_runing.orion", 'w') as f:
            f.write(str(False))
        
    def _start(self):
        with open("Brain\\Data\\TTS_runing.orion", 'w') as f:
            f.write(str(True))

    async def speak(self, text: str):
        
        if self.engine == "gtts":
            await self._speak_gtts(text)
        elif self.engine == "edge":
            await self._speak_edge_tts(text)
        elif self.engine == "pyttsx3":
            await self._speak_offline(text)
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

    async def _speak_offline(self, text):
        async with self.lock:
            self.stop()
        
        self._start()
        engine = pyttsx3.init()
        temp_path = "Brain/Data/audio.wav"
        self.stop()  # Stop any existing audio first
        engine.save_to_file(text, temp_path)
        engine.runAndWait()

        # Wait to ensure file is written completely
        await asyncio.sleep(0.2)

        try:
            pygame.mixer.music.load(temp_path)
            self._start()  # Set running flag
            pygame.mixer.music.play()

            # Wait until playback finishes
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)

        except Exception as e:
            print(f"⚠️ TTS Playback Error: {e}")
        finally:
            self.stop()
            time.sleep(0.2)
            current_dir = Path.cwd()
            parent_dir = current_dir.parent
            print(f"{os.path.abspath(temp_path)}")
            os.system(f'del /F /Q "{os.path.abspath(temp_path)}')

        
    def stop(self):
        pygame.mixer.music.stop()
        self._stop()

    def pause(self):
        if self._isruning():
            pygame.mixer.music.pause()
            self._stop()

    def unpause(self):
        if not self._isruning():
            pygame.mixer.music.unpause()
            self._start()
            
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
    tts = OrionTTS(engine="pyttsx3")  # Change to 'gtts', 'pyttsx3', or 'groq' as needed
    while True:
        user = input("> ")
        await tts.speak("Hello! This is Orion. I will now speak in short chunks, just like a human assistant.")
        time.sleep(1)
        tts.pause()
        time.sleep(1)
        tts.unpause()
        if user.lower() in ["exit", "quit", "stop"]:
            print("👋 Exit requested by voice.")
            break

if __name__ == "__main__":
    asyncio.run(main())
