import asyncio
import sys
from Brain.model import model

async def test_search_chatbot():
    # Test search with chatbot processing
    print("\n🧪 Testing search with chatbot processing...")
    query = "Tell me about the latest developments in quantum computing"
    print(f"Query: {query}")
    response = await model(query)
    print(f"Response: {response}")
    
    # Test explicit search with chatbot explanation
    print("\n🧪 Testing explicit search with chatbot explanation...")
    query = "Search for climate change solutions and explain them to me"
    print(f"Query: {query}")
    response = await model(query)
    print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(test_search_chatbot())