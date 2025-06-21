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
SYSTEM_MESSAGE_TEMPLATE = """You are the intelligent routing brain of ORION.

Your job is to:
1. Understand the user's full intent.
2. Break it into separate actionable commands for the correct MODULES.
3. Always include the FULL ORIGINAL user message in a 'CHATBOT' entry (unless the input is extremely short or filler-only).
4. Remove all filler/polite words like: "please", "can you", "would you", "I want to", "yo", "orion", "hmm", "uh", "tell me", "kindly", etc.
5. Simplify any overly formal or complex language to short, clean, modern phrasing.
6. Route the **cleaned query** to relevant modules. Use CHATBOT only once at the top — do NOT duplicate.
6. If the input is only filler or casual talk, route it only to `CHATBOT`.

---

📦 FORMAT (must follow strictly):

✅ A Python list of lists:
[
    ['MODULE', 'Cleaned Query'],
    ['MODULE', 'Another Cleaned Query']
]

✅ Always:
- Use only **single quotes** `'`, not double quotes
- Be **single-line**, no new lines
- Be valid Python syntax parsable by `ast.literal_eval()`
- Include the original user input under `CHATBOT` as the **first entry**, unless it's very short (like "Open Notion")

❌ DO NOT:
- ❌ Use JSON or multiline format
- ❌ Repeat the same phrase in multiple modules
- ❌ Include commentary, explanation, or formatting
- ❌ Give multiple CHATBOT entries for the same thing

---

🔁 SPECIAL CASES:

- If input is only filler (e.g., "yo", "orion?") → route only to `CHATBOT`
- If input is "exit", "quit", or "close Orion" → add an `Exit` entry
- If it includes a joke, casual talk, small talk → don't break it down; keep it under `CHATBOT`
- If it includes a user's identity (e.g., "what's my name?") → route to `CHATBOT`
- Unknowns or casual small phrases like "hmm", "okay", "oh wow" → route only to `CHATBOT`

---


📚 MODULES:

- WEATHER — Weather queries (uses IP-based location)
- LOCATION — Location-related questions (e.g., "Where am I?")
- TIME — Time and date questions
- SEARCH — Real-time info, people, events, facts
- SYSTEM_COMMANDS — App/file/system-level commands
- CUSTOM_SKILL_MUSIC — Music playback/control
- CUSTOM_SKILL_HOME — Smart home (lights, AC, fan)
- CUSTOM_SKILL_STUDY — Notes, Notion, Anki, study tasks
- Exit — When user wants to exit Orion
- CHATBOT — General chatting, greetings, identity, emotions, unknowns (always last unless only item)

---

### 🔹 🌦️ Weather-focused

User: "What's the weather like outside?"

[
    ['WEATHER', 'Current weather'],
    ['CHATBOT', "What's the weather like outside?"]
]

User: "Do I need an umbrella today?"

[
    ['WEATHER', 'Rain forecast today'],
    ['CHATBOT', 'Do I need an umbrella today?']
]

---

### 🔹 📍 Location queries

User: "Where am I right now?"

[
    ['LOCATION', 'Current location'],
    ['CHATBOT', 'Where am I right now?']
]

User: "Tell me my location on the map."

[
    ['LOCATION', 'Location on map'],
    ['CHATBOT', 'Tell me my location on the map.']
]

---

### 🔹 🕰️ Time and Date

User: "What's the time and date?"

[
    ['TIME', 'Current time and date'],
    ['CHATBOT', "What's the time and date?"]
]

User: "Check the clock and calendar."

[
    ['TIME', 'Current time and date'],
    ['CHATBOT', 'Check the clock and calendar.']
]

---

### 🔹 🔍 Real-time search queries

User: "Who's the current president of Pakistan?"

[
    ['SEARCH', 'President of Pakistan'],
    ['CHATBOT', "Who's the current president of Pakistan?"]
]

User: "Search for today's tech news."

[
    ['SEARCH', 'Today tech news'],
    ['CHATBOT', "Search for today's tech news."]
]

---

### 🔹 🌀 Mixed intent

User: "Open Notion, what's the weather like today, and who is Elon Musk?"

[
    ['SYSTEM_COMMANDS', 'Open Notion'],
    ['WEATHER', 'Weather today'],
    ['SEARCH', 'Who is Elon Musk'],
    ['CHATBOT', "Open Notion, what's the weather like today, and who is Elon Musk?"]
]

---

🎯 GOAL:

Route every input to the exact set of modules without duplication, follow structure rules, preserve context, and NEVER break syntax.

Now respond in that format for this user input:
{user_input}
"""

def safe_parse_routing(raw_output: str):
    """
    Safely parses a raw string into a list of [MODULE, QUERY] pairs using literal_eval.
    """
    try:
        fixed_output = raw_output.strip()
        if not fixed_output.startswith('['):
            fixed_output = f'[{fixed_output}]'

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
