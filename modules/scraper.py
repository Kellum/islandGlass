"""
Contractor Discovery Module - Web Scraping
Searches for contractors using various methods:
1. Google Places API (recommended for production)
2. Mock data for testing (when API not available)

Note: For real scraping, consider using Google Places API or similar services
"""
import asyncio
import time
import re
import os
from typing import List, Dict, Optional
from modules.database import Database


class ContractorScraper:
    """Finds contractor leads using various data sources"""

    def __init__(self, db: Database):
        """Initialize scraper with database connection"""
        self.db = db
        self.rate_limit_delay = 2  # seconds between requests
        self.max_retries = 3
        self.google_places_api_key = os.getenv("GOOGLE_PLACES_API_KEY")

    async def search_google_places(
        self,
        search_query: str,
        location: str = "Jacksonville, FL",
        max_results: int = 20
    ) -> List[Dict]:
        """
        Search using Google Places API (Text Search) with pagination support
        Fetches up to 60 results across 3 pages
        Requires GOOGLE_PLACES_API_KEY in .env file
        """
        import aiohttp

        if not self.google_places_api_key:
            print("Google Places API key not found. Using mock data instead.")
            return await self.generate_mock_data(search_query, max_results)

        contractors = []
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        page_num = 1
        next_page_token = None
        max_pages = 3  # Google Places API limit

        try:
            async with aiohttp.ClientSession() as session:
                while page_num <= max_pages and len(contractors) < max_results:
                    # Build params for this page
                    params = {
                        "key": self.google_places_api_key
                    }

                    if page_num == 1:
                        params["query"] = f"{search_query} {location}"
                    else:
                        params["pagetoken"] = next_page_token

                    print(f"Fetching page {page_num} from Google Places API...")

                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            results = data.get('results', [])

                            if not results:
                                print(f"No more results on page {page_num}")
                                break

                            print(f"Page {page_num}: Found {len(results)} results")

                            # Process results from this page
                            for place in results:
                                if len(contractors) >= max_results:
                                    break

                                contractor = {
                                    'company_name': place.get('name'),
                                    'address': place.get('formatted_address'),
                                    'google_rating': place.get('rating'),
                                    'review_count': place.get('user_ratings_total'),
                                    'source': 'google_places_api',
                                    'enrichment_status': 'pending',
                                    'state': 'FL'
                                }

                                # Extract city from address
                                if contractor['address']:
                                    city_match = re.search(
                                        r',\s*([A-Za-z\s]+),\s*FL',
                                        contractor['address']
                                    )
                                    if city_match:
                                        contractor['city'] = city_match.group(1).strip()

                                # Get additional details if place_id available
                                if place.get('place_id'):
                                    details = await self.get_place_details(
                                        session,
                                        place['place_id']
                                    )
                                    contractor.update(details)

                                contractors.append(contractor)

                                # Rate limiting between details requests
                                await asyncio.sleep(0.5)

                            # Check for next page token
                            next_page_token = data.get('next_page_token')

                            if next_page_token and len(contractors) < max_results:
                                # Google requires a short delay before using next_page_token
                                print(f"Waiting 2 seconds before fetching next page...")
                                await asyncio.sleep(2)
                                page_num += 1
                            else:
                                break
                        else:
                            print(f"Google Places API error: {response.status}")
                            if page_num == 1:  # Only fallback to mock data if first page fails
                                return await self.generate_mock_data(search_query, max_results)
                            break

        except Exception as e:
            print(f"Error calling Google Places API: {e}")
            if page_num == 1:  # Only fallback to mock data if no results yet
                return await self.generate_mock_data(search_query, max_results)

        print(f"Total contractors fetched: {len(contractors)} from {page_num} page(s)")
        return contractors

    async def get_place_details(
        self,
        session,
        place_id: str
    ) -> Dict:
        """Get detailed information for a specific place"""
        details = {}
        url = "https://maps.googleapis.com/maps/api/place/details/json"

        try:
            params = {
                "place_id": place_id,
                "fields": "formatted_phone_number,website,business_status",
                "key": self.google_places_api_key
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get('result', {})

                    details['phone'] = result.get('formatted_phone_number')
                    details['website'] = result.get('website')

        except Exception as e:
            print(f"Error getting place details: {e}")

        return details

    async def generate_mock_data(
        self,
        search_query: str,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Generate realistic mock contractor data for testing
        This simulates what would be returned from a real search
        """
        # Extract business type from query
        business_type = "Contractor"
        if "bathroom" in search_query.lower():
            business_type = "Bathroom Remodeling"
        elif "kitchen" in search_query.lower():
            business_type = "Kitchen Renovation"
        elif "builder" in search_query.lower():
            business_type = "Custom Home Builder"

        mock_contractors = [
            {
                'company_name': f'Jacksonville Premium {business_type}',
                'contact_person': 'John Smith',
                'phone': '(904) 555-0101',
                'email': 'info@jpremium.com',
                'website': 'https://example.com/jpremium',
                'address': '1234 Kings Ave, Jacksonville, FL 32207',
                'city': 'Jacksonville',
                'state': 'FL',
                'zip': '32207',
                'google_rating': 4.8,
                'review_count': 127,
                'specializations': f'{business_type}, Full Home Remodeling',
                'company_type': 'residential',
                'source': 'mock_data',
                'enrichment_status': 'pending'
            },
            {
                'company_name': f'Elite {business_type} Solutions',
                'contact_person': 'Sarah Johnson',
                'phone': '(904) 555-0102',
                'email': 'contact@elitesolutions.com',
                'website': 'https://example.com/elite',
                'address': '5678 Beach Blvd, Jacksonville Beach, FL 32250',
                'city': 'Jacksonville Beach',
                'state': 'FL',
                'zip': '32250',
                'google_rating': 4.9,
                'review_count': 203,
                'specializations': f'{business_type}, Custom Design',
                'company_type': 'both',
                'source': 'mock_data',
                'enrichment_status': 'pending'
            },
            {
                'company_name': f'Atlantic Coast {business_type}',
                'contact_person': 'Mike Davis',
                'phone': '(904) 555-0103',
                'email': 'mike@atlanticcoast.com',
                'website': 'https://example.com/atlantic',
                'address': '9012 Atlantic Blvd, Jacksonville, FL 32225',
                'city': 'Jacksonville',
                'state': 'FL',
                'zip': '32225',
                'google_rating': 4.6,
                'review_count': 89,
                'specializations': f'{business_type}, Commercial Projects',
                'company_type': 'commercial',
                'source': 'mock_data',
                'enrichment_status': 'pending'
            },
            {
                'company_name': f'Heritage {business_type} & Design',
                'contact_person': 'Lisa Martinez',
                'phone': '(904) 555-0104',
                'email': 'info@heritagedesign.com',
                'website': 'https://example.com/heritage',
                'address': '3456 Southside Blvd, Jacksonville, FL 32216',
                'city': 'Jacksonville',
                'state': 'FL',
                'zip': '32216',
                'google_rating': 4.7,
                'review_count': 156,
                'specializations': f'{business_type}, Historic Preservation',
                'company_type': 'residential',
                'source': 'mock_data',
                'enrichment_status': 'pending'
            },
            {
                'company_name': f'First Coast {business_type} Pros',
                'contact_person': 'David Wilson',
                'phone': '(904) 555-0105',
                'website': 'https://example.com/firstcoast',
                'address': '7890 San Jose Blvd, Jacksonville, FL 32217',
                'city': 'Jacksonville',
                'state': 'FL',
                'zip': '32217',
                'google_rating': 4.5,
                'review_count': 74,
                'specializations': f'{business_type}, Emergency Repairs',
                'company_type': 'residential',
                'source': 'mock_data',
                'enrichment_status': 'pending'
            }
        ]

        # Return limited number of results
        return mock_contractors[:min(max_results, len(mock_contractors))]

    def check_duplicate(self, contractor_data: Dict) -> bool:
        """
        Check if contractor already exists in database

        Returns:
            True if duplicate found, False otherwise
        """
        company_name = contractor_data.get('company_name', '')
        phone = contractor_data.get('phone', '')

        if not company_name:
            return False

        # Search by company name
        existing = self.db.search_contractors(search_term=company_name)

        if existing:
            # Check for exact or close matches
            for contractor in existing:
                # Exact company name match
                if contractor['company_name'].lower() == company_name.lower():
                    return True

                # Phone number match
                if phone and contractor.get('phone') == phone:
                    return True

        return False

    async def discover_contractors(
        self,
        search_query: str,
        max_results: int = 20,
        save_to_db: bool = True
    ) -> Dict:
        """
        Main method: Discover contractors and optionally save to database
        Now with smart duplicate filtering - only new contractors are shown/saved

        Args:
            search_query: Search term for contractors
            max_results: Maximum number of NEW (non-duplicate) results desired
            save_to_db: Whether to save results to database

        Returns:
            Dict with results summary including only NEW contractors
        """
        results = {
            'total_found': 0,  # Total results from Google
            'saved': 0,  # Successfully saved new contractors
            'duplicates': 0,  # Duplicates filtered out
            'errors': 0,  # Errors during save
            'contractors': [],  # Only NEW contractors (for display)
            'pages_fetched': 0
        }

        try:
            # Fetch more results than needed to account for duplicates
            # Google allows up to 60 results (3 pages)
            fetch_limit = min(max_results + 20, 60)  # Fetch extra to compensate for duplicates

            # Search for contractors (uses Google Places API or mock data)
            all_contractors = await self.search_google_places(search_query, max_results=fetch_limit)
            results['total_found'] = len(all_contractors)

            # Filter out duplicates BEFORE displaying/saving
            new_contractors = []
            duplicates_found = 0

            for contractor in all_contractors:
                if self.check_duplicate(contractor):
                    duplicates_found += 1
                    print(f"⏭️  Duplicate skipped: {contractor.get('company_name')}")
                else:
                    new_contractors.append(contractor)

                    # Stop if we have enough new contractors
                    if len(new_contractors) >= max_results:
                        break

            results['duplicates'] = duplicates_found
            results['contractors'] = new_contractors  # Only new contractors for display

            print(f"\n📊 Search Results: {len(all_contractors)} total, {len(new_contractors)} new, {duplicates_found} duplicates")

            # Save new contractors to database
            if save_to_db:
                for contractor in new_contractors:
                    try:
                        saved = self.db.insert_contractor(contractor)
                        if saved:
                            results['saved'] += 1
                            print(f"✅ Saved: {contractor.get('company_name')}")
                        else:
                            results['errors'] += 1
                    except Exception as e:
                        print(f"❌ Error saving contractor: {e}")
                        results['errors'] += 1

                    # Rate limiting
                    await asyncio.sleep(self.rate_limit_delay)

        except Exception as e:
            print(f"Error in discover_contractors: {e}")
            results['errors'] += 1

        return results

    async def bulk_discover(
        self,
        search_queries: List[str],
        max_results_per_query: int = 20
    ) -> Dict:
        """
        Run multiple search queries in sequence

        Args:
            search_queries: List of search terms
            max_results_per_query: Max results per query

        Returns:
            Combined results summary
        """
        all_results = {
            'total_found': 0,
            'saved': 0,
            'duplicates': 0,
            'errors': 0,
            'by_query': {}
        }

        for query in search_queries:
            print(f"Searching: {query}")

            result = await self.discover_contractors(
                query,
                max_results=max_results_per_query,
                save_to_db=True
            )

            all_results['total_found'] += result['total_found']
            all_results['saved'] += result['saved']
            all_results['duplicates'] += result['duplicates']
            all_results['errors'] += result['errors']
            all_results['by_query'][query] = result

            # Rate limiting between queries
            await asyncio.sleep(self.rate_limit_delay)

        return all_results


# Utility function to run scraper from sync context
def run_scraper(search_query: str, max_results: int = 20, db: Database = None):
    """
    Synchronous wrapper for running the async scraper
    Useful for Streamlit integration
    """
    if db is None:
        db = Database()

    scraper = ContractorScraper(db)

    # Run async function in event loop
    return asyncio.run(
        scraper.discover_contractors(search_query, max_results, save_to_db=True)
    )
