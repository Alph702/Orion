import asyncio
from Brain.model import model
from Backend.STT import FastNaturalSpeechRecognition

async def voice_loop():
    print("🤖 Orion Assistant (voice only)")
    stt = FastNaturalSpeechRecognition()
    stt.start_background_listener()  # ✅ Start once only

    try:
        while True:
            user_input = await stt.handle()  # ✅ Await from queue only
            if not user_input.strip():
                continue
            print(f"🗣️ {user_input}")
            await model(user_input, stt.stop)
    except KeyboardInterrupt:
        stt.stop_background_listener()
        print("👋 Exiting on keyboard interrupt.")

if __name__ == '__main__':
    asyncio.run(voice_loop())
