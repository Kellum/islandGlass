"""
Test script for the contractor scraper
"""
import asyncio
from modules.database import Database
from modules.scraper import ContractorScraper


async def test_basic_scrape():
    """Test basic scraping functionality"""
    print("Initializing database connection...")
    db = Database()

    print("Creating scraper instance...")
    scraper = ContractorScraper(db)

    print("\nTesting scraper with query: 'bathroom remodeling Jacksonville FL'")
    print("=" * 60)

    results = await scraper.discover_contractors(
        search_query="bathroom remodeling Jacksonville FL",
        max_results=10,
        save_to_db=False  # Don't save during initial test
    )

    print("\nResults Summary:")
    print(f"Total Found: {results['total_found']}")
    print(f"Saved: {results['saved']}")
    print(f"Duplicates: {results['duplicates']}")
    print(f"Errors: {results['errors']}")

    print("\nContractors:")
    print("=" * 60)

    if results['contractors']:
        for idx, contractor in enumerate(results['contractors'], 1):
            print(f"\n{idx}. {contractor.get('company_name', 'Unknown')}")
            print(f"   Phone: {contractor.get('phone', 'N/A')}")
            print(f"   Address: {contractor.get('address', 'N/A')}")
            print(f"   City: {contractor.get('city', 'N/A')}")
            print(f"   Rating: {contractor.get('google_rating', 'N/A')}")
            print(f"   Website: {contractor.get('website', 'N/A')}")
    else:
        print("No contractors found.")
        print("\nNote: Google Maps scraping is challenging due to dynamic content.")
        print("Consider using Google Places API for better results.")


if __name__ == "__main__":
    print("Starting scraper test...\n")
    asyncio.run(test_basic_scrape())
    print("\n✅ Test complete!")
