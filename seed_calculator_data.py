"""
Seed Calculator Pricing Data
Populates the database with calculator pricing configuration
"""
import sys
sys.path.insert(0, '/Users/ryankellum/claude-proj/islandGlassLeads')

from modules.database import Database

def seed_calculator_data():
    """Seed all calculator pricing data"""
    db = Database()

    print("=" * 80)
    print("SEEDING CALCULATOR PRICING DATA")
    print("=" * 80)

    # Get company_id and user_id
    print("\n1. Getting company and user IDs...")
    company_id, user_id = db.get_first_company_and_user()

    if not company_id or not user_id:
        print("❌ ERROR: Could not find company or user. Please create a company and user first.")
        return False

    print(f"   Company ID: {company_id}")
    print(f"   User ID: {user_id}")

    # Seed glass config
    print("\n2. Seeding glass configuration...")
    glass_configs = [
        # 1/8" Clear
        {'thickness': '1/8"', 'type': 'clear', 'base_price': 8.50, 'polish_price': 0.65},

        # 3/16" Clear (must be tempered)
        {'thickness': '3/16"', 'type': 'clear', 'base_price': 10.00, 'polish_price': 0.75, 'only_tempered': True},

        # 1/4" Clear
        {'thickness': '1/4"', 'type': 'clear', 'base_price': 12.50, 'polish_price': 0.85},

        # 3/8" Clear
        {'thickness': '3/8"', 'type': 'clear', 'base_price': 18.00, 'polish_price': 1.10},

        # 1/2" Clear
        {'thickness': '1/2"', 'type': 'clear', 'base_price': 22.50, 'polish_price': 1.35},

        # 1/4" Bronze
        {'thickness': '1/4"', 'type': 'bronze', 'base_price': 18.00, 'polish_price': 0.85},

        # 3/8" Bronze
        {'thickness': '3/8"', 'type': 'bronze', 'base_price': 25.00, 'polish_price': 1.10},

        # 1/2" Bronze
        {'thickness': '1/2"', 'type': 'bronze', 'base_price': 30.00, 'polish_price': 1.35},

        # 1/4" Gray
        {'thickness': '1/4"', 'type': 'gray', 'base_price': 16.50, 'polish_price': 0.85},

        # 3/8" Gray
        {'thickness': '3/8"', 'type': 'gray', 'base_price': 23.00, 'polish_price': 1.10},

        # 1/2" Gray
        {'thickness': '1/2"', 'type': 'gray', 'base_price': 28.00, 'polish_price': 1.35},

        # 1/4" Mirror (cannot be tempered, flat polish only)
        {'thickness': '1/4"', 'type': 'mirror', 'base_price': 15.00, 'polish_price': 0.27, 'no_polish': True, 'never_tempered': True},

        # 3/8" Mirror
        {'thickness': '3/8"', 'type': 'mirror', 'base_price': 20.00, 'polish_price': 0.27, 'no_polish': True, 'never_tempered': True}
    ]

    for config in glass_configs:
        try:
            result = db.insert_glass_config(
                thickness=config['thickness'],
                type_name=config['type'],
                base_price=config['base_price'],
                polish_price=config['polish_price'],
                only_tempered=config.get('only_tempered', False),
                no_polish=config.get('no_polish', False),
                never_tempered=config.get('never_tempered', False),
                company_id=company_id,
                created_by=user_id
            )
            if result:
                print(f"   ✅ {config['thickness']} {config['type']}")
            else:
                print(f"   ⚠️  {config['thickness']} {config['type']} (already exists)")
        except Exception as e:
            print(f"   ❌ {config['thickness']} {config['type']}: {e}")

    # Seed markups
    print("\n3. Seeding markups...")
    markups = [
        {'name': 'tempered', 'percentage': 35.0},
        {'name': 'shape', 'percentage': 25.0}
    ]

    for markup in markups:
        try:
            result = db.insert_markup(
                name=markup['name'],
                percentage=markup['percentage'],
                company_id=company_id,
                created_by=user_id
            )
            if result:
                print(f"   ✅ {markup['name']}: {markup['percentage']}%")
            else:
                print(f"   ⚠️  {markup['name']} (already exists)")
        except Exception as e:
            print(f"   ❌ {markup['name']}: {e}")

    # Seed beveled pricing
    print("\n4. Seeding beveled pricing...")
    beveled = [
        {'thickness': '3/16"', 'price_per_inch': 1.50},
        {'thickness': '1/4"', 'price_per_inch': 2.01},
        {'thickness': '3/8"', 'price_per_inch': 2.91},
        {'thickness': '1/2"', 'price_per_inch': 3.80}
    ]

    for item in beveled:
        try:
            result = db.insert_beveled_pricing(
                glass_thickness=item['thickness'],
                price_per_inch=item['price_per_inch'],
                company_id=company_id,
                created_by=user_id
            )
            if result:
                print(f"   ✅ {item['thickness']}: ${item['price_per_inch']}/inch")
            else:
                print(f"   ⚠️  {item['thickness']} (already exists)")
        except Exception as e:
            print(f"   ❌ {item['thickness']}: {e}")

    # Seed clipped corners pricing
    print("\n5. Seeding clipped corners pricing...")
    corners = [
        {'thickness': '1/4"', 'clip_size': 'under_1', 'price': 5.50},
        {'thickness': '1/4"', 'clip_size': 'over_1', 'price': 22.18},
        {'thickness': '3/8"', 'clip_size': 'under_1', 'price': 7.50},
        {'thickness': '3/8"', 'clip_size': 'over_1', 'price': 30.00},
        {'thickness': '1/2"', 'clip_size': 'under_1', 'price': 9.00},
        {'thickness': '1/2"', 'clip_size': 'over_1', 'price': 35.00}
    ]

    for item in corners:
        try:
            result = db.insert_clipped_corner_pricing(
                glass_thickness=item['thickness'],
                clip_size=item['clip_size'],
                price_per_corner=item['price'],
                company_id=company_id,
                created_by=user_id
            )
            if result:
                print(f"   ✅ {item['thickness']} {item['clip_size']}: ${item['price']}")
            else:
                print(f"   ⚠️  {item['thickness']} {item['clip_size']} (already exists)")
        except Exception as e:
            print(f"   ❌ {item['thickness']} {item['clip_size']}: {e}")

    print("\n" + "=" * 80)
    print("✅ SEEDING COMPLETE")
    print("=" * 80)

    return True


if __name__ == "__main__":
    seed_calculator_data()
