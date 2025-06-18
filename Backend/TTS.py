import time
import sounddevice as sd
import soundfile as sf
import io
import asyncio

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
        else:
            print("Unknown TTS engine.")
        

    async def _speak_edge_tts(self, text):
        from edge_tts import Communicate
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
        from gtts import gTTS
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
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

# 🧪 Example usage
async def main():
    tts = OrionTTS(engine="edge")  
    await tts.speak("Hello! This is Orion. I will now speak in short chunks, just like a human assistant.")

if __name__ == "__main__":
    asyncio.run(main())
