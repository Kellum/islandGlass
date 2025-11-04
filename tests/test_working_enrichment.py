"""
Test enrichment with a reliable working website
"""
import asyncio
from modules.enrichment import ContractorEnrichment
from modules.database import Database

async def test_working_enrichment():
    print("=" * 60)
    print("TESTING ENRICHMENT WITH WORKING WEBSITE")
    print("=" * 60)

    db = Database()
    enricher = ContractorEnrichment()

    test_contractor_id = 3

    print("\n1. Updating contractor ID 3 with a real working website...")

    # Use a reliable contractor website
    # Let's use a Jacksonville area contractor
    real_website = "https://www.jacksonvilleremodeler.com"

    success = db.update_contractor(test_contractor_id, {
        "website": real_website,
        "enrichment_status": "pending"
    })

    if success:
        print(f"   ✅ Updated website to: {real_website}")
    else:
        print("   ❌ Failed to update contractor")
        return

    contractor = db.get_contractor_by_id(test_contractor_id)
    print(f"\n2. Testing: {contractor['company_name']}")
    print(f"   Website: {contractor['website']}")

    print("\n3. Running enrichment (15-20 seconds)...")

    result = await enricher.enrich_contractor(test_contractor_id)

    print(f"\n{'='*60}")
    print("RESULT")
    print(f"{'='*60}")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")

    if result['success'] and result.get('enrichment_data'):
        data = result['enrichment_data']
        print(f"\n✅ ENRICHMENT SUCCESSFUL!")
        print(f"\nLead Score: {data.get('glazing_opportunity_score')}/10")
        print(f"Company Type: {data.get('company_type')}")
        print(f"Specializations: {', '.join(data.get('specializations', []))}")
        print(f"Glazing Opportunities: {', '.join(data.get('glazing_opportunity_types', []))}")
        print(f"\nProfile Notes: {data.get('profile_notes')}")
        print(f"\nOutreach Angle: {data.get('outreach_angle')}")
    else:
        print(f"\n⚠️  {result['message']}")

    print(f"\n{'='*60}")

if __name__ == "__main__":
    asyncio.run(test_working_enrichment())
