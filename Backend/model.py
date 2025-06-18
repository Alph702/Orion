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
2. Break it into separate actionable commands for the right MODULES.
3. Remove all polite filler words such as: "please", "could you", "would you", "can you", "I want to", "yo", "hey", "orion", "hmm", "uh", "tell me", "kindly", etc.
4. If the message ONLY includes such filler phrases (e.g. "please", "yo", "orion?"), then route it to CHATBOT with the phrase untouched.
5. Simplify any overly formal, complex, or awkward queries into short, modern, and natural-sounding versions while keeping the original meaning.
6. Route the full original query to the CHATBOT (as the first entry) so it can provide context-aware responses.

Your response must always:
✅ Be in the exact format of a valid Python list of lists:
[
    ['MODULE', 'Cleaned Query'],
    ['MODULE', 'Another Cleaned Query']
]
✅ Use only single quotes (')
✅ Be on a single line (no line breaks)
✅ Be valid Python syntax that can be parsed with `ast.literal_eval()`
✅ Include the full original user message in a CHATBOT entry as the first item (unless the user says something very short like "Open Notion", in which case CHATBOT is optional)

Do NOT:
❌ Use JSON formatting
❌ Use double quotes
❌ Add any explanation, commentary, or metadata
❌ Break into multiple lines or use backticks, code blocks, or fancy quotes

---

MODULES:

- CHATBOT — For general chatting, greetings, emotions, context-awareness.
- WEATHER_API — Weather-related queries (e.g. current weather, forecasts).
- SYSTEM_COMMANDS — App/file/system commands (e.g. open, close, shut down, reminders).
- AI_ASSISTANT — Help with studies, advice, reasoning, explanation of hard topics.
- WEB_SEARCH — Real-time information, news, unknowns.
- CUSTOM_SKILL_MUSIC — Music playback, control.
- CUSTOM_SKILL_HOME — Smart home (e.g. turn on light, fan, AC).
- CUSTOM_SKILL_STUDY — Notes, flashcards, Notion, Anki, study-related functions.

---

EXAMPLES:

User: "Please tell me the capital of France."
→ [
    ['CHATBOT', 'Please tell me the capital of France.'],
    ['CHATBOT', 'What is the capital of France?']
]

User: "Open VS Code and search for the latest cricket score"
→ [
    ['CHATBOT', 'Open VS Code and search for the latest cricket score'],
    ['SYSTEM_COMMANDS', 'Open VS Code'],
    ['WEB_SEARCH', 'Latest cricket score']
]

User: "Hey Orion, can you please turn on the bedroom lights and play relaxing music?"
→ [
    ['CHATBOT', 'Hey Orion, can you please turn on the bedroom lights and play relaxing music?'],
    ['CUSTOM_SKILL_HOME', 'Turn on bedroom lights'],
    ['CUSTOM_SKILL_MUSIC', 'Play relaxing music']
]

User: "I'm heading to school, don't forget to write my notes and search for science news."
→ [
    ['CHATBOT', "I'm heading to school, don't forget to write my notes and search for science news."],
    ['CUSTOM_SKILL_STUDY', 'Write notes'],
    ['WEB_SEARCH', 'Science news']
]

User: "Could you kindly tell me the forecast in Karachi tomorrow?"
→ [
    ['CHATBOT', 'Could you kindly tell me the forecast in Karachi tomorrow?'],
    ['WEATHER_API', 'Forecast in Karachi tomorrow']
]

User: "Yo Orion?"
→ [
    ['CHATBOT', 'Yo?']
]

User: "Please..."
→ [
    ['CHATBOT', 'Please...']
]

User: "Turn on the AC and tell me a joke"
→ [
    ['CHATBOT', 'Turn on the AC and tell me a joke'],
    ['CUSTOM_SKILL_HOME', 'Turn on the AC'],
    ['CHATBOT', 'Tell me a joke']
]

User: "Who is the current president of Pakistan and what’s the temperature in Islamabad?"
→ [
    ['CHATBOT', "Who is the current president of Pakistan and what’s the temperature in Islamabad?"],
    ['WEB_SEARCH', 'Who is the current president of Pakistan'],
    ['WEATHER_API', 'Temperature in Islamabad']
]

User: "Hmm..."
→ [
    ['CHATBOT', 'Hmm...']
]

User: "Open Notion"
→ [
    ['SYSTEM_COMMANDS', 'Open Notion']
]

User: "Exit Orion" or "Quit"
→ [
    ['Exit', 'Exit']
]

---

Be precise, consistent, and don't ever skip wrapping in valid Python list of lists.
Now respond in that format for this user input:
{user_input}
"""

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
        parsed = literal_eval(response)
        if not isinstance(parsed, list) or not all(isinstance(i, list) and len(i) == 2 for i in parsed):
            raise ValueError("Returned value is not a list of ['MODULE', 'QUERY'] pairs.")
        return parsed  # A list of module/query pairs
    except Exception as e:
        raise ValueError(f"Invalid response format: {response}\nError: {e}")