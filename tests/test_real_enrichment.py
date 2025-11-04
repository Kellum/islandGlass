"""
Test enrichment with a real website
"""
import asyncio
from modules.enrichment import ContractorEnrichment
from modules.database import Database

async def test_real_enrichment():
    print("=" * 60)
    print("TESTING ENRICHMENT WITH REAL WEBSITE")
    print("=" * 60)

    db = Database()
    enricher = ContractorEnrichment()

    # Get contractor ID 2 and update with a real website
    test_contractor_id = 2

    print("\n1. Updating contractor ID 2 with a real website...")

    # Update with a real bathroom remodeling company
    # Using a generic construction company website that should be accessible
    real_website = "https://www.bhg.com/bathroom-remodeling-6828851"  # Better Homes & Gardens bathroom remodeling article

    success = db.update_contractor(test_contractor_id, {
        "website": real_website,
        "enrichment_status": "pending"
    })

    if not success:
        print("   ❌ Failed to update contractor")
        return

    print(f"   ✅ Updated website to: {real_website}")

    # Get updated contractor
    contractor = db.get_contractor_by_id(test_contractor_id)
    print(f"\n2. Contractor: {contractor['company_name']}")
    print(f"   Website: {contractor['website']}")

    print("\n3. Running enrichment...")
    print("   (This will fetch the website and analyze with Claude API)")
    print("   (May take 15-20 seconds)")

    # Run enrichment
    result = await enricher.enrich_contractor(test_contractor_id)

    print(f"\n{'='*60}")
    print("ENRICHMENT RESULT")
    print(f"{'='*60}")

    print(f"\nSuccess: {result['success']}")
    print(f"Message: {result['message']}")

    if result['success'] and result.get('enrichment_data'):
        data = result['enrichment_data']

        print(f"\n{'='*60}")
        print("EXTRACTED DATA:")
        print(f"{'='*60}")

        print(f"\n📊 LEAD SCORE: {data.get('glazing_opportunity_score', 'N/A')}/10")
        print(f"\n🏢 Company Info:")
        print(f"   Type: {data.get('company_type', 'N/A')}")
        print(f"   Contact: {data.get('contact_person', 'N/A')}")
        print(f"   Email: {data.get('contact_email', 'N/A')}")

        print(f"\n🔧 Specializations:")
        for spec in data.get('specializations', []):
            print(f"   - {spec}")

        print(f"\n🪟 Glazing Opportunities:")
        for opp in data.get('glazing_opportunity_types', []):
            print(f"   - {opp}")

        print(f"\n📝 Profile Notes:")
        print(f"   {data.get('profile_notes', 'N/A')}")

        print(f"\n💡 Outreach Angle:")
        print(f"   {data.get('outreach_angle', 'N/A')}")

        print(f"\n🤝 Uses Subcontractors: {data.get('uses_subcontractors', 'N/A')}")

        if data.get('disqualify_reason'):
            print(f"\n⚠️  Disqualify Reason: {data.get('disqualify_reason')}")

    elif not result['success']:
        print(f"\n❌ Enrichment failed: {result['message']}")
        if result.get('enrichment_data'):
            data = result['enrichment_data']
            print(f"   Score: {data.get('glazing_opportunity_score', 'N/A')}/10")
            print(f"   Reason: {data.get('disqualify_reason', 'N/A')}")

    # Show updated database record
    print(f"\n{'='*60}")
    print("UPDATED DATABASE RECORD")
    print(f"{'='*60}")

    updated = db.get_contractor_by_id(test_contractor_id)
    print(f"\nCompany: {updated['company_name']}")
    print(f"Enrichment Status: {updated.get('enrichment_status', 'N/A')}")
    print(f"Lead Score: {updated.get('lead_score', 'Not scored')}")
    print(f"Specializations: {updated.get('specializations', 'N/A')}")
    print(f"Glazing Opportunities: {updated.get('glazing_opportunity_types', 'N/A')}")

    print(f"\n{'='*60}")
    print("✅ TEST COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(test_real_enrichment())
