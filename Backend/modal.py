from dotenv import load_dotenv
import os
from groq import Groq
import asyncio  # Add asyncio for asynchronous programming

# Load environment variables from the .env file
load_dotenv(dotenv_path='../.env')

# Get the GroqAPI value
groq_api = os.getenv('GroqAPI')
if not groq_api:
    raise ValueError("GroqAPI environment variable is not set. Please check your .env file.")

# Initialize the Groq client
client = Groq(api_key=groq_api)

# Define the system message template
SYSTEM_MESSAGE_TEMPLATE = """You are the routing engine for ORION.
Your job is to:
1. Decide which MODULE should handle the input.
2. Strip away polite or filler phrases like “please,” “can you,” “I want to,” “could you,” etc.
3. Return the output strictly in this format:
['<MODULE_NAME>', '<Cleaned Core User Query>']
---
MODULES:
- CHATBOT — General questions, chatting, jokes.
- WEATHER_API — Weather info, forecasts, temperature.
- SYSTEM_COMMANDS — App or file operations, reminders, playback.
- AI_ASSISTANT — Help with studies, deep answers, advice.
- WEB_SEARCH — Real-time or unknown topics, news, trends.
- CUSTOM_SKILL_MUSIC — Music control.
- CUSTOM_SKILL_HOME — Smart home functions.
- CUSTOM_SKILL_STUDY — Study tools, Notion, Anki, etc.
---
Examples:
User: "Can you tell me the capital of Turkey?"  
→ ['CHATBOT', 'What is the capital of Turkey?']

User: "Please check weather in Lahore."  
→ ['WEATHER_API', 'Weather in Lahore']

User: "Could you search who is president of Pakistan?"  
→ ['WEB_SEARCH', 'Who is the president of Pakistan']

User: "I want to play study music"  
→ ['CUSTOM_SKILL_MUSIC', 'Play study music']

User: "Can you open VS Code?"  
→ ['SYSTEM_COMMANDS', 'Open VS Code']
---
Now respond in that exact format:
{user_input}"""

async def modal(user_input: str):
    """
    Asynchronous function to process user input and return the module and cleaned query.
    """
        # Wrap the synchronous call in asyncio.to_thread
    chat_completion = await asyncio.to_thread(
        client.chat.completions.create,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_MESSAGE_TEMPLATE.format(user_input=user_input),
            }
        ],
        model="gemma2-9b-it",
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    response = chat_completion.choices[0].message.content

    return response