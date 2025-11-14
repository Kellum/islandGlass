"""
Simple Database Inspection - Check what exists in Supabase
"""

from modules.database import Database
import json

def check_database():
    """Simple check of what tables and data exist"""

    print("\n" + "="*70)
    print("SIMPLE DATABASE INSPECTION")
    print("="*70)

    db = Database()

    # List of tables we expect from migrations
    tables_to_check = {
        'jobs': 'Basic jobs table (from 001)',
        'po_clients': 'PO clients table (from 001)',
        'vendors': 'Vendors table (from 007_po_system_phase1.sql)',
        'purchase_orders': 'Purchase orders table (from 007)',
        'locations': 'Locations table (from 009_po_auto_generation.sql)',
        'calculator_settings': 'Calculator settings (from 005)',
        'pricing_formula_config': 'Pricing formula config (from 006)',
        'glass_config': 'Glass config table (from initial)',
    }

    print("\nChecking which tables exist...\n")

    existing_tables = []
    missing_tables = []

    for table, description in tables_to_check.items():
        try:
            # Try to query the table (just count)
            response = db.client.table(table).select("*", count="exact").limit(0).execute()
            count = response.count if hasattr(response, 'count') else 0
            existing_tables.append(table)
            print(f"   ✓ {table:30} EXISTS  ({description})")
            print(f"     └─ Record count: {count}")
        except Exception as e:
            missing_tables.append(table)
            print(f"   ✗ {table:30} MISSING ({description})")
            print(f"     └─ Error: {str(e)[:80]}")

    # Check for specific columns in jobs table (from migration 009)
    if 'jobs' in existing_tables:
        print("\n\nChecking jobs table for columns from migration 009...")
        try:
            # Get one job to see its columns
            response = db.client.table("jobs").select("*").limit(1).execute()
            if response.data and len(response.data) > 0:
                job_cols = response.data[0].keys()
                migration_009_cols = ['location_code', 'is_remake', 'is_warranty']

                for col in migration_009_cols:
                    if col in job_cols:
                        print(f"   ✓ jobs.{col} EXISTS (from 009_po_auto_generation.sql)")
                    else:
                        print(f"   ✗ jobs.{col} MISSING (should be in 009_po_auto_generation.sql)")
            else:
                print("   No jobs found to inspect columns")
        except Exception as e:
            print(f"   Error checking jobs columns: {e}")

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\n✓ Existing tables: {len(existing_tables)}/{len(tables_to_check)}")
    for table in existing_tables:
        print(f"   - {table}")

    if missing_tables:
        print(f"\n✗ Missing tables: {len(missing_tables)}")
        for table in missing_tables:
            print(f"   - {table}")

    print("\n" + "="*70)

    # Save report
    report = {
        'existing_tables': existing_tables,
        'missing_tables': missing_tables,
        'total_checked': len(tables_to_check)
    }

    with open('db_inspection_simple.json', 'w') as f:
        json.dump(report, f, indent=2)

    print("Report saved to: db_inspection_simple.json\n")

    return report

if __name__ == "__main__":
    check_database()
