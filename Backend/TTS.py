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

load_dotenv(dotenv_path='../.env')
groq_api = os.getenv('GroqAPI')
if not groq_api:
    raise ValueError("❌ GroqAPI not set")

class OrionTTS:
    def __init__(self, engine="pyttsx3"):
        self.engine = engine.lower()
        self.lock = asyncio.Lock()

    def _isruning(self):
        with open("Brain/Data/TTS_runing.orion", 'r') as f:
            return f.read().strip().lower() == "true"

    def _stop(self):
        with open("Brain/Data/TTS_runing.orion", 'w') as f:
            f.write("false")

    def _start(self):
        with open("Brain/Data/TTS_runing.orion", 'w') as f:
            f.write("true")

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
        communicate = Communicate(text=text, voice="en-GB-RyanNeural")
        audio_stream = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])
        audio_stream.seek(0)
        data, samplerate = sf.read(audio_stream, dtype='int16')
        sd.play(data, samplerate)
        sd.wait()

    async def _speak_gtts(self, text):
        tts = gTTS(text)
        stream = io.BytesIO()
        tts.write_to_fp(stream)
        stream.seek(0)
        data, samplerate = sf.read(stream, dtype='int16')
        sd.play(data, samplerate)
        sd.wait()

    async def _speak_offline(self, text):
        self.stop()
        self._start()
        engine = pyttsx3.init()
        path = "Brain/Data/audio.wav"
        engine.save_to_file(text, path)
        engine.runAndWait()
        await asyncio.sleep(0.2)
        try:
            data, samplerate = sf.read(path, dtype='float32')
            sd.play(data, samplerate)
            while sd.get_stream().active:
                await asyncio.sleep(0.1)
        finally:
            self._stop()

    def stop(self):
        try:
            sd.stop()
            self._stop()
        except Exception as e:
            print(f"⚠️ Stop failed: {e}")

    def _speak_groq(self, text):
        client = Groq(api_key=groq_api)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            path = temp_audio.name
            temp_audio.write(
                client.audio.speech.create(
                    model="playai-tts",
                    voice="Atlas-PlayAI",
                    response_format="wav",
                    input=text,
                ).read()
            )
        with sf.SoundFile(path) as f:
            sd.play(f.read(dtype='float32'), f.samplerate)
            sd.wait()
        os.remove(path)
