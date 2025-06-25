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

if __name__ == "__main__":
    asyncio.run(test_model())