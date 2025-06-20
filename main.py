import asyncio
from Backend.STT import FastNaturalSpeechRecognition
from Backend.TTS import OrionTTS
from Brain.model import model
from Brain.ChatBot import Chatbot  # Handles queries, speech & logging

class OrionCore:
    def __init__(self):
        self.recognizer = FastNaturalSpeechRecognition()
        self.tts = OrionTTS(engine="pyttsx3")  # You can switch to 'gtts' or 'edge'
        self.exit_requested = False

    async def process_input(self, user_input):
        try:
            # Run the intent routing model
            responses = await model(user_input)

            for Model, query in responses:
                if Model == "CHATBOT":
                    await Chatbot(query=query).process_query()  # Already processes and speaks
                elif Model == "Exit":
                    print("🛑 Exit signal from model.")
                    self.exit_requested = True
                elif Model == "EXEC":
                    print(f"⚙️ Execute command: {query}")
                    # Optional: implement executor here
                else:
                    print(f"🔎 Unknown intent: {Model} -> {query}")

        except Exception as e:
            print(f"❌ Error while processing input: {e}")

    async def run(self):
        while not self.exit_requested:
            try:
                user_input = await self.recognizer.recognize_from_microphone()
                print(f"🗣️ You said: {user_input}")

                if user_input.strip().lower() in ["exit", "quit", "stop"]:
                    print("👋 Exit requested by voice.")
                    self.exit_requested = True
                    continue

                await self.process_input(user_input)
                await asyncio.sleep(0.5)  # slight pause to stabilize loop

            except Exception as e:
                print(f"❌ STT Error: {e}")
                await self.tts.speak("Sorry, I couldn't understand that.")
                await asyncio.sleep(1)

        print("✅ Orion shutting down gracefully.")

# 🎯 Entry point
async def main():
    core = OrionCore()
    await core.run()

if __name__ == "__main__":
    asyncio.run(main())
