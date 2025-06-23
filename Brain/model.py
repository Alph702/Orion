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

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "Chatbot",
                    "description": "Handles general user queries that don't require real-time information. "
                                   "This function is best suited for conversational queries, FAQs, or general knowledge. "
                                   "It does not handle queries requiring real-time updates, such as news, weather, or current events.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "User query for the chatbot."}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_time",
                    "description": "Get the current local time.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "User query related to time."}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get detailed weather information for the user's location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "User query related to weather."}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_location_info",
                    "description": "Get detailed location information.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "User query related to location."}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "perform_search",
                    "description": "Perform a web search based on the user's query.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query."},
                            "max_results": {"type": "integer", "description": "Maximum number of search results to return."}
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

        self.function_map = {
            "Chatbot": self.Chatbot.handle_query,
            "get_time": self.realtime_info.get_time_info,
            "get_weather": self.realtime_info.get_detailed_weather,
            "get_location_info": self.realtime_info.get_location_info,
            "perform_search": self.realtime_info.perform_search,
        }

    async def handle(self, user_input: str) -> str:
        response = self.client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": user_input}],
            tools=self.tools,
            tool_choice="auto"
        )

        choice = response.choices[0]
        if choice.finish_reason == "tool_calls":
            results = []

            for tool_call in choice.message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                func = self.function_map.get(func_name)
                if func:
                    if asyncio.iscoroutinefunction(func):
                        result = await func(**args)
                    else:
                        result = func(**args)
                else:
                    result = f"⚠️ Function '{func_name}' not implemented."

                results.append(f"🔧 {func_name} → {result}")

            return "\n\n".join(results)

        return choice.message.content

# Run test
async def test():
    model = OrionModel()
    result = await model.handle("So what are you how are you orion and what about the Iran and Israel conflict and is there any issues for Trump in that conflict")
# Only run if executed directly
if __name__ == "__main__":
    asyncio.run(test())
