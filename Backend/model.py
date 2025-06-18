from dotenv import load_dotenv
import os
from groq import Groq
import asyncio  # Add asyncio for asynchronous programming
import time
from ast import literal_eval

# Load environment variables from the .env file
load_dotenv(dotenv_path='../.env')

# Get the GroqAPI value
groq_api = os.getenv('GroqAPI')
if not groq_api:
    raise ValueError("GroqAPI environment variable is not set. Please check your .env file.")

# Initialize the Groq client
client = Groq(api_key=groq_api)

# Define the system message template
SYSTEM_MESSAGE_TEMPLATE = """You are the intelligent routing brain of ORION.

Your job is to:
1. Understand the user's full intent.
2. Break it into separate actionable commands for the correct MODULES.
3. Always include the FULL ORIGINAL user message in a 'CHATBOT' entry (unless the input is extremely short or filler-only).
4. Remove all filler/polite words like: "please", "can you", "would you", "I want to", "yo", "orion", "hmm", "uh", "tell me", "kindly", etc.
5. Simplify any overly formal or complex language to short, clean, modern phrasing.
6. Route the **cleaned query** to relevant modules. Use CHATBOT only once at the top — do NOT duplicate.

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
- Include the original user input under `CHATBOT` as the **first entry**, unless it’s very short (like "Open Notion")

---

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
- If it includes a user’s identity (e.g., "what’s my name?") → route to `CHATBOT`
- Unknowns or casual small phrases like "hmm", "okay", "oh wow" → route only to `CHATBOT`

---

📚 MODULES:

- CHATBOT — General chatting, greetings, emotions, identity, unknowns
- WEATHER_API — Weather queries (today, tomorrow, cities)
- SYSTEM_COMMANDS — App/file/system-level (e.g., open, close, shut down, reminders)
- AI_ASSISTANT — Studies, learning help, advice, topic explanations
- WEB_SEARCH — Real-time info, people, events, facts
- CUSTOM_SKILL_MUSIC — Music playback/control (e.g., play lofi, pause music)
- CUSTOM_SKILL_HOME — Smart home (e.g., lights, AC, fan)
- CUSTOM_SKILL_STUDY — Notes, Notion, Anki, study tasks
- Exit — When user wants to exit Orion

---

🧪 EXAMPLES:

**User**: "Hey Orion, open YouTube and tell me a joke"
→ [
    ['CHATBOT', 'Hey Orion, open YouTube and tell me a joke'],
    ['SYSTEM_COMMANDS', 'Open YouTube']
]

**User**: "Turn on the lights and play music"
→ [
    ['CHATBOT', 'Turn on the lights and play music'],
    ['CUSTOM_SKILL_HOME', 'Turn on lights'],
    ['CUSTOM_SKILL_MUSIC', 'Play music']
]

**User**: "Remind me to study at 5pm and help me understand Newton's laws"
→ [
    ['CHATBOT', "Remind me to study at 5pm and help me understand Newton's laws"],
    ['SYSTEM_COMMANDS', 'Set reminder to study at 5pm'],
    ['AI_ASSISTANT', "Explain Newton's laws"]
]

**User**: "What's the weather in Karachi and open Notion"
→ [
    ['CHATBOT', "What's the weather in Karachi and open Notion"],
    ['WEATHER_API', 'Weather in Karachi'],
    ['SYSTEM_COMMANDS', 'Open Notion']
]

**User**: "Google search moon landing and who is Elon Musk?"
→ [
    ['CHATBOT', 'Google search moon landing and who is Elon Musk?'],
    ['WEB_SEARCH', 'Moon landing'],
    ['WEB_SEARCH', 'Elon Musk']
]

**User**: "Exit Orion"
→ [
    ['CHATBOT', 'Exit Orion'],
    ['Exit', 'Exit']
]

**User**: "Please..."
→ [
    ['CHATBOT', 'Please...']
]

**User**: "Hmm"
→ [
    ['CHATBOT', 'Hmm']
]

---

🎯 GOAL:

Route every input to the exact set of modules without duplication, follow structure rules, preserve context, and NEVER break syntax.

Now respond in that format for this user input:
{user_input}
"""

def safe_parse_routing(raw_output: str):

    try:
        # Ensure full outer brackets if missing
        fixed_output = raw_output.strip()
        if not fixed_output.startswith('['):
            fixed_output = f'[{fixed_output}]'

        parsed = literal_eval(fixed_output)

        if not isinstance(parsed, list) or not all(
            isinstance(i, list) and len(i) == 2 and all(isinstance(x, str) for x in i)
            for i in parsed
        ):
            raise ValueError("Invalid format")
        return parsed

    except Exception as e:
        print("❌ Parsing Failed:", e)
        return [['CHATBOT', 'Sorry, I couldn\'t understand that.']]


async def model(user_input: str):
    """
    Asynchronous function to process user input and return the module and cleaned query.
    """
    start_time = time.time()  # Start timing the function execution
    try:
        # Wrap the synchronous call in asyncio.to_thread
        chat_completion = await asyncio.to_thread(
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
        response = chat_completion.choices[0].message.content.strip()
    except Exception as e:
        response = f"Error: {str(e)}"  # Handle errors gracefully

    end_time = time.time()  # End timing the function execution
    print(f"Function execution time: {end_time - start_time:.2f} seconds")  # Print the execution time

    try:
        parsed = safe_parse_routing(response)
        if not isinstance(parsed, list) or not all(isinstance(i, list) and len(i) == 2 for i in parsed):
            raise ValueError("Returned value is not a list of ['MODULE', 'QUERY'] pairs.")
        return parsed  # A list of module/query pairs
    except Exception as e:
        raise ValueError(f"Invalid response format: {response}\nError: {e}")