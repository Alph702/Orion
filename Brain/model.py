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

- CHATBOT — General chatting, greetings, emotions, identity, unknowns
- WEATHER_API — Weather queries (today, tomorrow, cities)
- SYSTEM_COMMANDS — App/file/system-level (e.g., open, close, shut down, reminders)
- WEB_SEARCH — Real-time info, people, events, facts
- CUSTOM_SKILL_MUSIC — Music playback/control (e.g., play lofi, pause music)
- CUSTOM_SKILL_HOME — Smart home (e.g., lights, AC, fan)
- CUSTOM_SKILL_STUDY — Notes, Notion, Anki, study tasks
- Exit — When user wants to exit Orion

---

### 🔹 💬 1. Mixed commands with filler words

User: "Hey Orion, can you please open YouTube, what's the weather like today, and tell me a joke?"

[
    ['CHATBOT', "Hey Orion, can you please open YouTube, what's the weather like today, and tell me a joke?"],
    ['SYSTEM_COMMANDS', 'Open YouTube'],
    ['WEATHER_API', 'Weather today']
]

User: 🤷 Sorry, I didn't catch that.

[
    ['CHATBOT', "Sorry, I didn't catch that."]
]

---

### 🔹 🎓 2. Study-related and search

User: "Can you help me revise cell structure and search for biology news?"

[
    ['CHATBOT', 'Can you help me revise cell structure and search for biology news?'],
    ['CUSTOM_SKILL_STUDY', 'Revise cell structure'],
    ['WEB_SEARCH', 'Biology news']
]

---

### 🔹 📱 3. App control with polite-only input

User: "Hey Orion, open VS Code and close Spotify."

[
    ['CHATBOT', 'Hey Orion, open VS Code and close Spotify.'],
    ['SYSTEM_COMMANDS', 'Open VS Code'],
    ['SYSTEM_COMMANDS', 'Close Spotify']
]

---

### 🔹 🌤️ 4. Weather + unknown

User: "What's the weather tomorrow in Karachi and who is the prime minister of Norway?"

[
    ['CHATBOT', "What's the weather tomorrow in Karachi and who is the prime minister of Norway?"],
    ['WEATHER_API', 'Weather in Karachi tomorrow'],
    ['WEB_SEARCH', 'Prime minister of Norway']
]

---

### 🔹 🧠 5. AI help + reminder

User: "Could you kindly explain photosynthesis and remind me to study at 5pm"

[
    ['CHATBOT', 'Could you kindly explain photosynthesis and remind me to study at 5pm'],
    ['SYSTEM_COMMANDS', 'Set reminder to study at 5pm']
]

---

### 🔹 🗣️ 6. Only filler words

User: "Please..."

[
    ['CHATBOT', 'Please...']
]

---

### 🔹 🌀 7. Unknown small talk

User: "Hmm..."

[
    ['CHATBOT', 'Hmm...']
]

---

### 🔹 📚 8. Deep query + educational

User: "Why is the sky blue and what is the meaning of life?"

[
    ['CHATBOT', 'Why is the sky blue and what is the meaning of life?']
]

---

### 🔹 🏠 9. Smart home + music

User: "Turn on bedroom lights and play lofi beats"

[
    ['CHATBOT', 'Turn on bedroom lights and play lofi beats'],
    ['CUSTOM_SKILL_HOME', 'Turn on bedroom lights'],
    ['CUSTOM_SKILL_MUSIC', 'Play lofi beats']
]

---

### 🔹 ❌ 10. Exit command

User: "Okay Orion, I'm done. Exit please."

[
    ['CHATBOT', 'Okay Orion, I'm done. Exit please.'],
    ['Exit', 'Exit']
]

User: "ok bye I am going to eat some dinner now."

[
    ['CHATBOT', 'Ok bye I am going to eat some dinner now.'],
    ['Exit', 'Exit']
]

User: "shutdown"

[
    ['CHATBOT', 'shutdown'],
    ['Exit', 'Exit']
]
etc.
---

### 🔹 🔍 11. Messy real-world query

User: "Orion, tell me the weather, open my browser, and what's Elon Musk up to?"

[
    ['CHATBOT', "Orion, tell me the weather, open my browser, and what's Elon Musk up to?"],
    ['WEATHER_API', 'Weather'],
    ['SYSTEM_COMMANDS', 'Open browser'],
    ['WEB_SEARCH', 'Elon Musk news']
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
