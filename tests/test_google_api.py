"""
Quick test to verify Google Places API is working
"""
import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def test_google_places():
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")

    print(f"API Key found: {api_key[:20]}..." if api_key else "No API key!")

    if not api_key:
        print("ERROR: GOOGLE_PLACES_API_KEY not found in environment")
        return

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    params = {
        "query": "bathroom remodeling Jacksonville FL",
        "key": api_key
    }

    print(f"\nTesting Google Places API...")
    print(f"URL: {url}")
    print(f"Query: {params['query']}\n")

    try:
        async with aiohttp.ClientSession() as session:
            print("Making API request...")
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"Response status: {response.status}")

                if response.status == 200:
                    data = await response.json()
                    results = data.get('results', [])

                    print(f"\n✅ SUCCESS! Found {len(results)} results")

                    if results:
                        print("\nFirst result:")
                        first = results[0]
                        print(f"  Name: {first.get('name')}")
                        print(f"  Address: {first.get('formatted_address')}")
                        print(f"  Rating: {first.get('rating')}")
                        print(f"  Place ID: {first.get('place_id')}")
                else:
                    text = await response.text()
                    print(f"\n❌ ERROR: {response.status}")
                    print(f"Response: {text}")

    except asyncio.TimeoutError:
        print("❌ ERROR: Request timed out after 30 seconds")
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_google_places())
