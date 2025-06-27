import asyncio
from Brain.model import model
from Backend.STT import FastNaturalSpeechRecognition

async def main():
    print("🤖 Orion Assistant (type 'exit' to quit, press Enter for voice input)")
    stt = FastNaturalSpeechRecognition()
    while True:
        user_input = input("> ")
        if user_input.strip().lower() in ("exit", "quit"):
            print("👋 Goodbye!")
            break
        if user_input.strip() == "":
            user_input = await stt.handle()
            print(f"🗣️ {user_input}")
        response = await model(user_input)

if __name__ == "__main__":
    asyncio.run(main())