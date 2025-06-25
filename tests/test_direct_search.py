import asyncio
import sys
import time
from Backend.RealtimeData import RealTimeInformation

async def test_direct_search():
    realtime_info = RealTimeInformation()
    
    # Test cases with different min_summary_length values
    test_cases = [
        {
            "description": "Testing with short summary length (40 characters)",
            "query": "python programming",
            "min_summary_length": 40
        },
        {
            "description": "Testing with long summary length (200 characters)",
            "query": "python programming",
            "min_summary_length": 200
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 {test_case['description']}...")
        query = test_case['query']
        min_summary_length = test_case['min_summary_length']
        print(f"Query: {query}")
        print(f"Min Summary Length: {min_summary_length}")
        
        # Call perform_search directly with the min_summary_length parameter
        try:
            result = await realtime_info.perform_search(query=query, min_summary_length=min_summary_length)
            print(f"✅ Search completed successfully")
            
            # Print a truncated version of the result for readability
            max_display_length = 500
            if len(result) > max_display_length:
                truncated_result = result[:max_display_length] + "... (truncated)"
            else:
                truncated_result = result
            print(f"Result: {truncated_result}")
            
            # Count the number of search results
            result_count = result.count("🔗")
            print(f"📊 Number of search results: {result_count}")
            
        except Exception as e:
            print(f"❌ Search failed with error: {str(e)}")
        
        # Add a separator for better readability
        print("\n" + "-" * 50)

if __name__ == "__main__":
    asyncio.run(test_direct_search())