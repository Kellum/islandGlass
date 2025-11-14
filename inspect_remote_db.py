"""
Inspect Remote Supabase Database Schema
This script will query the database to see what tables and columns exist
"""

from modules.database import Database
import json

def inspect_database():
    """Query the database to see current schema"""

    print("\n" + "="*70)
    print("REMOTE DATABASE INSPECTION")
    print("="*70)

    db = Database()

    # Get all tables in public schema
    print("\n1. Fetching all tables in public schema...")
    tables_query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """

    result = db.client.rpc('exec_sql', {'query': tables_query}).execute()
    if hasattr(result, 'data') and result.data:
        tables = [row['table_name'] for row in result.data]
    else:
        # Fallback: manually check known tables
        print("   Could not query information_schema, checking known tables...")
        known_tables = [
            'jobs', 'vendors', 'purchase_orders', 'po_clients',
            'locations', 'users', 'user_profiles', 'glass_config'
        ]
        tables = []
        for table in known_tables:
            try:
                db.client.table(table).select("id").limit(1).execute()
                tables.append(table)
            except:
                pass

    print(f"\n   Found {len(tables)} tables:")
    for table in tables:
        print(f"   - {table}")

    # For each table, get columns
    print("\n2. Fetching column details for each table...")
    schema_details = {}

    for table in tables:
        columns_query = f"""
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = '{table}'
            ORDER BY ordinal_position;
        """

        columns = db.execute_query(columns_query)
        schema_details[table] = columns

        print(f"\n   Table: {table}")
        print(f"   Columns: {len(columns)}")
        for col in columns:
            print(f"     - {col['column_name']} ({col['data_type']})")

    # Check for specific migration-related objects
    print("\n3. Checking for key objects from migrations...")

    # Check if vendors table exists (from migration 007)
    if 'vendors' in tables:
        print("   ✓ vendors table EXISTS (from 007_po_system_phase1.sql)")
    else:
        print("   ✗ vendors table MISSING (should be in 007_po_system_phase1.sql)")

    # Check if purchase_orders table exists
    if 'purchase_orders' in tables:
        print("   ✓ purchase_orders table EXISTS (from 007_po_system_phase1.sql)")
    else:
        print("   ✗ purchase_orders table MISSING (should be in 007_po_system_phase1.sql)")

    # Check if locations table exists (from migration 009)
    if 'locations' in tables:
        print("   ✓ locations table EXISTS (from 009_po_auto_generation.sql)")
    else:
        print("   ✗ locations table MISSING (should be in 009_po_auto_generation.sql)")

    # Check jobs table for new columns from migration 009
    if 'jobs' in tables:
        jobs_cols = [col['column_name'] for col in schema_details['jobs']]

        if 'location_code' in jobs_cols:
            print("   ✓ jobs.location_code EXISTS (from 009_po_auto_generation.sql)")
        else:
            print("   ✗ jobs.location_code MISSING (should be in 009_po_auto_generation.sql)")

        if 'is_remake' in jobs_cols:
            print("   ✓ jobs.is_remake EXISTS (from 009_po_auto_generation.sql)")
        else:
            print("   ✗ jobs.is_remake MISSING (should be in 009_po_auto_generation.sql)")

        if 'is_warranty' in jobs_cols:
            print("   ✓ jobs.is_warranty EXISTS (from 009_po_auto_generation.sql)")
        else:
            print("   ✗ jobs.is_warranty MISSING (should be in 009_po_auto_generation.sql)")

    # Check for functions from migration 009
    print("\n4. Checking for custom functions...")
    functions_query = """
        SELECT
            routine_name
        FROM information_schema.routines
        WHERE routine_schema = 'public'
        AND routine_type = 'FUNCTION'
        ORDER BY routine_name;
    """

    functions = db.execute_query(functions_query)
    function_names = [f['routine_name'] for f in functions]

    print(f"\n   Found {len(function_names)} custom functions:")
    for func in function_names:
        print(f"   - {func}")

    # Check for specific functions from migration 009
    if 'extract_street_number' in function_names:
        print("   ✓ extract_street_number function EXISTS (from 009_po_auto_generation.sql)")
    else:
        print("   ✗ extract_street_number function MISSING (should be in 009_po_auto_generation.sql)")

    if 'format_name_for_po' in function_names:
        print("   ✓ format_name_for_po function EXISTS (from 009_po_auto_generation.sql)")
    else:
        print("   ✗ format_name_for_po function MISSING (should be in 009_po_auto_generation.sql)")

    print("\n" + "="*70)
    print("INSPECTION COMPLETE")
    print("="*70)
    print("\nSummary saved to: db_inspection_report.json")

    # Save detailed report
    report = {
        'tables': tables,
        'schema_details': {
            table: [
                {
                    'column': col['column_name'],
                    'type': col['data_type'],
                    'nullable': col['is_nullable'],
                    'default': col['column_default']
                }
                for col in cols
            ]
            for table, cols in schema_details.items()
        },
        'functions': function_names
    }

    with open('db_inspection_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    return report

if __name__ == "__main__":
    inspect_database()
