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
        self.recognizer.energy_threshold = 300  # Already low
        self.recognizer.dynamic_energy_threshold = False  # Static threshold is faster
        self.recognizer.pause_threshold = 0.5  # Waits just a short time after you stop
        self.exit = True  # Control flag to stop listening
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
            status = f.read().strip()
        if status.lower() == 'true':
            self.exit = True
        else:
            self.exit = False 
    
    def set_exit_status(self, status: bool):
        with open('Brain/Data/stop.orion', 'w') as f:
            f.write(str(status))
        self.exit = status
    
    def _callback(self, recognizer, audio):
        try:
            text = recognizer.recognize_google(audio)
            self.get_exit_status()
            if self.exit:
                if text.lower() in ["orion", "hi orion", "hey irion", "wakeup", "wake up", "wakeup orion", "wake up orion"]:
                    self.set_exit_status(False)
            self.tts.stop()
            print(f"🎤 Recognized (raw): {text}")
            loop = self.loop
            if loop is None:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None
            self.audio_handler.put_threadsafe(text, loop)
        except sr.UnknownValueError:
            self.audio_handler.put_threadsafe("🤷 Sorry, I didn't catch that.", self.loop)
        except sr.RequestError as e:
            self.audio_handler.put_threadsafe(f"🌐 API error: {e}", self.loop)
        except Exception as e:
            self.audio_handler.put_threadsafe(f"⚠️ Error: {e}", self.loop)

    def start_background_listener(self):
        if self.listener is None:
            self._stop_event.clear()
            print("🎧 Background listener started.")
            if self.loop is None:
                try:
                    self.loop = asyncio.get_running_loop()
                except RuntimeError:
                    self.loop = None
            self.listener = self.recognizer.listen_in_background(self.microphone, self._callback)

    def stop_background_listener(self):
        if self.listener:
            self.listener(wait_for_stop=False)
            self.listener = None
            print("🛑 Background listener stopped.")

    async def get_audio_result(self):
        return await self.audio_handler.get()

    async def recognize_from_microphone(self) -> str:
        try:
            with sr.Microphone() as source:
                print("🎙️ Listening... (speak at your pace)")
                audio_data = self.recognizer.listen(source)  # No timeout, unlimited

            result = await asyncio.to_thread(self.recognizer.recognize_google, audio_data)
            self.get_exit_status()
            if self.exit:
                if result.lower() in ["orion", "hi orion", "hey irion", "wakeup", "wake up", "wakeup orion", "wake up orion"]:
                    self.set_exit_status(False)
            if not self.exit:
                return result
            else:
                return "Orion is off currently."
        except sr.UnknownValueError:
            return "🤷 Sorry, I didn't catch that."
        except sr.RequestError as e:
            return f"🌐 API error: {e}"
        except Exception as e:
            return f"⚠️ Error: {e}"
    def stop(self):
        self.set_exit_status(True)
    
    async def handle(self):
        result = ""
        if self.tts._isruning():
            self.start_background_listener()
            result = await self.get_audio_result()  # <-- Await the coroutine
            self.stop_background_listener()
        elif not self.tts._isruning():
            result = await self.recognize_from_microphone()
        
        return result

async def main():
    recognizer = FastNaturalSpeechRecognition()
    recognizer.start_background_listener()

    try:
        while True:
            result = await recognizer.get_audio_result()
            if result is None:
                continue
            print(f"🗣️ {result}")
            if result.lower() in ["exit", "quit", "stop"]:
                recognizer.stop_background_listener()
                break
    except KeyboardInterrupt:
        recognizer.stop_background_listener()
        print("👋 Exiting on keyboard interrupt.")

if __name__ == "__main__":
    asyncio.run(main())
