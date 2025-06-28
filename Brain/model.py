from dotenv import load_dotenv
import os
import time
from groq import Groq
import json
import asyncio

from Brain.ChatBot import Chatbot
from Backend.RealtimeData import RealTimeInformation
# from Backend.STT import FastNaturalSpeechRecognition

# Load .env
load_dotenv(dotenv_path='../.env')
groq_api = os.getenv('GroqAPI')
if not groq_api:
    raise ValueError("❌ GroqAPI not found in environment.")

class OrionModel:
    def __init__(self, stop_function:function):
        self.client = Groq(api_key=groq_api)
        self.realtime_info = RealTimeInformation()
        self.Chatbot = Chatbot()
        self.stop_function = stop_function

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
                        },
                        {
                            "type": "function",
                            "function": {
                                "name": "Search",
                                "description": (
                                    "This function is responsible for performing web searches based on user queries. "
                                    "Use it when the user explicitly asks to search for information on the web, "
                                    "or when the query requires up-to-date information that might not be in your training data. "
                                    "Examples include: 'search for latest news', 'look up information about a recent event', "
                                    "or 'find details about a specific topic'."
                                ),
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "description": "The search query to be executed"
                                        },
                                        "max_results": {
                                            "type": "integer",
                                            "description": "Maximum number of search results to return (default: 3)",
                                            "default": 3
                                        },
                                        "min_summary_length": {
                                            "type": "integer",
                                            "description": "Minimum length of text to extract from each search result (default: 80, min: 30, max: 500)",
                                            "default": 80
                                        }
                                    },
                                    "required": ["query"]
                                }
                            }
                        },
                        {
                            "type": "function",
                            "function": {
                                "name": "Stop",
                                "description": (
                                    "This function is used to stop the assistant from listening or processing further requests. "
                                    "It can be called when the user explicitly asks to stop the assistant, or when the assistant needs to pause its operations. "
                                    "Example usage: 'stop listening', 'pause orion', 'exit', 'quit orion', 'stop orion', 'exit orion' and 'mute orion', 'mute', 'bye Orion'"
                                ),
                                "parameters": {}
                            }
                        }
                    ]
        # Map function name to actual callable
        # Ensure Stop is always an async function
        async def async_stop_wrapper():
            result = self.stop_function()
            if asyncio.iscoroutine(result):
                return await result
            return result

        self.function_map = {
            "Chatbot": self.Chatbot.handle_query,
            "Search": self.realtime_info.perform_search,
            "Stop": async_stop_wrapper
        }

    async def handle(self, user_input: str) -> str:
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are Orion, a function-calling assistant. "
                        "You must always respond using either the 'Chatbot' or 'Search' function tools, or both when appropriate. "
                        "Do NOT answer directly. Your job is only to select the function and arguments. "
                        "For general queries or queries about weather, time, location, use the 'Chatbot' function with appropriate contexts. "
                        "Valid contexts for Chatbot: 'weather', 'time', 'location', 'search', 'general'. "
                        "For explicit web search requests, use the 'Search' function. "
                        "When a query requires both search and conversation, use BOTH functions - the Search results will be automatically fed into the Chatbot for a comprehensive response. "
                        "For example, if the user asks 'Tell me about the latest AI news', call both Search (for 'latest AI news') and Chatbot (to process and explain the results)."
                    )
                },
                {
                    "role": "user",
                    "content": "How are you Orion and what is the weather and time and search for latest news today"
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
                            }
                        },
                        {
                            "id": "tool2",
                            "type": "function",
                            "function": {
                                "name": "Search",
                                "arguments": json.dumps({
                                    "query": "latest news today",
                                    "max_results": 3
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
                results = []
                search_results = ""
                
                # First pass: Process all Search function calls
                for tool_call in message.tool_calls:
                    try:
                        function_name = tool_call.function.name
                        if function_name == "Search":
                            print(f"🔍 Processing Search tool call")
                            try:
                                args = json.loads(tool_call.function.arguments)
                                print(f"🧠 Calling Search with: {args}")
                                
                                # Extract min_summary_length from query if explicitly mentioned
                                query = args.get('query', '')
                                if 'min_summary_length=' in query:
                                    try:
                                        # Extract the value after min_summary_length=
                                        min_length_str = query.split('min_summary_length=')[1].split()[0]
                                        # Remove any non-numeric characters
                                        min_length_str = ''.join(c for c in min_length_str if c.isdigit())
                                        if min_length_str:
                                            args['min_summary_length'] = int(min_length_str)
                                            # Remove the parameter from the query
                                            args['query'] = query.replace(f'min_summary_length={min_length_str}', '').strip()
                                            print(f"📏 Extracted min_summary_length={args['min_summary_length']} from query")
                                    except Exception as e:
                                        print(f"⚠️ Failed to extract min_summary_length: {str(e)}")
                                
                                # Ensure min_summary_length is passed if not provided
                                if 'min_summary_length' not in args:
                                    args['min_summary_length'] = 80  # Default value
                                    
                                search_result = await self.realtime_info.perform_search(**args)
                                if search_result:
                                    # Format search results for better readability
                                    formatted_result = f"\n\n=== SEARCH RESULTS FOR '{args.get('query', 'unknown query')}' ===\n{search_result}\n=== END OF SEARCH RESULTS ===\n"
                                    search_results += formatted_result
                                    print(f"✅ Search returned results")
                            except Exception as e:
                                error_msg = f"❌ Error executing Search for '{args.get('query', 'unknown query')}': {str(e)}"
                                print(error_msg)
                                search_results += f"\n\n=== SEARCH ERROR ===\n{error_msg}\n=== END OF SEARCH ERROR ===\n"
                    except Exception as e:
                        error_msg = f"❌ Error processing Search tool call: {str(e)}"
                        print(error_msg)
                        search_results += f"\n\n=== SEARCH PROCESSING ERROR ===\n{error_msg}\n=== END OF SEARCH PROCESSING ERROR ===\n"
                
                # Second pass: Process all other function calls, with special handling for Chatbot
                for tool_call in message.tool_calls:
                    try:
                        function_name = tool_call.function.name
                        print(f"🔍 Processing tool call: {function_name}")
                        
                        # Skip Search calls as they were already processed
                        if function_name == "Search":
                            continue
                            
                        # Parse arguments with error handling
                        try:
                            args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError as e:
                            error_msg = f"❌ Invalid JSON in arguments for {function_name}: {str(e)}"
                            print(error_msg)
                            results.append(error_msg)
                            continue
                        
                        # Special handling for Chatbot to include search results
                        if function_name == "Chatbot":
                            print(f"🧠 Calling Chatbot with search results")
                            original_query = args.get("query", "")
                            
                            # If we have search results, include them in the Chatbot query
                            if search_results:
                                enhanced_query = f"""I've gathered some real-time information from the web to help answer this query. This information may not always be 100% accurate, so please verify with other sources when possible.

{search_results}

ORIGINAL USER QUERY: "{original_query}"

INSTRUCTIONS:
1. Analyze the search results thoroughly
2. Provide a comprehensive, short, and well-structured response addressing the user's query
3. Synthesize information from multiple sources when available
4. Highlight key points and important findings
5. Present a balanced view if there are conflicting perspectives
6. If the search results are insufficient or irrelevant, acknowledge this limitation
7. If you don't know the answer, simply state that you don't know
8. Format your response in a clear, readable manner."""
                                args["query"] = enhanced_query
                            
                            # Call Chatbot with enhanced query
                            try:
                                result = await self.Chatbot.handle_query(**args)
                                if result is not None:  # Only append non-None results
                                    print(f"✅ Chatbot returned result")
                                    results.append(result)
                                else:
                                    print(f"⚠️ Chatbot returned None")
                            except Exception as e:
                                error_msg = f"❌ Error executing Chatbot with query '{original_query[:30]}...': {str(e)}"
                                print(error_msg)
                                results.append(f"An error occurred while processing your request: {str(e)}. Please try again or rephrase your query.")
                        # Handle other functions normally
                        elif function_name in self.function_map:
                            print(f"🧠 Calling {function_name} with: {args}")
                            function_to_call = self.function_map[function_name]
                            
                            # Call function with error handling
                            try:
                                result = await function_to_call(**args)
                                if result is not None:  # Only append non-None results
                                    print(f"✅ {function_name} returned result of type: {type(result)}")
                                    results.append(result)
                                else:
                                    print(f"⚠️ {function_name} returned None")
                            except Exception as e:
                                error_msg = f"❌ Error executing {function_name}: {str(e)}"
                                print(error_msg)
                                results.append(error_msg)
                        else:
                            error_msg = f"❌ Unknown function: {function_name}"
                            print(error_msg)
                            results.append(error_msg)
                    except Exception as e:
                        error_msg = f"❌ Error processing tool call: {str(e)}"
                        print(error_msg)
                        results.append(error_msg)
                
                return "\n".join(results) if results else "❌ No results from function calls."

        except Exception as e:
            error_msg = f"🚨 Error in model.handle: {str(e)}"
            print(error_msg)
            return error_msg


# Create an instance of the model to be imported by other modules


# Function to be imported by other modules
async def model(user_input, stop_function:function):
    model_instance = OrionModel(stop_function=stop_function)
    return await model_instance.handle(user_input)

# Run test
async def test():
    # result = await model("How are you Orion and what is the weather and time? and news today")
    result = await model("bye Orion")
    print(result)
    
# Only run when this file is executed directly
if __name__ == "__main__":
    asyncio.run(test())
