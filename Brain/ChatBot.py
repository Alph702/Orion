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
        self.tts    = TTS.OrionTTS(engine="pyttsx3")

        # 3) Path to your existing JSON (with manual system prompt already inside)
        self.db_file = os.path.join('Brain', 'Data', 'ChatHistory.json')
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        if not os.path.exists(self.db_file):
            # If file doesn't exist, create it as empty array.
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)

        # 4) Handle the query
        self.query = query
        if not self.query:
            response = "Sorry... I didn't catch anything. Can you repeat that?"
            print(f"🤖 Orion: {response}")
            asyncio.run(self.tts.speak(response))
            # Log just this interaction
            self._log_to_json("user", "", "assistant", response)
            return

        print(f"🗣️ User: {self.query}")

    async def process_query(self):
        try:
            start = time.time()

            # Load the entire history (including your manual system prompt)
            with open(self.db_file, 'r', encoding='utf-8') as f:
                history = json.load(f)

            # Build messages: history + current user message
            messages = history + [{"role": "user", "content": self.query}]

            # Ask the model
            resp = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
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
        """Append user and assistant messages to the existing JSON file with UTF-8."""
        try:
            with open(self.db_file, 'r+', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []

                # Append user message
                data.append({"role": role, "content": content})

                # Append assistant message if provided
                if assistant_role and assistant_content is not None:
                    data.append({"role": assistant_role, "content": assistant_content})

                # Write back
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=4)
                f.truncate()

        except Exception as err:
            print(f"❌ Failed to log chat: {err}")

# # 🔧 Example usage:
# if __name__ == "__main__":
#     Chatbot(query="Who is your boss and what is photosynthesis?")
