import re
from dotenv import load_dotenv
import os
import asyncio
import time
from ast import literal_eval
from groq import Groq

# Load environment variables from the .env file
load_dotenv(dotenv_path='../.env')

# Retrieve the Groq API key
groq_api = os.getenv('GroqAPI')
if not groq_api:
    raise ValueError("❌ GroqAPI environment variable is not set. Please check your .env file.")

# Initialize the Groq client
client = Groq(api_key=groq_api)

# Template for routing input through ORION
SYSTEM_MESSAGE_TEMPLATE = """
You are the intelligent routing brain of ORION.

🎯 YOUR JOB:
You will process a user's spoken or typed input and output a valid routing structure using actionable module commands. You must:

1. Identify the user's true intent.
2. Convert the input into one or more precise, simplified queries.
3. Remove all filler/polite words: "please", "can you", "would you", "I want to", "yo", "orion", "hmm", "uh", "tell me", "kindly", "just", "like", etc.
4. Simplify formal or complex wording into short, direct phrases.
5. Assign each query to the correct MODULE.
6. Always include the original user input as the final `CHATBOT` entry, unless it is only casual/filler.
7. Avoid duplication of meaning across modules.

---

📦 STRICT FORMAT (MANDATORY):

✅ Must be a **single-line Python list of lists**, like:

[
    ['MODULE', 'Cleaned Query'],
    ['MODULE', 'Another Cleaned Query'],
    ['CHATBOT', 'Original user message']
]

✅ Always:
- Use **single quotes `'`** only (not double quotes).
- Return output in **one line only** (no line breaks).
- Be valid Python syntax that can be parsed by `ast.literal_eval()`.
- Place the `CHATBOT` entry **at the end**, unless it's the **only** module.
- Do **not repeat** the same query in multiple modules.

❌ Never:
- ❌ Use JSON format
- ❌ Use double quotes
- ❌ Add explanations, comments, markdown, or new lines
- ❌ Use multiline formatting or duplicate `CHATBOT` entries
- ❌ Mix CHATBOT anywhere except at the end (or alone)

---

📚 MODULES:

- `WEATHER` — Weather questions (e.g., rain, temperature)
- `LOCATION` — Location questions (e.g., "Where am I?")
- `TIME` — Time or date questions
- `SEARCH` — Real-world facts, people, events, info
- `SYSTEM_COMMANDS` — OS/app actions (e.g., open Notion)
- `CUSTOM_SKILL_MUSIC` — Music playback/control
- `CUSTOM_SKILL_HOME` — Smart home commands (lights, fan)
- `CUSTOM_SKILL_STUDY` — Study tools, Notion, Anki, tasks
- `Exit` — Shutdown commands like "exit", "quit"
- `CHATBOT` — Small talk, emotions, unknowns (always last unless only item)

---

⚠️ SPECIAL RULES:

- If the input is only filler (e.g., "yo", "orion?") → return only `[['CHATBOT', 'yo']]`
- If it's about exiting (e.g., "quit", "shutdown") → add `['Exit', 'Exit Orion']` and still include `CHATBOT` at the end
- If it's small talk, jokes, feelings → just use `CHATBOT`
- If unclear, always route to `CHATBOT` as fallback

---

💡 EXAMPLES (STRICTLY ONE-LINE):

User: "Can you open Notion, and what's the weather like today?"  
[
    ['SYSTEM_COMMANDS', 'Open Notion'], ['WEATHER', 'Weather today'], ['CHATBOT', "Can you open Notion, and what's the weather like today?"]
]

User: "Where am I right now and who is the president of Pakistan?"  
[
    ['LOCATION', 'Current location'], ['SEARCH', 'President of Pakistan'], ['CHATBOT', 'Where am I right now and who is the president of Pakistan?']
]

User: "Play some music and turn on the light in my room."  
[
    ['CUSTOM_SKILL_MUSIC', 'Play music'], ['CUSTOM_SKILL_HOME', 'Turn on room light'], ['CHATBOT', 'Play some music and turn on the light in my room.']
]

User: "Please tell me the time and open my study notes."  
[
    ['TIME', 'Current time'], ['CUSTOM_SKILL_STUDY', 'Open study notes'], ['CHATBOT', 'Please tell me the time and open my study notes.']
]

User: "Yo Orion, what's going on?"  
[
    ['CHATBOT', "Yo Orion, what's going on?"]
]

User: "What's the date and is it going to rain today?"  
[
    ['TIME', 'Current date'], ['WEATHER', 'Rain forecast today'], ['CHATBOT', "What's the date and is it going to rain today?"]
]

User: "Tell me who is Elon Musk and open YouTube."  
[
    ['SEARCH', 'Who is Elon Musk'], ['SYSTEM_COMMANDS', 'Open YouTube'], ['CHATBOT', 'Tell me who is Elon Musk and open YouTube.']
]

User: "Close Orion."  
[
    ['Exit', 'Exit Orion'], ['CHATBOT', 'Close Orion.']
]

User: "Hmm okay"  
[
    ['CHATBOT', 'Hmm okay']
]

User: "Start my study session and play lofi music"  
[
    ['CUSTOM_SKILL_STUDY', 'Start study session'], ['CUSTOM_SKILL_MUSIC', 'Play lofi music'], ['CHATBOT', 'Start my study session and play lofi music']
]

User: "Search for Python decorators and show me today's temperature."  
[
    ['SEARCH', 'Python decorators'], ['WEATHER', 'Today temperature'], ['CHATBOT', 'Search for Python decorators and show me today's temperature.']
]

User: "What time is it and where am I?"  
[
    ['TIME', 'Current time'], ['LOCATION', 'Current location'], ['CHATBOT', 'What time is it and where am I?']
]

---

Now respond in that exact format (a **single Python-valid one-line list of lists**) for this user input:

{user_input}
"""

def safe_parse_routing(raw_output: str):
    try:
        fixed_output = raw_output.strip().replace("'", "'")

        if not fixed_output.startswith('['):
            fixed_output = f'[{fixed_output}]'

        print("🧾 Fixed Output:", fixed_output)
        parsed = literal_eval(fixed_output)

        if not isinstance(parsed, list) or not all(
            isinstance(pair, list) and len(pair) == 2 and all(isinstance(x, str) for x in pair)
            for pair in parsed
        ):
            raise ValueError("Invalid format")

        return parsed

    except Exception as e:
        print("❌ Parsing Failed:", e)
        return [['CHATBOT', "Sorry, I couldn't understand that."]]


async def model(user_input: str):
    """
    Asynchronously processes user input and returns a list of routing commands.
    """
    start_time = time.time()

    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_MESSAGE_TEMPLATE.replace("{user_input}", user_input),
                }
            ],
            model="gemma2-9b-it",
            temperature=1,
            top_p=1,
            stream=False,
            stop=None,
        )

        content = response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ Completion Failed:", e)
        return [['CHATBOT', "Sorry, something went wrong."]]

    end_time = time.time()
    print(f"⏱️ Function execution time: {end_time - start_time:.2f} seconds")

    # Safely parse the content and return result
    return safe_parse_routing(content)
