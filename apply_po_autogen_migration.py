"""
Apply PO Auto-Generation Migration to Supabase
"""

import sys

def apply_migration():
    """Provide instructions for applying the migration"""

    print("\n" + "="*70)
    print("PO Auto-Generation Migration")
    print("="*70)
    print("\nThis migration adds auto-generation support for PO numbers.")
    print("\nSteps:")
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Paste the contents of: database/migrations/009_po_auto_generation.sql")
    print("4. Run the SQL")
    print("\nThe migration file is ready at:")
    print("  database/migrations/009_po_auto_generation.sql")
    print("\nThis migration will:")
    print("  - Add location_code, is_remake, is_warranty fields to jobs table")
    print("  - Create locations reference table with 3 locations:")
    print("    01 = Fernandina/Yulee, FL")
    print("    02 = Georgia")
    print("    03 = Jacksonville, FL")
    print("  - Add helper functions for PO generation:")
    print("    * extract_street_number(address) - extracts first number from address")
    print("    * format_name_for_po(...) - formats names for PO number")
    print("    * count_duplicate_pos(...) - counts existing POs for sequence numbering")
    print("  - Add indexes for performance")
    print("  - Add constraint to prevent both is_remake and is_warranty being true")
    print("\n" + "="*70)
    print("\n")

if __name__ == "__main__":
    apply_migration()
