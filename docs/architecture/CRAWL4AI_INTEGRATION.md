# Crawl4AI Multi-Source Integration Plan

**Created**: October 27, 2025
**Status**: Design Phase - Ready for Implementation
**Goal**: Integrate Crawl4AI to supplement Google Places API with faster, multi-source contractor discovery

---

## Executive Summary

### The Problem
- **Google Places API is slow** due to rate limiting and regulations
- **Limited to one source**: Only Google Maps data
- **Cost concerns**: After free tier, costs add up quickly
- **Speed bottleneck**: Can't scale contractor discovery efficiently

### The Solution
**Parallel Multi-Source Discovery**: Run Google Places API AND Crawl4AI scrapers simultaneously

**Benefits**:
- 🚀 **2-3x faster**: 150-200 contractors in ~6-8 seconds (vs 60 in ~5 seconds)
- 💰 **Lower costs**: Reduce Google API calls by 50-70%
- 🎯 **Better coverage**: Access Houzz, Yelp, HomeAdvisor, Thumbtack, BBB
- 🔒 **Reliability**: Multiple sources means no single point of failure
- ✅ **Quality**: Cross-reference data for accuracy

---

## Architecture Overview

### Current (Google Only)
```
User Search → Google Places API → 60 contractors → Database
              (5 seconds, rate limited)
```

### New (Multi-Source Parallel)
```
User Search → ┌─ Google Places API (60 contractors) ─┐
              ├─ Houzz Scraper (50 contractors) ─────┤
              ├─ Yelp Scraper (50 contractors) ──────┤ → Merger → 150+ contractors → Database
              └─ HomeAdvisor Scraper (40 contractors)┘   (dedupe)   (6-8 seconds)

              (All run in parallel using asyncio)
```

---

## Prerequisites

### Python Upgrade Required

**Current**: Python 3.9.6
**Required**: Python 3.10+ or 3.11
**Reason**: Crawl4AI requires modern async features

#### Recommended: Use `uv` (Fastest Method)
```bash
# 1. Install uv tool
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install Python 3.10
uv python install 3.10

# 3. Navigate to project
cd /Users/ryankellum/claude-proj/islandGlassLeads

# 4. Create new virtual environment with Python 3.10
uv venv --python 3.10

# 5. Activate environment
source .venv/bin/activate

# 6. Reinstall all existing dependencies
uv pip install -r requirements.txt

# 7. Add Crawl4AI and new dependencies
uv pip install crawl4ai beautifulsoup4 lxml

# 8. Test existing app still works
python dash_app.py
```

#### Alternative Methods
**Option 1: Homebrew (macOS)**
```bash
brew install python@3.10
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install crawl4ai beautifulsoup4 lxml
```

**Option 2: Python.org**
1. Download Python 3.10 from https://www.python.org/downloads/macos/
2. Install via installer
3. Create new venv: `python3.10 -m venv .venv`
4. Activate and reinstall dependencies

---

## Dependencies

### Add to `requirements.txt`
```txt
# Multi-source scraping
crawl4ai>=0.7.0
beautifulsoup4>=4.12.0
lxml>=4.9.0

# Already have (keep versions):
aiohttp>=3.9.0
asyncio  # Built-in
```

### Install Command
```bash
pip install crawl4ai beautifulsoup4 lxml
```

---

## File Structure

### New Directory: `modules/scrapers/`
```
islandGlassLeads/
├── modules/
│   ├── scraper.py              # UPDATED: Main orchestrator
│   ├── enrichment.py           # Existing (no changes)
│   ├── outreach.py             # Existing (no changes)
│   ├── database.py             # Existing (no changes)
│   │
│   └── scrapers/               # ✨ NEW DIRECTORY
│       ├── __init__.py         # Package init
│       ├── base.py             # Abstract base scraper class
│       ├── merger.py           # Deduplication and merging logic
│       │
│       ├── google_places.py   # Refactored from scraper.py
│       ├── houzz.py            # NEW: Houzz scraper
│       ├── yelp.py             # NEW: Yelp scraper
│       ├── homeadvisor.py      # NEW: HomeAdvisor scraper
│       └── thumbtack.py        # NEW: Thumbtack scraper (optional)
```

