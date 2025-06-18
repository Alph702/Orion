import speech_recognition as sr
import asyncio
import time

class FastNaturalSpeechRecognition:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # Already low
        self.recognizer.dynamic_energy_threshold = False  # Static threshold is faster
        self.recognizer.pause_threshold = 0.5  # Waits just a short time after you stop

    async def recognize_from_microphone(self) -> str:
        try:
            with sr.Microphone() as source:
                print("🎙️ Listening... (speak at your pace)")
                audio_data = self.recognizer.listen(source)  # No timeout, unlimited

            start = time.time()
            result = await asyncio.to_thread(self.recognizer.recognize_google, audio_data)
            print(f"✅ Processed in {time.time() - start:.2f} sec")
            return result
        except sr.UnknownValueError:
            return "🤷 Sorry, I didn't catch that."
        except sr.RequestError as e:
            return f"🌐 API error: {e}"
        except Exception as e:
            return f"⚠️ Error: {e}"

async def main():
    recognizer = FastNaturalSpeechRecognition()
    while True:
        result = await recognizer.recognize_from_microphone()
        print(f"🗣️ {result}")
        if result.lower() in ["exit", "quit"]:
            break

if __name__ == "__main__":
    asyncio.run(main())
