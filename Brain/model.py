from dotenv import load_dotenv
import os
import time
from groq import Groq
import json
import asyncio

from Brain.ChatBot import Chatbot
from Backend.RealtimeData import RealTimeInformation

# Load .env
load_dotenv(dotenv_path='../.env')
groq_api = os.getenv('GroqAPI')
if not groq_api:
    raise ValueError("❌ GroqAPI not found in environment.")

class OrionModel:
    def __init__(self):
        self.client = Groq(api_key=groq_api)
        self.realtime_info = RealTimeInformation()
        self.Chatbot = Chatbot()

        # Tool definitions for Groq function calling
        self.tools = [
                        {
                            "type": "function",
                            "function": {
                                "name": "Chatbot",
                                "description": (
                                    "This function is responsible for answering any user query. "
                                    "Use it especially when the query involves real-time information, such as: "
                                    "'what is the time', 'tell me the weather', 'where am I', or 'search about Einstein'. "
                                    "Always call this function with the original user query, and add all relevant topics to the 'contexts' list. "
                                    "Valid contexts: 'weather', 'time', 'location', 'search', 'general'. "
                                    "If the query includes multiple topics, include all of them in 'contexts'."
                                ),
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "description": "The user's original query"
                                        },
                                        "contexts": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            },
                                            "description": (
                                                "The list of topics to answer from. Choose one or more from: 'weather', 'time', 'location', 'search', 'general'"
                                            )
                                        }
                                    },
                                    "required": ["query", "contexts"]
                                }
                            }
                        }
                    ]
        # Map function name to actual callable
        self.function_map = {
            "Chatbot": self.Chatbot.handle_query
        }

    async def handle(self, user_input: str) -> str:
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are Orion, a function-calling assistant. "
                        "You must always respond using the 'Chatbot' function tool. "
                        "Do NOT answer directly. Your job is only to select the function and arguments. "
                        "Valid contexts: 'weather', 'time', 'location', 'search', 'general'."
                    )
                },
                {
                    "role": "user",
                    "content": "How are you Orion and what is the weather and time and news today"
                },
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "tool1",
                            "type": "function",
                            "function": {
                                "name": "Chatbot",
                                "arguments": json.dumps({
                                    "query": "How are you Orion and what is the weather and time?",
                                    "contexts": ['general', 'weather', 'time']
                                })
                            },
                            "id": "tool2",
                            "type": "function",
                            "function": {
                                "name": "Chatbot",
                                "arguments": json.dumps({
                                    "query": "todays news",
                                    "contexts": ["search"]
                                })
                            }
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]

            response = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )

            if not response or not response.choices:
                return "❌ No response from model."

            choice = response.choices[0]
            message = choice.message

            # ✅ TOOL CALL PATH
            if choice.finish_reason == "tool_calls" and message and message.tool_calls:
                tool_call = message.tool_calls[0]
                args = json.loads(tool_call.function.arguments)

                print(f"🧠 Calling Chatbot with: {args}")
                result = await self.Chatbot.handle_query(**args)

        except Exception as e:
            return f"🚨 Error: {str(e)}"


# Run test
async def test():
    model = OrionModel()
    result = await model.handle("How are you Orion and what is the weather and time? and news today")
    print(result)
    
# Only run when this file is executed directly
if __name__ == "__main__":
    asyncio.run(test())
