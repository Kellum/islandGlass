"""
Simple automated test for enrichment module
"""
import asyncio
from modules.enrichment import ContractorEnrichment
from modules.database import Database

async def test_enrichment():
    print("=" * 60)
    print("SIMPLE ENRICHMENT TEST")
    print("=" * 60)

    db = Database()
    enricher = ContractorEnrichment()

    # Get contractors
    contractors = db.get_all_contractors()
    print(f"\nTotal contractors: {len(contractors)}")

    # Get pending
    pending = enricher.get_pending_enrichments(limit=1)

    if pending:
        contractor = pending[0]
        print(f"\nTesting enrichment for: {contractor['company_name']}")
        print(f"Website: {contractor.get('website', 'N/A')}")

        # Test enrichment
        result = await enricher.enrich_contractor(contractor['id'])

        print(f"\n{'='*60}")
        print("RESULT:")
        print(f"{'='*60}")
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")

        if result.get('enrichment_data'):
            data = result['enrichment_data']
            print(f"\nScore: {data.get('glazing_opportunity_score', 'N/A')}/10")
            if data.get('profile_notes'):
                print(f"Notes: {data.get('profile_notes')}")

        print(f"\n{'='*60}")
        print("✅ TEST COMPLETE")
        print(f"{'='*60}")

    else:
        print("\n⚠️  No contractors pending enrichment")

    print("\nNote: Since these are example.com URLs, enrichment will fail.")
    print("To test with real contractors:")
    print("  1. Add real contractor websites to the database")
    print("  2. Or test through the Streamlit UI with real Google Maps results")

if __name__ == "__main__":
    asyncio.run(test_enrichment())
