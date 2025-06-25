import asyncio
from Backend.STT import FastNaturalSpeechRecognition
from Backend.TTS import OrionTTS
from Brain.model import model
from Brain.ChatBot import Chatbot  # Handles queries, speech & logging
from Backend.RealtimeData import RealTimeInformation
import nest_asyncio
nest_asyncio.apply()


class OrionCore:
    def __init__(self):
        self.recognizer = FastNaturalSpeechRecognition()
        self.tts = OrionTTS(engine="pyttsx3")  # You can switch to 'gtts' or 'edge'
        self.exit_requested = False

    async def process_input(self, user_input):
        try:
            try:
                for Model, query in responses:
                    if Model.upper() in ["WEATHER", "TIME", "LOCATION", "SEARCH"]:
                        result = await RealTimeInformation().get(module=Model.upper(), query=query)
                        web_responses += result if result else ""
                    elif Model == "CHATBOT":
                        Query = f"This realtime information from web and other ways of getting information is not always accurate, so please verify it with other sources if you can. Here are the results: \n\n{web_responses}\n\n --- \n\n This is users query: {query}\n\n --- \n\n Now, please respond to the user with the best possible answer based on the information you have and the query provided. If you don't know the answer, just say 'I don't know'."
                        chatbot = Chatbot()
                        reply = await chatbot.process_query(Query)
                        print(f"Chatbot reply: {reply}")
                        # The TTS is already handled in the chatbot.process_query method
                    elif Model == "Exit":
                        print("🛑 Exit signal from model.")
                        self.exit_requested = True
                    else:
                        print(f"🔎 Unknown intent: {Model} -> {query}")
            except Exception as e:
                error_msg = f"❌ Error processing model response: {str(e)}"
                print(error_msg)
                await self.tts.speak("Sorry, I had trouble understanding how to respond to that.")

        except Exception as e:
            error_msg = f"❌ Error while processing input: {str(e)}"
            print(error_msg)
            await self.tts.speak("Sorry, something went wrong with your request.")

    async def run(self):
        while not self.exit_requested:
            try:
                user_input = await self.recognizer.recognize_from_microphone()
                print(f"🗣️ You said: {user_input}")

                if user_input.lower() in ["exit", "quit", "stop", "shut down", "shutdown"]:
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
    loop = asyncio.get_event_loop()

    # Create and run the main Orion task
    main_task = loop.create_task(main())

    try:
        loop.run_until_complete(main_task)
    except KeyboardInterrupt:
        print("👋 Orion terminated by keyboard interrupt.")
