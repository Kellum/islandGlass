"""Debug database access"""
import sys
import os
from dotenv import load_dotenv

load_dotenv('/Users/ryankellum/claude-proj/islandGlassLeads/.env')
sys.path.insert(0, '/Users/ryankellum/claude-proj/islandGlassLeads')

from modules.database import Database

print("Testing Database class...")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_KEY: {os.getenv('SUPABASE_KEY')[:20]}...")

db = Database()
print(f"\nDatabase client initialized")
print(f"URL: {db.url}")
print(f"Key: {db.key[:20]}...")

print("\nTrying to fetch glass_config...")
glass_configs = db.get_glass_config()
print(f"Got {len(glass_configs)} configs")

if len(glass_configs) > 0:
    print("\nFirst few configs:")
    for config in glass_configs[:3]:
        print(f"  {config}")
else:
    print("\n❌ NO CONFIGS FOUND")
    print("Trying direct Supabase query...")
    try:
        response = db.client.table("glass_config").select("*").execute()
        print(f"Direct query returned: {len(response.data)} rows")
        if len(response.data) > 0:
            print(f"First row: {response.data[0]}")
    except Exception as e:
        print(f"Direct query failed: {e}")
