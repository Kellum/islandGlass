"""
Test script for contractor enrichment module
"""
import asyncio
from modules.enrichment import ContractorEnrichment
from modules.database import Database

def main():
    print("=" * 60)
    print("TESTING CONTRACTOR ENRICHMENT MODULE")
    print("=" * 60)

    # Initialize
    db = Database()
    enricher = ContractorEnrichment()

    # Get all contractors
    print("\n1. Fetching all contractors from database...")
    contractors = db.get_all_contractors()
    print(f"   Found {len(contractors)} contractors")

    # Display contractors
    print("\n2. Current contractors in database:")
    for contractor in contractors:
        print(f"\n   ID: {contractor['id']}")
        print(f"   Company: {contractor['company_name']}")
        print(f"   City: {contractor.get('city', 'N/A')}")
        print(f"   Website: {contractor.get('website', 'No website')}")
        print(f"   Enrichment Status: {contractor.get('enrichment_status', 'N/A')}")
        print(f"   Lead Score: {contractor.get('lead_score', 'Not scored')}")

    # Get pending enrichments
    print("\n3. Checking for contractors pending enrichment...")
    pending = enricher.get_pending_enrichments(limit=10)
    print(f"   Found {len(pending)} pending enrichment(s)")

    if not pending:
        print("\n   No contractors with websites pending enrichment.")
        print("   All contractors have been processed or don't have websites.")
        return

    # Display pending contractors
    print("\n4. Contractors pending enrichment:")
    for contractor in pending:
        print(f"   - {contractor['company_name']} ({contractor.get('city', 'N/A')})")
        print(f"     Website: {contractor.get('website', 'N/A')}")

    # Ask user if they want to test enrichment
    print("\n" + "=" * 60)
    response = input("\nTest enrichment on first contractor? (yes/no): ").strip().lower()

    if response == 'yes':
        test_contractor = pending[0]
        contractor_id = test_contractor['id']

        print(f"\n5. Testing enrichment for: {test_contractor['company_name']}")
        print(f"   Website: {test_contractor.get('website', 'N/A')}")
        print("\n   Running enrichment... (this may take 10-15 seconds)")

        # Run enrichment
        result = asyncio.run(enricher.enrich_contractor(contractor_id))

        print("\n" + "=" * 60)
        print("ENRICHMENT RESULT")
        print("=" * 60)

        if result['success']:
            print(f"\n✅ SUCCESS: {result['message']}")

            if result.get('enrichment_data'):
                data = result['enrichment_data']
                print("\nExtracted Data:")
                print(f"  Lead Score: {data.get('glazing_opportunity_score', 'N/A')}/10")
                print(f"  Company Type: {data.get('company_type', 'N/A')}")
                print(f"  Contact Email: {data.get('contact_email', 'N/A')}")
                print(f"  Contact Person: {data.get('contact_person', 'N/A')}")
                print(f"  Specializations: {', '.join(data.get('specializations', []))}")
                print(f"  Glazing Opportunities: {', '.join(data.get('glazing_opportunity_types', []))}")
                print(f"  Uses Subcontractors: {data.get('uses_subcontractors', 'N/A')}")
                print(f"\n  Profile Notes: {data.get('profile_notes', 'N/A')}")
                print(f"\n  Outreach Angle: {data.get('outreach_angle', 'N/A')}")
        else:
            print(f"\n⚠️  FAILED: {result['message']}")
            if result.get('enrichment_data'):
                data = result['enrichment_data']
                print(f"\n  Score: {data.get('glazing_opportunity_score', 'N/A')}/10")
                print(f"  Disqualify Reason: {data.get('disqualify_reason', 'N/A')}")

        # Show updated contractor
        print("\n6. Fetching updated contractor record...")
        updated_contractor = db.get_contractor_by_id(contractor_id)

        print(f"\n   Enrichment Status: {updated_contractor.get('enrichment_status', 'N/A')}")
        print(f"   Lead Score: {updated_contractor.get('lead_score', 'Not scored')}")
        print(f"   Specializations: {updated_contractor.get('specializations', 'N/A')}")

    else:
        print("\n   Skipping enrichment test.")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run the Streamlit app: streamlit run app.py --server.port 8080")
    print("  2. Navigate to 'Website Enrichment' page")
    print("  3. Test enrichment through the UI")

if __name__ == "__main__":
    main()
