"""
Apply Safe Migration to Supabase
Adds missing tables and columns from migrations 007 and 009
"""

from modules.database import Database
import sys

def apply_migration():
    """Apply the safe migration SQL"""

    print("\n" + "="*70)
    print("APPLYING SAFE MIGRATION TO SUPABASE")
    print("="*70)

    # Read the migration SQL
    print("\nReading migration file...")
    with open('database/migrations/SAFE_ADD_MISSING_ITEMS.sql', 'r') as f:
        migration_sql = f.read()

    print(f"Migration file loaded: {len(migration_sql)} characters")

    # Connect to database
    print("\nConnecting to Supabase...")
    db = Database()

    # Execute the migration using raw SQL
    # Note: Supabase Python client doesn't have a direct SQL execution method
    # We'll need to use the REST API or psql
    print("\nIMPORTANT: The Python Supabase client doesn't support raw SQL execution.")
    print("Please use one of these methods instead:")
    print("\n1. Supabase Dashboard (RECOMMENDED):")
    print("   - Go to: https://supabase.com/dashboard")
    print("   - Navigate to SQL Editor")
    print("   - Copy the contents of: database/migrations/SAFE_ADD_MISSING_ITEMS.sql")
    print("   - Paste and click 'Run'")

    print("\n2. Using psql directly:")
    print("   psql 'postgresql://postgres:[YOUR-PASSWORD]@db.dgsjmsccpdrgnnpzlsgj.supabase.co:5432/postgres' \\")
    print("        -f database/migrations/SAFE_ADD_MISSING_ITEMS.sql")

    print("\n3. I can display the SQL for you to copy:")
    response = input("\nWould you like me to display the SQL to copy? (y/n): ")

    if response.lower() == 'y':
        print("\n" + "="*70)
        print("MIGRATION SQL - COPY THIS TO SUPABASE SQL EDITOR")
        print("="*70)
        print(migration_sql)
        print("\n" + "="*70)

    print("\nAfter running the migration, verify with:")
    print("  python3 simple_db_check.py")
    print("\n" + "="*70)

if __name__ == "__main__":
    apply_migration()