---

## Implementation Details

### 1. Base Scraper Class (`modules/scrapers/base.py`)

**Purpose**: Define common interface for all scrapers

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class BaseScraper(ABC):
    """Abstract base class for all contractor scrapers"""

    def __init__(self):
        self.source_name = self.get_source_name()

    @abstractmethod
    async def search(self, query: str, location: str, limit: int = 50) -> List[Dict]:
        """
        Search for contractors

        Args:
            query: Search query (e.g., "bathroom remodeling")
            location: Location string (e.g., "Jacksonville, FL")
            limit: Maximum number of results

        Returns:
            List of contractor dictionaries in standard format
        """
        pass

    @abstractmethod
    def normalize_contractor(self, raw_data: Dict) -> Dict:
        """
        Normalize contractor data to standard format

        Standard format:
        {
            "company_name": str,
            "phone": str,
            "email": str or None,
            "website": str or None,
            "address": str or None,
            "city": str,
            "state": str,
            "google_rating": float or None,
            "google_reviews": int or None,
            "source": str (e.g., "houzz", "yelp")
        }
        """
        pass

    def get_source_name(self) -> str:
        """Return the name of this source"""
        return self.__class__.__name__.replace('Scraper', '').lower()

    async def test_connection(self) -> bool:
        """Test if this scraper can connect to its source"""
        try:
            results = await self.search("test", "New York, NY", limit=1)
            return len(results) > 0
        except Exception as e:
            print(f"Connection test failed for {self.source_name}: {e}")
            return False
```

---

### 2. Google Places Scraper (`modules/scrapers/google_places.py`)

**Purpose**: Refactor existing Google Places code into new architecture

```python
import os
import requests
from typing import List, Dict
from .base import BaseScraper

