"""
Simple Calculator Data Seeder
Uses Supabase client directly to seed calculator pricing
"""
import os
from supabase import create_client, Client

# Load environment
SUPABASE_URL = "https://dgsjmsccpdrgnnpzlsgj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRnc2ptc2NjcGRyZ25ucHpsc2dqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDQ4MDI3MCwiZXhwIjoyMDc2MDU2MjcwfQ.2hDVGbUHJkkxOGB1mKe0lScSD4TdmhgzwhhfdaVAGMU"

client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_company_and_user():
    """Get first company and user IDs"""
    try:
        # Get first company
        company_resp = client.table("companies").select("id").limit(1).execute()
        if not company_resp.data:
            print("❌ No company found. Please create a company first.")
            return None, None
        company_id = company_resp.data[0]['id']

        # Get first user
        user_resp = client.auth.admin.list_users()
        if not user_resp or len(user_resp) == 0:
            print("❌ No users found. Please create a user first.")
            return None, None
        user_id = user_resp[0].id

        return company_id, user_id
    except Exception as e:
        print(f"Error getting company/user: {e}")
        return None, None

def seed_data():
    print("=" * 80)
    print("SEEDING CALCULATOR DATA")
    print("=" * 80)

    company_id, user_id = get_company_and_user()
    if not company_id or not user_id:
        return

    print(f"\nUsing:")
    print(f"  Company ID: {company_id}")
    print(f"  User ID: {user_id}")

    # Glass Config
    print("\n1. Seeding glass_config...")
    glass_configs = [
        ('1/8"', 'clear', 8.50, 0.65, False, False, False),
        ('3/16"', 'clear', 10.00, 0.75, True, False, False),
        ('1/4"', 'clear', 12.50, 0.85, False, False, False),
        ('3/8"', 'clear', 18.00, 1.10, False, False, False),
        ('1/2"', 'clear', 22.50, 1.35, False, False, False),
        ('1/4"', 'bronze', 18.00, 0.85, False, False, False),
        ('3/8"', 'bronze', 25.00, 1.10, False, False, False),
        ('1/2"', 'bronze', 30.00, 1.35, False, False, False),
        ('1/4"', 'gray', 16.50, 0.85, False, False, False),
        ('3/8"', 'gray', 23.00, 1.10, False, False, False),
        ('1/2"', 'gray', 28.00, 1.35, False, False, False),
        ('1/4"', 'mirror', 15.00, 0.27, False, True, True),
        ('3/8"', 'mirror', 20.00, 0.27, False, True, True),
    ]

    for thickness, type_name, base, polish, only_temp, no_pol, never_temp in glass_configs:
        try:
            client.table("glass_config").insert({
                "thickness": thickness,
                "type": type_name,
                "base_price": base,
                "polish_price": polish,
                "only_tempered": only_temp,
                "no_polish": no_pol,
                "never_tempered": never_temp,
                "company_id": company_id,
                "created_by": user_id
            }).execute()
            print(f"   ✅ {thickness} {type_name}")
        except Exception as e:
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                print(f"   ⚠️  {thickness} {type_name} (already exists)")
            else:
                print(f"   ❌ {thickness} {type_name}: {e}")

    # Markups
    print("\n2. Seeding markups...")
    markups = [
        ('tempered', 35.0),
        ('shape', 25.0)
    ]

    for name, percentage in markups:
        try:
            client.table("markups").insert({
                "name": name,
                "percentage": percentage,
                "company_id": company_id,
                "created_by": user_id
            }).execute()
            print(f"   ✅ {name}: {percentage}%")
        except Exception as e:
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                print(f"   ⚠️  {name} (already exists)")
            else:
                print(f"   ❌ {name}: {e}")

    # Beveled pricing
    print("\n3. Seeding beveled_pricing...")
    beveled = [
        ('3/16"', 1.50),
        ('1/4"', 2.01),
        ('3/8"', 2.91),
        ('1/2"', 3.80)
    ]

    for thickness, price in beveled:
        try:
            client.table("beveled_pricing").insert({
                "glass_thickness": thickness,
                "price_per_inch": price,
                "company_id": company_id,
                "created_by": user_id
            }).execute()
            print(f"   ✅ {thickness}: ${price}/inch")
        except Exception as e:
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                print(f"   ⚠️  {thickness} (already exists)")
            else:
                print(f"   ❌ {thickness}: {e}")

    # Clipped corners
    print("\n4. Seeding clipped_corners_pricing...")
    corners = [
        ('1/4"', 'under_1', 5.50),
        ('1/4"', 'over_1', 22.18),
        ('3/8"', 'under_1', 7.50),
        ('3/8"', 'over_1', 30.00),
        ('1/2"', 'under_1', 9.00),
        ('1/2"', 'over_1', 35.00)
    ]

    for thickness, clip_size, price in corners:
        try:
            client.table("clipped_corners_pricing").insert({
                "glass_thickness": thickness,
                "clip_size": clip_size,
                "price_per_corner": price,
                "company_id": company_id,
                "created_by": user_id
            }).execute()
            print(f"   ✅ {thickness} {clip_size}: ${price}")
        except Exception as e:
            if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                print(f"   ⚠️  {thickness} {clip_size} (already exists)")
            else:
                print(f"   ❌ {thickness} {clip_size}: {e}")

    print("\n" + "=" * 80)
    print("✅ SEEDING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    seed_data()
