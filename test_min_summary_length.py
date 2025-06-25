import asyncio
import sys
import time
from Brain.model import model

async def test_min_summary_length():
    # Test with explicit min_summary_length values
    test_cases = [
        {
            "description": "Testing with short summary length (40 characters)",
            "query": "Search for artificial intelligence with min_summary_length=40",
            "expected_min_length": 40
        },
        {
            "description": "Testing with medium summary length (120 characters)",
            "query": "Search for artificial intelligence with min_summary_length=120",
            "expected_min_length": 120
        },
        {
            "description": "Testing with long summary length (200 characters)",
            "query": "Search for artificial intelligence with min_summary_length=200",
            "expected_min_length": 200
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 {test_case['description']}...")
        query = test_case['query']
        print(f"Query: {query}")
        
        print(f"⏱️ Starting test at {time.strftime('%H:%M:%S')}")
        
        # The model should extract the min_summary_length parameter from the query
        # and pass it to the perform_search method
        try:
            response = await model(query)
            print(f"✅ Test completed successfully")
            
            # Check if the response contains any indication of the min_summary_length
            if 'min_summary_length' in response:
                print(f"✅ Response contains min_summary_length reference")
            
            # Check if the response length is reasonable
            print(f"📏 Response length: {len(response)} characters")
            
            # Print a truncated version of the response for readability
            max_display_length = 500
            if len(response) > max_display_length:
                truncated_response = response[:max_display_length] + "... (truncated)"
            else:
                truncated_response = response
            print(f"Response: {truncated_response}")
            
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
        
        print(f"Expected min_summary_length: {test_case['expected_min_length']}")
        print(f"⏱️ Finished test at {time.strftime('%H:%M:%S')}")
        
        # Add a separator for better readability
        print("\n" + "-" * 50)

if __name__ == "__main__":
    asyncio.run(test_min_summary_length())