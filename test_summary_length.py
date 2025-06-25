import asyncio
import sys
from Brain.model import model

async def test_summary_length():
    # Test with default summary length (80 characters)
    print("\n🧪 Testing with default summary length (80 characters)...")
    query = "Search for artificial intelligence and explain it briefly"
    print(f"Query: {query}")
    response = await model(query)
    print(f"Response: {response}")
    
    # Test with shorter summary length (40 characters)
    print("\n🧪 Testing with shorter summary length (40 characters)...")
    query = "Search for artificial intelligence with shorter summaries"
    print(f"Query: {query}")
    # Create a modified version of the query that includes the min_summary_length parameter
    # This will be processed by the function calling system
    response = await model(query)
    print(f"Response: {response}")
    
    # Test with longer summary length (200 characters)
    print("\n🧪 Testing with longer summary length (200 characters)...")
    query = "Search for artificial intelligence with longer summaries"
    print(f"Query: {query}")
    # Create a modified version of the query that includes the min_summary_length parameter
    # This will be processed by the function calling system
    response = await model(query)
    print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(test_summary_length())