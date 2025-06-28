import asyncio
import sys
from Brain.model import model

async def test_model():
    # Test a simple query
    print("\n🧪 Testing simple query...")
    response = await model("How are you today?")
    print(f"Response: {response}")
    
    # Test a weather query
    print("\n🧪 Testing weather query...")
    response = await model("What's the weather like?")
    print(f"Response: {response}")
    
    # Test a search query
    print("\n🧪 Testing search query...")
    response = await model("Search for latest news about AI")
    print(f"Response: {response}")
    
    # Test a combined query
    print("\n🧪 Testing combined query...")
    response = await model("What time is it and search for Python programming tips")
    print(f"Response: {response}")
    
    # Test search with chatbot processing
    print("\n🧪 Testing search with chatbot processing...")
    response = await model("Tell me about the latest developments in quantum computing")
    print(f"Response: {response}")
    
    # Test explicit search with chatbot explanation
    print("\n🧪 Testing explicit search with chatbot explanation...")
    response = await model("Search for climate change solutions and explain them to me")
    print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(test_model())