from dotenv import load_dotenv
import os
import asyncio
import time
import json
from groq import Groq
from Backend import TTS
from Backend.RealtimeData import RealTimeInformation

# Load environment variables from .env
load_dotenv(dotenv_path='../.env')

class Chatbot:
    def __init__(self):
        # 1) Load Groq API key
        self.groq_api = os.getenv('GroqAPI')
        if not self.groq_api:
            raise ValueError("❌ GroqAPI environment variable is not set in .env file.")

        # 2) Initialize client & TTS
        self.client = Groq(api_key=self.groq_api)
        self.tts    = TTS.OrionTTS(engine="pyttsx3")  # You can switch to 'gtts' or 'edge'
        self.realtime_info = RealTimeInformation()

        # 3) Path to your existing JSON (with manual system prompt already inside)
        self.db_file = os.path.join('Brain', 'Data', 'ChatHistory.json')
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        if not os.path.exists(self.db_file):
            # If file doesn't exist, create it as empty array.
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)

    async def handle_query(self, query, contexts:list = ["General"]):
        if not query:
            print("❌ Empty query received. Please provide a valid input.")
            return "❌ Empty query received. Please provide a valid input."
        print(f"🗣️ User: {query}")
        response = ""
        for context in contexts:
            if context.lower() == "weather":
                response += "\n" + await self.realtime_info.get_detailed_weather()
            elif context.lower() == "time":
                response += "\n" + await self.realtime_info.get_time_info()
            elif context.lower() == "location":
                response += "\n" + await self.realtime_info.get_location_info()
            elif context.lower() == "search":
                # Search context is handled separately by the Search function
                pass
            elif context.lower() == "general":
                pass  # General context, no action needed

        if response:
            query = f"""This realtime information from web and other ways of getting information is not always accurate, so please verify it with other sources if you can. Here are the results: 
---
{response}
--- 
This is users query: {query}
---
Now, please respond to the user with the best possible answer based on the information you have and the query provided. If you don't know the answer, just say 'I don't know'."""

        reply = await self.process_query(query)
        return reply

    @staticmethod
    def load_chat_history_trimmed(filepath, user_query, max_history=6):
        with open(filepath, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        with open(os.path.join('Brain', 'Data', 'orionconfig.json'), 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 🔹 Separate the system prompt from the rest
        system_prompt = [msg for msg in history if msg["role"] == "system"]
        system_prompt[0]['content'].replace("{user}", config['user'])
        conversation = [msg for msg in history if msg["role"] != "system"]

        # 🔹 Trim conversation to the last N entries (user + assistant messages)
        trimmed = conversation[-max_history:]

        # 🔹 Append current user query
        trimmed.append({"role": "user", "content": user_query})

        # 🔹 Combine: system prompt + trimmed history + new query
        return system_prompt + trimmed

    async def process_query(self, query):
        try:
            start = time.time()

            # Load the entire history (including your manual system prompt)
            with open(self.db_file, 'r', encoding='utf-8') as f:
                history = json.load(f)

            # Build messages: history + current user message
            messages = self.load_chat_history_trimmed(self.db_file, query)

            # Ask the model
            resp = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                temperature=0.84,
                top_p=1,
                stream=False,
            )
            reply = resp.choices[0].message.content.strip()

            elapsed = time.time() - start
            print(f"⏱️ Processed in {elapsed:.2f}s")
            print(f"🤖 Orion: {reply}")
            await self.tts.speak(reply)

            # Append both user + assistant in one shot
            self._log_to_json("user", query, "assistant", reply)
            
            return reply

        except Exception as e:
            err = f"❌ Error while processing query: {e}"
            print(err)
            await self.tts.speak("Oops, something went wrong.")
            # Log the error as assistant response
            self._log_to_json("user", query, "assistant", err)
            
            return err

    def _log_to_json(self, role, content, assistant_role=None, assistant_content=None):
        try:
            with open(self.db_file, 'r+', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []

                # 🔹 Remove system messages from re-logging
                if role == "system":
                    return

                # 🔹 Append current messages
                entries = [{"role": role, "content": content}]
                if assistant_role and assistant_content:
                    entries.append({"role": assistant_role, "content": assistant_content})

                # 🔹 Avoid re-adding system messages
                data += entries

                f.seek(0)
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.truncate()

        except Exception as e:
            print(f"❌ Failed to log chat: {e}")

# # 🔧 Example usage:
# if __name__ == "__main__":
#     bot = Chatbot()
#     bot.handle_query("Who am I. Who is your boss and what is photosynthesis?")
