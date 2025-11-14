"""
Apply PO System Phase 1 Migration to Supabase
"""

from modules.database import Database
import sys

def apply_migration():
    """Apply the Phase 1 migration SQL"""

    print("Connecting to database...")
    db = Database()

    # Read the migration file
    print("Reading migration file...")
    with open('database/migrations/007_po_system_phase1.sql', 'r') as f:
        sql = f.read()

    # For Supabase, we need to execute via RPC or use the SQL editor
    # Since we're using the Python client, we'll need to run this manually
    # in the Supabase SQL editor

    print("\n" + "="*70)
    print("IMPORTANT: Manual Migration Required")
    print("="*70)
    print("\nThe PO System Phase 1 migration needs to be run manually in Supabase.")
    print("\nSteps:")
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Paste the contents of: database/migrations/007_po_system_phase1.sql")
    print("4. Run the SQL")
    print("\nThe migration file is ready at:")
    print("  /Users/ryankellum/claude-proj/islandGlassLeads/database/migrations/007_po_system_phase1.sql")
    print("\nThis migration will create:")
    print("  - vendors table")
    print("  - purchase_orders table")
    print("  - po_items table")
    print("  - po_receiving_history table")
    print("  - po_payment_history table")
    print("  - quickbooks_sync_log table")
    print("  - System settings table (if not exists)")
    print("  - Jobs table enhancements")
    print("  - Triggers and functions for auto-calculations")
    print("\n" + "="*70)
    print("\n")

if __name__ == "__main__":
    apply_migration()
