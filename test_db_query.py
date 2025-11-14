"""Quick database query test"""
from supabase import create_client

SUPABASE_URL = "https://dgsjmsccpdrgnnpzlsgj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRnc2ptc2NjcGRyZ25ucHpsc2dqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDQ4MDI3MCwiZXhwIjoyMDc2MDU2MjcwfQ.2hDVGbUHJkkxOGB1mKe0lScSD4TdmhgzwhhfdaVAGMU"

client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Testing glass_config query...")
try:
    # Try 1: With is deleted_at null
    response1 = client.table("glass_config").select("*").is_("deleted_at", "null").execute()
    print(f"With is_(deleted_at, null): {len(response1.data)} rows")

    # Try 2: Without filter
    response2 = client.table("glass_config").select("*").execute()
    print(f"Without filter: {len(response2.data)} rows")

    # Try 3: Check for soft deletes
    if len(response2.data) > 0:
        print("\nFirst 3 rows:")
        for row in response2.data[:3]:
            print(f"  {row.get('thickness')} {row.get('type')}: base={row.get('base_price')}, deleted_at={row.get('deleted_at')}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
