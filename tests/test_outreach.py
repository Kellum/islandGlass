"""
Test outreach generation with enriched contractor
"""
from modules.outreach import OutreachGenerator
from modules.database import Database

def main():
    print("=" * 70)
    print("TESTING OUTREACH GENERATION")
    print("=" * 70)

    db = Database()
    generator = OutreachGenerator()

    # Get enriched contractors
    enriched = db.client.table("contractors").select("*").eq("enrichment_status", "completed").execute()

    if not enriched.data:
        print("\n⚠️  No enriched contractors found.")
        print("Please run enrichment first before generating outreach materials.")
        return

    contractor = enriched.data[0]
    contractor_id = contractor['id']

    print(f"\n1. Testing with enriched contractor:")
    print(f"   ID: {contractor_id}")
    print(f"   Company: {contractor['company_name']}")
    print(f"   Specializations: {contractor.get('specializations', 'N/A')}")
    print(f"   Glazing Opportunities: {contractor.get('glazing_opportunity_types', 'N/A')}")
    print(f"   Lead Score: {contractor.get('lead_score', 'N/A')}/10")
    print(f"   Outreach Angle: {contractor.get('outreach_angle', 'N/A')}")

    print(f"\n2. Generating outreach materials...")
    print("   (This will take 10-20 seconds)")

    # Generate outreach
    result = generator.generate_all_outreach(contractor_id)

    print(f"\n{'='*70}")
    print("OUTREACH GENERATION RESULT")
    print(f"{'='*70}")

    print(f"\nSuccess: {result['success']}")
    print(f"Message: {result['message']}")

    if result['success']:
        print(f"\n{'='*70}")
        print("GENERATED EMAIL TEMPLATES")
        print(f"{'='*70}")

        emails = result.get('emails', {})
        for i in range(1, 4):
            email_key = f"email_{i}"
            if email_key in emails:
                email = emails[email_key]
                print(f"\n📧 EMAIL {i}:")
                print(f"   Subject: {email.get('subject', 'N/A')}")
                print(f"   Body:\n")
                body = email.get('body', 'N/A')
                for line in body.split('\n'):
                    print(f"   {line}")
                print()

        print(f"\n{'='*70}")
        print("GENERATED CALL SCRIPTS")
        print(f"{'='*70}")

        scripts = result.get('scripts', {})
        for i in range(1, 3):
            script_key = f"script_{i}"
            if script_key in scripts:
                print(f"\n📞 CALL SCRIPT {i}:")
                script = scripts[script_key]
                for line in script.split('\n'):
                    print(f"   {line}")
                print()

        # Verify database save
        print(f"\n{'='*70}")
        print("DATABASE VERIFICATION")
        print(f"{'='*70}")

        materials = db.get_outreach_materials(contractor_id)
        print(f"\n✅ Saved {len(materials)} materials to database")

        for material in materials:
            print(f"   - {material['material_type']}: {material.get('subject_line', 'Script')}")

    else:
        print(f"\n❌ Outreach generation failed: {result['message']}")

    print(f"\n{'='*70}")
    print("✅ TEST COMPLETE")
    print(f"{'='*70}")

    print("\nNext: View outreach materials in Streamlit UI")
    print("  1. Go to 'Contractor Detail' page")
    print("  2. Select contractor to view generated materials")

if __name__ == "__main__":
    main()
