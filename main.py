import asyncio
from Backend.STT import FastNaturalSpeechRecognition
from Backend.TTS import OrionTTS
from Backend.model import model

class OrionCore:
    def __init__(self):
        self.recognizer = FastNaturalSpeechRecognition()
        self.tts = OrionTTS(engine="edge")  # Change to "gtts" or "edge" if needed
        self.exit_requested = False

    async def process_input(self, user_input):
        try:
            responses = await model(user_input)

            chatbot_responses = []
            for response_type, content in responses:
                if response_type == "CHATBOT":
                    chatbot_responses.append(content)
                elif response_type == "Exit":
                    print("🛑 Exit signal from model.")
                    self.exit_requested = True
                elif response_type == "EXEC":
                    print(f"⚙️ Execute command: {content}")
                else:
                    print(f"🔎 Unknown response type: {response_type} -> {content}")

            if chatbot_responses:
                response_text = " ".join(chatbot_responses)
                print(f"🤖 Orion: {response_text}")
                await self.tts.speak(response_text)

        except Exception as e:
            print(f"❌ Error while processing input: {e}")

    async def run(self):
        while True:
            user_input = await self.recognizer.recognize_from_microphone()
            print(f"🗣️ User: {user_input}")

            # Exit only after finishing everything
            if user_input.strip().lower() in ["exit", "quit"]:
                print("👋 Exit requested by user.")
                self.exit_requested = True

            await self.process_input(user_input)

            if self.exit_requested:
                print("✅ Finished last task. Exiting gracefully.")
                break

# Entry point
async def main():
    core = OrionCore()
    await core.run()

if __name__ == "__main__":
    asyncio.run(main())
