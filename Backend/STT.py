import speech_recognition as sr
import asyncio
import time
import threading
from Backend.TTS import OrionTTS

class AudioHandler:
    def __init__(self):
        self.audio_queue = asyncio.Queue()

    async def put(self, message: str):
        await self.audio_queue.put(message)

    def put_threadsafe(self, message: str, loop):
        asyncio.run_coroutine_threadsafe(self.audio_queue.put(message), loop)

    async def get(self):
        return await self.audio_queue.get()

class FastNaturalSpeechRecognition:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 0.5
        self.exit = True
        self.listener = None
        self._stop_event = threading.Event()

        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        self.tts = OrionTTS()
        self.audio_handler = AudioHandler()

    def get_exit_status(self):
        with open('Brain/Data/stop.orion', 'r') as f:
            self.exit = f.read().strip().lower() == 'true'

    def set_exit_status(self, status: bool):
        with open('Brain/Data/stop.orion', 'w') as f:
            f.write(str(status))
        self.exit = status

    def _callback(self, recognizer, audio):
        try:
            text = recognizer.recognize_google(audio)
            self.get_exit_status()
            if self.exit and text.lower() in ["orion", "hi orion", "hey orion", "wakeup"]:
                self.set_exit_status(False)
            if self.tts and self.tts._isruning():
                print("🛑 Barge-in detected! Stopping TTS...")
                self.tts.stop()
            print(f"🎤 Recognized (raw): {text}")
            if not self.exit:
                self.audio_handler.put_threadsafe(text, self.loop)
        except sr.UnknownValueError:
            self.audio_handler.put_threadsafe("🤷 Sorry, I didn't catch that.", self.loop)
        except sr.RequestError as e:
            self.audio_handler.put_threadsafe(f"🌐 API error: {e}", self.loop)
        except Exception as e:
            self.audio_handler.put_threadsafe(f"⚠️ Error: {e}", self.loop)

    def start_background_listener(self):
        if self.listener is None:
            print("🎧 Background listener started.")
            self.listener = self.recognizer.listen_in_background(self.microphone, self._callback)

    def run_background_listener(self):
        self.start_background_listener()
        while not self._stop_event.is_set():
            time.sleep(0.1)

    def start_in_thread(self):
        threading.Thread(target=self.run_background_listener, daemon=True).start()

    def stop_background_listener(self):
        if self.listener:
            self.listener(wait_for_stop=False)
            self.listener = None
            self._stop_event.set()
            print("🛑 Background listener stopped.")

    async def get_audio_result(self):
        return await self.audio_handler.get()

    async def recognize_from_microphone(self) -> str:
        try:
            with sr.Microphone() as source:
                print("🎙️ Listening... (speak at your pace)")
                audio_data = self.recognizer.listen(source)
            result = await asyncio.to_thread(self.recognizer.recognize_google, audio_data)
            self.get_exit_status()
            if self.exit and result.lower() in ["orion", "hi orion", "wake up"]:
                self.set_exit_status(False)
            return result if not self.exit else None
        except sr.UnknownValueError:
            return "🤷 Sorry, I didn't catch that."
        except sr.RequestError as e:
            return f"🌐 API error: {e}"
        except Exception as e:
            return f"⚠️ Error: {e}"

    async def handle(self):
        if self.tts._isruning():
            return await self.get_audio_result()
        else:
            return await self.recognize_from_microphone()

    def stop(self):
        self.set_exit_status(True)