class GooglePlacesScraper(BaseScraper):
    """Scraper for Google Places API"""

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        self.base_url = "https://maps.googleapis.com/maps/api/place"

    async def search(self, query: str, location: str, limit: int = 60) -> List[Dict]:
        """Search Google Places API"""
        if not self.api_key:
            print("Google Places API key not found, skipping...")
            return []

        # Use existing logic from modules/scraper.py
        # (Move existing code here)
        search_text = f"{query} {location}"
        contractors = []

        # Text Search API call
        url = f"{self.base_url}/textsearch/json"
        params = {
            "query": search_text,
            "key": self.api_key
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Google API error: {response.status_code}")
            return []

        data = response.json()
        results = data.get("results", [])

        for place in results[:limit]:
            contractor = self.normalize_contractor(place)
            contractors.append(contractor)

        return contractors

    def normalize_contractor(self, raw_data: Dict) -> Dict:
        """Normalize Google Places data to standard format"""
        return {
            "company_name": raw_data.get("name"),
            "phone": raw_data.get("formatted_phone_number"),
            "email": None,  # Google doesn't provide emails
            "website": raw_data.get("website"),
            "address": raw_data.get("formatted_address"),
            "city": self._extract_city(raw_data),
            "state": self._extract_state(raw_data),
            "google_rating": raw_data.get("rating"),
            "google_reviews": raw_data.get("user_ratings_total"),
            "google_place_id": raw_data.get("place_id"),
            "source": "google_places"
        }

    def _extract_city(self, place_data: Dict) -> str:
        """Extract city from address components"""
        for component in place_data.get("address_components", []):
            if "locality" in component.get("types", []):
                return component.get("long_name")
        return ""

    def _extract_state(self, place_data: Dict) -> str:
        """Extract state from address components"""
        for component in place_data.get("address_components", []):
            if "administrative_area_level_1" in component.get("types", []):
                return component.get("short_name")
        return ""
```

---

### 3. Houzz Scraper (`modules/scrapers/houzz.py`)

**Purpose**: Scrape contractor data from Houzz.com

```python
import asyncio
from typing import List, Dict
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
from .base import BaseScraper

class HouzzScraper(BaseScraper):
    """Scraper for Houzz.com contractor directory"""

    async def search(self, query: str, location: str, limit: int = 50) -> List[Dict]:
        """Search Houzz for contractors"""
        contractors = []

        # Clean location for URL
        location_slug = location.lower().replace(", ", "-").replace(" ", "-")
        query_slug = query.lower().replace(" ", "-")

        # Build Houzz search URL
        # Example: https://www.houzz.com/professionals/bathroom-remodeler/jacksonville-fl-us-prof
        search_url = f"https://www.houzz.com/professionals/{query_slug}/{location_slug}-us-prof"

        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                # Run crawler
                result = await crawler.arun(
                    url=search_url,
                    # Scroll page to trigger lazy loading
                    js_code=[
                        "window.scrollTo(0, document.body.scrollHeight);",
                        "await new Promise(r => setTimeout(r, 1000));"  # Wait for load
                    ],
                    wait_for="css:.hz-pro-search-result",  # Wait for results
                    bypass_cache=True
                )

                if not result.success:
                    print(f"Houzz scrape failed: {result.error_message}")
                    return []

                # Parse HTML with BeautifulSoup
                soup = BeautifulSoup(result.html, 'lxml')

                # Find contractor cards (adjust selectors based on actual HTML)
                contractor_cards = soup.select('.hz-pro-search-result')[:limit]

                for card in contractor_cards:
                    try:
                        contractor = self._parse_contractor_card(card)
                        if contractor:
                            contractors.append(contractor)
                    except Exception as e:
                        print(f"Error parsing Houzz card: {e}")
                        continue

        except Exception as e:
            print(f"Houzz scraper error: {e}")

        return contractors

    def _parse_contractor_card(self, card) -> Dict:
        """Parse individual contractor card from Houzz"""
        # Extract data from HTML elements
        name_elem = card.select_one('.pro-name')
        phone_elem = card.select_one('.pro-phone')
        location_elem = card.select_one('.pro-location')
        rating_elem = card.select_one('.pro-rating')
        reviews_elem = card.select_one('.pro-reviews-count')
        profile_link = card.select_one('a.pro-link')

        raw_data = {
            "business_name": name_elem.text.strip() if name_elem else None,
            "phone": phone_elem.text.strip() if phone_elem else None,
            "location": location_elem.text.strip() if location_elem else None,
            "rating": float(rating_elem.text.strip()) if rating_elem else None,
            "review_count": int(reviews_elem.text.strip()) if reviews_elem else None,
            "profile_url": "https://www.houzz.com" + profile_link['href'] if profile_link else None
        }

        return self.normalize_contractor(raw_data)

    def normalize_contractor(self, raw_data: Dict) -> Dict:
        """Normalize Houzz data to standard format"""
        # Parse city and state from location string
        location = raw_data.get("location", "")
        city, state = self._parse_location(location)

        return {
            "company_name": raw_data.get("business_name"),
            "phone": self._clean_phone(raw_data.get("phone")),
            "email": None,  # Houzz doesn't show emails in listings
            "website": raw_data.get("profile_url"),
            "address": None,  # Not in listing view
            "city": city,
            "state": state,
            "google_rating": raw_data.get("rating"),  # Use as generic rating
            "google_reviews": raw_data.get("review_count"),
            "source": "houzz"
        }

    def _parse_location(self, location_str: str) -> tuple:
        """Parse 'City, ST' into (city, state)"""
        parts = location_str.split(",")
        if len(parts) >= 2:
            return parts[0].strip(), parts[1].strip()
        return location_str, ""

    def _clean_phone(self, phone: str) -> str:
        """Clean phone number"""
        if not phone:
            return None
        # Remove formatting, keep digits
        import re
        return re.sub(r'\D', '', phone)
```

---

### 4. Yelp Scraper (`modules/scrapers/yelp.py`)

**Purpose**: Scrape contractor data from Yelp.com

```python
import asyncio
from typing import List, Dict
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
from .base import BaseScraper

class YelpScraper(BaseScraper):
    """Scraper for Yelp.com business directory"""

    async def search(self, query: str, location: str, limit: int = 50) -> List[Dict]:
        """Search Yelp for contractors"""
        contractors = []

        # Build Yelp search URL
        # Example: https://www.yelp.com/search?find_desc=bathroom+remodeling&find_loc=Jacksonville,+FL
        search_url = f"https://www.yelp.com/search"
        search_params = f"?find_desc={query.replace(' ', '+')}&find_loc={location.replace(' ', '+')}"
        full_url = search_url + search_params

        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(
                    url=full_url,
                    js_code="window.scrollTo(0, document.body.scrollHeight);",
                    wait_for="css:.businessName__09f24__EYSZE",
                    bypass_cache=True
                )

                if not result.success:
                    print(f"Yelp scrape failed: {result.error_message}")
                    return []

                # Parse with BeautifulSoup
                soup = BeautifulSoup(result.html, 'lxml')

                # Find business cards
                business_cards = soup.select('[data-testid="serp-ia-card"]')[:limit]

                for card in business_cards:
                    try:
                        contractor = self._parse_business_card(card)
                        if contractor:
                            contractors.append(contractor)
                    except Exception as e:
                        print(f"Error parsing Yelp card: {e}")
                        continue

        except Exception as e:
            print(f"Yelp scraper error: {e}")

        return contractors

    def _parse_business_card(self, card) -> Dict:
        """Parse individual business card from Yelp"""
        name_elem = card.select_one('.businessName__09f24__EYSZE')
        rating_elem = card.select_one('[aria-label*="star rating"]')
        review_count_elem = card.select_one('.reviewCount__09f24__EUXPN')
        phone_elem = card.select_one('.secondaryAttributes__09f24__lMNZN')
        address_elem = card.select_one('address')

        raw_data = {
            "business_name": name_elem.text.strip() if name_elem else None,
            "rating": self._extract_rating(rating_elem),
            "review_count": self._extract_review_count(review_count_elem),
            "phone": phone_elem.text.strip() if phone_elem else None,
            "address": address_elem.text.strip() if address_elem else None,
        }

        return self.normalize_contractor(raw_data)

    def _extract_rating(self, elem) -> float:
        """Extract rating from aria-label"""
        if not elem:
            return None
        label = elem.get('aria-label', '')
        # Parse "4.5 star rating" → 4.5
        import re
        match = re.search(r'([\d.]+)\s*star', label)
        return float(match.group(1)) if match else None

    def _extract_review_count(self, elem) -> int:
        """Extract review count"""
        if not elem:
            return None
        text = elem.text.strip()
        # Parse "123 reviews" → 123
        import re
        match = re.search(r'(\d+)', text)
        return int(match.group(1)) if match else None

    def normalize_contractor(self, raw_data: Dict) -> Dict:
        """Normalize Yelp data to standard format"""
        # Parse address for city/state
        address = raw_data.get("address", "")
        city, state = self._parse_address(address)

        return {
            "company_name": raw_data.get("business_name"),
            "phone": raw_data.get("phone"),
            "email": None,
            "website": None,  # Would need to visit detail page
            "address": address,
            "city": city,
            "state": state,
            "google_rating": raw_data.get("rating"),
            "google_reviews": raw_data.get("review_count"),
            "source": "yelp"
        }

    def _parse_address(self, address: str) -> tuple:
        """Extract city and state from address"""
        # Simple parsing - may need refinement
        parts = address.split(",")
        if len(parts) >= 2:
            city = parts[-2].strip()
            state_zip = parts[-1].strip().split()
            state = state_zip[0] if state_zip else ""
            return city, state
        return "", ""
```

---

### 5. Merger & Deduplication (`modules/scrapers/merger.py`)

**Purpose**: Combine and deduplicate contractors from multiple sources

```python
from typing import List, Dict
import re
from difflib import SequenceMatcher

class ContractorMerger:
    """Deduplicate and merge contractors from multiple sources"""

    def merge_contractors(self, contractors: List[Dict]) -> List[Dict]:
        """
        Merge contractors by phone number and name similarity

        Strategy:
        1. Group by normalized phone number (primary key)
        2. For contractors without phone, check name+city similarity
        3. Merge records intelligently, preferring best data from each source
        """
        merged = {}
        no_phone_contractors = []

        for contractor in contractors:
            phone = self._normalize_phone(contractor.get('phone', ''))

            if phone:
                # Use phone as key
                if phone in merged:
                    merged[phone] = self._merge_two_contractors(merged[phone], contractor)
                else:
                    merged[phone] = contractor
                    merged[phone]['sources'] = [contractor.get('source', 'unknown')]
            else:
                # No phone - check later for name similarity
                no_phone_contractors.append(contractor)

        # Handle contractors without phone numbers
        for contractor in no_phone_contractors:
            match_found = False

            for key, existing in merged.items():
                if self._is_same_contractor(existing, contractor):
                    merged[key] = self._merge_two_contractors(existing, contractor)
                    match_found = True
                    break

            if not match_found:
                # Add as new contractor
                unique_key = f"no_phone_{len(merged)}"
                merged[unique_key] = contractor
                merged[unique_key]['sources'] = [contractor.get('source', 'unknown')]

        return list(merged.values())

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone to digits only"""
        if not phone:
            return ""
        return re.sub(r'\D', '', phone)

    def _is_same_contractor(self, c1: Dict, c2: Dict, threshold: float = 0.85) -> bool:
        """Check if two contractors are the same based on name and location"""
        # Compare names
        name1 = (c1.get('company_name') or "").lower()
        name2 = (c2.get('company_name') or "").lower()

        if not name1 or not name2:
            return False

        name_similarity = SequenceMatcher(None, name1, name2).ratio()

        # Compare cities
        city1 = (c1.get('city') or "").lower()
        city2 = (c2.get('city') or "").lower()

        same_city = city1 == city2 if city1 and city2 else False

        # Match if name is very similar AND same city
        return name_similarity >= threshold and same_city

    def _merge_two_contractors(self, existing: Dict, new: Dict) -> Dict:
        """
        Merge two contractor records intelligently

        Strategy:
        - Prefer non-null values
        - For ratings: compute weighted average
        - For sources: combine into array
        - For specific fields: prefer Google data (most reliable)
        """
        merged = existing.copy()

        # Add new source
        if 'sources' not in merged:
            merged['sources'] = [existing.get('source', 'unknown')]

        new_source = new.get('source', 'unknown')
        if new_source not in merged['sources']:
            merged['sources'].append(new_source)

        # Merge fields with intelligent preferences
        for key, value in new.items():
            if key == 'sources' or key == 'source':
                continue  # Already handled

            # Prefer non-null values
            if value and not existing.get(key):
                merged[key] = value

            # For contact info, prefer Google data (most accurate)
            elif key in ['phone', 'address', 'email'] and new.get('source') == 'google_places':
                merged[key] = value

            # For website, prefer non-Google sources (Houzz has better profiles)
            elif key == 'website' and new.get('source') in ['houzz', 'homeadvisor']:
                merged[key] = value

        # Merge ratings (weighted average by review count)
        merged = self._merge_ratings(merged, existing, new)

        return merged

    def _merge_ratings(self, merged: Dict, existing: Dict, new: Dict) -> Dict:
        """Merge ratings using weighted average based on review count"""
        existing_rating = existing.get('google_rating')
        existing_reviews = existing.get('google_reviews') or 1

        new_rating = new.get('google_rating')
        new_reviews = new.get('google_reviews') or 1

        if existing_rating and new_rating:
            # Weighted average
            total_reviews = existing_reviews + new_reviews
            weighted_rating = (
                (existing_rating * existing_reviews) + (new_rating * new_reviews)
            ) / total_reviews

            merged['google_rating'] = round(weighted_rating, 2)
            merged['google_reviews'] = total_reviews

        return merged

    def get_merge_stats(self, original_count: int, merged_count: int) -> Dict:
        """Calculate merge statistics"""
        duplicates_removed = original_count - merged_count
        dedup_rate = (duplicates_removed / original_count * 100) if original_count > 0 else 0

        return {
            "original_count": original_count,
            "merged_count": merged_count,
            "duplicates_removed": duplicates_removed,
            "deduplication_rate": f"{dedup_rate:.1f}%"
        }
```

---

### 6. Main Orchestrator (`modules/scraper.py` - Updated)

**Purpose**: Coordinate parallel searches across all sources

```python
import asyncio
from typing import List, Dict, Optional
from modules.scrapers.google_places import GooglePlacesScraper
from modules.scrapers.houzz import HouzzScraper
from modules.scrapers.yelp import YelpScraper
from modules.scrapers.homeadvisor import HomeAdvisorScraper  # Optional
from modules.scrapers.merger import ContractorMerger

class MultiSourceScraper:
    """Orchestrate contractor searches across multiple sources in parallel"""

    def __init__(self):
        """Initialize all scrapers"""
        self.scrapers = {
            'google': GooglePlacesScraper(),
            'houzz': HouzzScraper(),
            'yelp': YelpScraper(),
            # 'homeadvisor': HomeAdvisorScraper(),  # Add when ready
        }
        self.merger = ContractorMerger()

    async def search_all_sources(
        self,
        query: str,
        location: str,
        sources: Optional[List[str]] = None,
        limit_per_source: int = 50
    ) -> Dict:
        """
        Search all enabled sources in parallel and merge results

        Args:
            query: Search query (e.g., "bathroom remodeling")
            location: Location (e.g., "Jacksonville, FL")
            sources: List of source names to use (default: all available)
            limit_per_source: Max results per source

        Returns:
            Dict with merged contractors and metadata
        """
        # Use all sources if not specified
        if sources is None:
            sources = list(self.scrapers.keys())

        print(f"Searching {len(sources)} sources in parallel: {sources}")
        start_time = asyncio.get_event_loop().time()

        # Create search tasks for each source
        tasks = []
        for source in sources:
            if source in self.scrapers:
                task = self.scrapers[source].search(query, location, limit_per_source)
                tasks.append((source, task))
            else:
                print(f"Warning: Unknown source '{source}', skipping...")

        # Execute all searches in parallel
        results = await asyncio.gather(
            *[task for _, task in tasks],
            return_exceptions=True
        )

        # Combine results
        all_contractors = []
        source_stats = {}

        for (source, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                print(f"❌ Error from {source}: {result}")
                source_stats[source] = {"count": 0, "error": str(result)}
                continue

            print(f"✅ {source}: {len(result)} contractors found")
            all_contractors.extend(result)
            source_stats[source] = {"count": len(result), "error": None}

        # Deduplicate and merge
        original_count = len(all_contractors)
        merged_contractors = self.merger.merge_contractors(all_contractors)

        end_time = asyncio.get_event_loop().time()
        duration = round(end_time - start_time, 2)

        # Calculate stats
        merge_stats = self.merger.get_merge_stats(original_count, len(merged_contractors))

        return {
            "contractors": merged_contractors,
            "stats": {
                "total_found": len(merged_contractors),
                "original_count": original_count,
                "duplicates_removed": merge_stats["duplicates_removed"],
                "deduplication_rate": merge_stats["deduplication_rate"],
                "duration_seconds": duration,
                "sources": source_stats
            }
        }

    async def search_single_source(
        self,
        source: str,
        query: str,
        location: str,
        limit: int = 50
    ) -> List[Dict]:
        """Search a single source"""
        if source not in self.scrapers:
            raise ValueError(f"Unknown source: {source}")

        return await self.scrapers[source].search(query, location, limit)


# Convenience function for backward compatibility
async def search_contractors(query: str, location: str, sources: List[str] = None) -> List[Dict]:
    """
    Search for contractors across multiple sources

    Usage:
        results = await search_contractors("bathroom remodeling", "Jacksonville, FL")
        contractors = results["contractors"]
    """
    scraper = MultiSourceScraper()
    return await scraper.search_all_sources(query, location, sources)
```

---

## Database Schema Updates

### SQL Migration Script

Create file: `add_multi_source_support.sql`

```sql
-- Add multi-source tracking to contractors table

-- Track which sources provided data for this contractor
ALTER TABLE contractors
ADD COLUMN IF NOT EXISTS sources TEXT[] DEFAULT '{}';

-- Store raw data from each source (for debugging/auditing)
ALTER TABLE contractors
ADD COLUMN IF NOT EXISTS source_data JSONB DEFAULT '{}';

-- Track when contractor was first discovered
ALTER TABLE contractors
ADD COLUMN IF NOT EXISTS discovery_date TIMESTAMP DEFAULT NOW();

-- Track when data was last verified/updated
ALTER TABLE contractors
ADD COLUMN IF NOT EXISTS last_verified TIMESTAMP;

-- Create index for faster source queries
CREATE INDEX IF NOT EXISTS idx_contractors_sources ON contractors USING GIN(sources);

-- Create index for discovery date
CREATE INDEX IF NOT EXISTS idx_contractors_discovery_date ON contractors(discovery_date DESC);

-- Add comment for documentation
COMMENT ON COLUMN contractors.sources IS 'Array of data sources: google_places, houzz, yelp, homeadvisor';
COMMENT ON COLUMN contractors.source_data IS 'Raw data from each source in JSON format';
```

### Apply Migration
```bash
# Via Supabase Dashboard:
# 1. Go to SQL Editor
# 2. Paste contents of add_multi_source_support.sql
# 3. Click "Run"
```

---

## UI Updates

### Discovery Page (`pages/discovery.py`)

Add source selector and result display:

```python
import dash_mantine_components as dmc
from dash import html, callback, Input, Output, State
import asyncio
from modules.scraper import MultiSourceScraper

# Source selector component
source_selector = dmc.MultiSelect(
    id="source-selector",
    label="Data Sources",
    description="Select which sources to search (more sources = more results)",
    placeholder="Select sources",
    data=[
        {"label": "🗺️ Google Places API", "value": "google"},
        {"label": "🏠 Houzz (Design Contractors)", "value": "houzz"},
        {"label": "⭐ Yelp (Local Businesses)", "value": "yelp"},
        {"label": "🔨 HomeAdvisor (Verified Pros)", "value": "homeadvisor"},
    ],
    value=["google", "houzz", "yelp"],  # Default: all except HomeAdvisor
    searchable=True,
    clearable=True,
)

# Search callback
@callback(
    Output("search-results", "children"),
    Output("search-stats", "children"),
    Input("search-button", "n_clicks"),
    State("query-input", "value"),
    State("location-input", "value"),
    State("source-selector", "value"),
    prevent_initial_call=True
)
def perform_search(n_clicks, query, location, sources):
    """Execute multi-source search"""
    if not query or not location:
        return [], "Please enter both query and location"

    # Run async search
    scraper = MultiSourceScraper()
    result = asyncio.run(
        scraper.search_all_sources(query, location, sources)
    )

    contractors = result["contractors"]
    stats = result["stats"]

    # Build results display
    result_cards = [
        create_contractor_card(c) for c in contractors
    ]

    # Build stats display
    stats_display = dmc.Group([
        dmc.Badge(f"{stats['total_found']} contractors", color="green", size="lg"),
        dmc.Badge(f"{stats['duplicates_removed']} duplicates removed", color="blue"),
        dmc.Badge(f"{stats['duration_seconds']}s", color="gray"),
    ])

    return result_cards, stats_display

def create_contractor_card(contractor):
    """Create card with source badges"""
    sources = contractor.get('sources', [])

    source_badges = dmc.Group([
        dmc.Badge(
            source.capitalize(),
            color="blue" if source == "google" else
                  "green" if source == "houzz" else
                  "red" if source == "yelp" else "gray",
            size="sm"
        )
        for source in sources
    ], spacing="xs")

    return dmc.Card([
        dmc.Text(contractor['company_name'], weight=500, size="lg"),
        source_badges,
        dmc.Text(contractor.get('phone', 'No phone'), size="sm"),
        # ... rest of card
    ])
```

---

## Testing Plan

### 1. Unit Tests (Each Scraper)

```python
# test_scrapers.py
import asyncio
import pytest
from modules.scrapers.houzz import HouzzScraper
from modules.scrapers.yelp import YelpScraper
from modules.scrapers.google_places import GooglePlacesScraper

@pytest.mark.asyncio
async def test_houzz_scraper():
    scraper = HouzzScraper()
    results = await scraper.search("bathroom remodeling", "Jacksonville, FL", limit=5)

    assert len(results) > 0
    assert all('source' in r for r in results)
    assert all(r['source'] == 'houzz' for r in results)

@pytest.mark.asyncio
async def test_yelp_scraper():
    scraper = YelpScraper()
    results = await scraper.search("contractors", "New York, NY", limit=5)

    assert len(results) > 0
    assert all('company_name' in r for r in results)

# Run: pytest test_scrapers.py
```

### 2. Integration Tests (Parallel Execution)

```python
# test_multi_source.py
import asyncio
from modules.scraper import MultiSourceScraper

async def test_parallel_search():
    scraper = MultiSourceScraper()
    result = await scraper.search_all_sources(
        "bathroom remodeling",
        "Jacksonville, FL",
        sources=["google", "houzz", "yelp"]
    )

    assert result["stats"]["total_found"] > 0
    print(f"Found {result['stats']['total_found']} contractors")
    print(f"Sources: {result['stats']['sources']}")
    print(f"Duplicates removed: {result['stats']['duplicates_removed']}")

asyncio.run(test_parallel_search())
```

### 3. Performance Tests

```python
# test_performance.py
import asyncio
import time
from modules.scraper import MultiSourceScraper

async def benchmark_search():
    scraper = MultiSourceScraper()

    # Test 1: Single source (Google)
    start = time.time()
    result1 = await scraper.search_single_source("google", "contractors", "Jacksonville, FL")
    google_time = time.time() - start

    # Test 2: All sources parallel
    start = time.time()
    result2 = await scraper.search_all_sources("contractors", "Jacksonville, FL")
    multi_time = time.time() - start

    print(f"Google only: {len(result1)} contractors in {google_time:.2f}s")
    print(f"All sources: {result2['stats']['total_found']} contractors in {multi_time:.2f}s")
    print(f"Speed improvement: {len(result2['contractors']) / google_time:.1f} contractors/second")

asyncio.run(benchmark_search())
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] Upgrade Python to 3.10+
- [ ] Install Crawl4AI and dependencies
- [ ] Test each scraper independently
- [ ] Test parallel execution
- [ ] Verify deduplication logic
- [ ] Update database schema
- [ ] Test with real searches
- [ ] Update UI with source selector
- [ ] Add error handling for failed sources

### Deployment
- [ ] Update requirements.txt
- [ ] Update Railway Python version
- [ ] Deploy to staging
- [ ] Test on staging with real API keys
- [ ] Monitor performance and errors
- [ ] Deploy to production
- [ ] Monitor API usage (Google vs Crawl4AI ratio)

### Post-Deployment
- [ ] Gather user feedback on speed
- [ ] Analyze source quality (which sources provide best leads)
- [ ] Optimize scraper selectors if needed
- [ ] Add more sources if valuable

---

## Expected Results

### Performance Improvements
| Metric | Current (Google Only) | With Crawl4AI | Improvement |
|--------|----------------------|---------------|-------------|
| **Contractors per search** | 60 | 150-200 | 2.5-3.3x |
| **Time per search** | ~5 seconds | ~6-8 seconds | Similar |
| **Contractors per second** | 12/sec | 20-30/sec | 2-2.5x |
| **Google API calls** | 100% | 30-50% | 50-70% reduction |
| **Monthly cost** (1000 contractors) | ~$20 | ~$6-10 | 50-70% savings |

### Quality Improvements
- **Houzz contractors**: Higher-end, design-focused (better for custom glass work)
- **Yelp contractors**: Local, verified reviews (better trust signals)
- **Cross-referenced data**: More accurate through validation
- **Backup reliability**: If one source is down, others continue

---

## Maintenance & Monitoring

### Things to Watch
1. **Scraper breakage**: Websites change HTML structure
2. **Rate limiting**: Be respectful to scraped sites
3. **Data quality**: Monitor which sources provide best leads
4. **Performance**: Track search times and optimization needs

### Update Schedule
- **Weekly**: Check scrapers still working
- **Monthly**: Analyze source quality and ROI
- **Quarterly**: Update selectors if sites changed
- **Yearly**: Add new sources if valuable

---

## Next Steps

1. **Immediate** (this session):
   - Review and approve this plan
   - Decide on Python upgrade method

2. **Next session**:
   - Upgrade Python to 3.10
   - Install Crawl4AI
   - Test basic scraping

3. **Following sessions**:
   - Build Houzz scraper
   - Build Yelp scraper
   - Implement merger
   - Update UI
   - Deploy

**Estimated total time**: 10-15 hours over 3-4 sessions

---

**Ready to proceed?** Let me know if you want to start with the Python upgrade or if you have questions about any part of this plan!
