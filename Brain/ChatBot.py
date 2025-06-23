from dotenv import load_dotenv
import os
import asyncio
import time
import json
from groq import Groq
from Backend import TTS

# Load environment variables from .env
load_dotenv(dotenv_path='../.env')

class Chatbot:
    def __init__(self, query=None):
        # 1) Load Groq API key
        self.groq_api = os.getenv('GroqAPI')
        if not self.groq_api:
            raise ValueError("❌ GroqAPI environment variable is not set in .env file.")

        # 2) Initialize client & TTS
        self.client = Groq(api_key=self.groq_api)
        self.tts    = TTS.OrionTTS(engine="pyttsx3")  # You can switch to 'gtts' or 'edge'

        # 3) Path to your existing JSON (with manual system prompt already inside)
        self.db_file = os.path.join('Brain', 'Data', 'ChatHistory.json')
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        if not os.path.exists(self.db_file):
            # If file doesn't exist, create it as empty array.
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)

        # 4) Handle the query
        self.query = query


        print(f"🗣️ User: {self.query}")

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

    async def process_query(self):
        try:
            start = time.time()

            # Load the entire history (including your manual system prompt)
            with open(self.db_file, 'r', encoding='utf-8') as f:
                history = json.load(f)

            # Build messages: history + current user message
            messages = self.load_chat_history_trimmed(self.db_file, self.query)

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
            self._log_to_json("user", self.query, "assistant", reply)

        except Exception as e:
            err = f"❌ Error while processing query: {e}"
            print(err)
            await self.tts.speak("Oops, something went wrong.")
            # Log the error as assistant response
            self._log_to_json("user", self.query, "assistant", err)

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
#     Chatbot(query="Who am I. Who is your boss and what is photosynthesis?")
