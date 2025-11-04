"""
Test script for scraper with database save
"""
import asyncio
from modules.database import Database
from modules.scraper import ContractorScraper


async def test_save_to_db():
    """Test saving scraped contractors to database"""
    print("Initializing database connection...")
    db = Database()

    print("Creating scraper instance...")
    scraper = ContractorScraper(db)

    print("\nTesting scraper with save to database...")
    print("=" * 60)

    results = await scraper.discover_contractors(
        search_query="bathroom remodeling Jacksonville FL",
        max_results=5,
        save_to_db=True  # Save to database
    )

    print("\nResults Summary:")
    print(f"Total Found: {results['total_found']}")
    print(f"Saved to DB: {results['saved']}")
    print(f"Duplicates Skipped: {results['duplicates']}")
    print(f"Errors: {results['errors']}")

    print("\nVerifying database...")
    all_contractors = db.get_all_contractors()
    print(f"Total contractors in database: {len(all_contractors)}")

    print("\nRecent contractors:")
    print("=" * 60)
    for contractor in all_contractors[-5:]:
        print(f"- {contractor['company_name']} ({contractor['source']})")


if __name__ == "__main__":
    print("Starting scraper save test...\n")
    asyncio.run(test_save_to_db())
    print("\n✅ Test complete!")
