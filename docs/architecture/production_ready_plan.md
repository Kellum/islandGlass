# Production-Ready Contractor Discovery Plan

**Last Updated**: October 16, 2025
**Current Status**: App is feature-complete, using mock data for contractor discovery

---

## Current State Analysis

### What's Working
- ✅ All 8 pages functional (Dashboard, Discovery, Enrichment, Directory, Detail, Bulk Actions, Import, Settings)
- ✅ Claude AI enrichment (website analysis + lead scoring)
- ✅ Personalized outreach generation (emails + call scripts)
- ✅ Token tracking and cost monitoring
- ✅ CSV export/import
- ✅ Database: Supabase PostgreSQL

### What Needs Production Setup
- ⚠️ **Contractor Discovery**: Currently using mock data (5 fake contractors)
- ⚠️ **Python Version**: 3.9.6 (limits some options)
- ⚠️ **No Google API Key**: Code exists but needs activation

---

## Production-Ready Options

### Option 1: Google Places API ⭐ RECOMMENDED FOR QUICK START

**What it is**: Official Google API for finding businesses on Google Maps

**Pros**:
- ✅ Already coded in `modules/scraper.py` - just needs API key
- ✅ No code changes needed
- ✅ No Python upgrade required
- ✅ Most reliable and accurate data
- ✅ Free tier: 10,000 searches/month (sufficient for testing)
- ✅ Returns: company name, address, phone, website, ratings, reviews

**Cons**:
- ❌ Costs after free tier: $0.02/request ($20 per 1,000 requests)
- ❌ Limited to Google Maps data only (but that's usually enough)

**Cost Breakdown** (after free tier):
- 100 contractors: $2.00
- 500 contractors: $10.00
- 1,000 contractors: $20.00
- 5,000 contractors: $100.00

**New Pricing (March 1, 2025)**:
- Essentials tier: 10,000 free calls/month
- After free tier: $0.02 per Place Details request

**Setup Steps**:
1. Go to https://console.cloud.google.com/google/maps-apis/start
2. Create new project or select existing
3. Enable APIs:
   - Places API (New)
   - Places API
4. Create API credentials (API key)
5. Restrict key to Places API only (security)
6. Add to `.env` file:
   ```
   GOOGLE_PLACES_API_KEY=your-key-here
   ```
7. Restart Streamlit app
8. App automatically switches from mock data to real Google data

**No Code Changes Required** - the scraper already has this logic built in!

---

### Option 2: Upgrade Python + crawl4ai 🚀 MOST POWERFUL

**What it is**: AI-friendly web scraper that can crawl ANY contractor directory website

**Capabilities**:
- Extract contractor data from multiple sources:
  - **Houzz** (design-focused contractors, high-end projects)
  - **Yelp** (local businesses with reviews and ratings)
  - **HomeAdvisor/Angi** (contractor directories with verified pros)
  - **BBB** (Better Business Bureau - accredited businesses)
  - **Thumbtack** (local service professionals)
  - **Porch** (home improvement contractors)
- LLM-ready markdown output (perfect for Claude analysis)
- JavaScript execution (handles dynamic content)
- Deep crawling (multi-page navigation)
- 6x faster performance than traditional scrapers
- Completely free and open source

**Pros**:
- ✅ Multiple data sources = more contractors
- ✅ Cross-reference data for accuracy
- ✅ Free (no API costs)
- ✅ Flexible - scrape any site
- ✅ Active development and community support

**Cons**:
- ❌ Requires Python 3.10 or 3.11 (currently on 3.9.6)
- ❌ More complex setup
- ❌ Need custom scraping logic per site
- ❌ May violate some sites' Terms of Service (check robots.txt)
- ❌ Sites may block scrapers or change structure

**Python Upgrade Process** (using `uv` tool - fastest method):
```bash
# Install uv tool
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python 3.10 (or 3.11)
uv python install 3.10

# Update project to use new Python
cd /Users/ryankellum/claude-proj/islandGlassLeads
uv venv --python 3.10
source .venv/bin/activate

# Reinstall all dependencies
uv pip install -r requirements.txt

# Add crawl4ai
uv pip install crawl4ai
```

**Alternative Upgrade Methods**:
- Download from Python.org (https://www.python.org/downloads/macos/)
- Use Homebrew: `brew install python@3.10`
- Use pyenv: `pyenv install 3.10.x`

**Implementation Steps After Upgrade**:

1. **Add crawl4ai to requirements.txt**:
   ```
   crawl4ai>=0.7.0
   ```

2. **Create new scraper modules** (examples):

   **Houzz Scraper** (`modules/scrapers/houzz.py`):
   - Search: "bathroom remodeling Jacksonville FL"
   - Extract: company name, location, portfolio images, reviews
   - Target pages: Professional directory, project galleries

   **Yelp Scraper** (`modules/scrapers/yelp.py`):
   - Search: "contractors Jacksonville FL"
   - Extract: business name, phone, address, rating, review count
   - Target pages: Business listings, detailed pages

   **HomeAdvisor Scraper** (`modules/scrapers/homeadvisor.py`):
   - Search: "bathroom contractors Jacksonville"
   - Extract: pro name, services, location, certifications
   - Target pages: Pro directory, pro profiles

3. **Update UI** - Add source selector in Discovery page:
   ```python
   source = st.selectbox(
       "Data Source",
       ["Google Places API", "Houzz", "Yelp", "HomeAdvisor", "All Sources"]
   )
   ```

4. **Implement merge logic** - Deduplicate contractors from multiple sources by:
   - Phone number (primary key)
   - Company name similarity (fuzzy matching)
   - Address matching

**crawl4ai Features to Leverage**:
- **Chunking strategies**: Topic-based, regex, sentence-based
- **Media extraction**: Images from contractor portfolios
- **Table extraction**: Extract service pricing tables
- **Session management**: Handle login-required sites
- **Proxy support**: Rotate IPs to avoid blocks

---

### Option 3: Cheaper Google Alternatives 💰 COST-EFFECTIVE

Use alternative location/places APIs with lower costs:

#### Radar API
- **Free tier**: 100,000 requests/month
- **Paid**: $0.50 per 1,000 (25x cheaper than Google)
- **Website**: https://radar.com/
- **API**: Similar to Google Places

#### Mapbox Places API
- **Free tier**: 100,000 requests/month
- **Paid**: $0.75 per 1,000
- **Website**: https://www.mapbox.com/
- **API**: Search for places, geocoding

#### TomTom Search API
- **Pricing**: $0.50 per 1,000 (40x cheaper than Google)
- **Website**: https://developer.tomtom.com/
- **API**: Place search, POI categories

#### OpenStreetMap (Nominatim)
- **Pricing**: Completely free
- **Limits**: Fair usage policy (max 1 request/second)
- **Website**: https://nominatim.org/
- **Note**: Less business data than Google

**Implementation**:
- Create new scraper method for chosen API
- Swap API endpoint and parameters
- Keep existing code structure

---

### Option 4: Hybrid Approach 🎯 RECOMMENDED - BEST OF ALL WORLDS

**⭐ NEW RECOMMENDATION**: Use both Google Places AND Crawl4AI together for maximum speed and coverage!

Combine multiple sources for maximum contractor coverage and faster results:

**Phase 1: Dual Primary Sources (PARALLEL)**
- **Google Places API**: Reliable, structured data (when available)
- **Crawl4AI Sources**: Faster, no rate limits, multiple platforms
  - Houzz (design contractors, high-end residential)
  - Yelp (local businesses with reviews)
  - HomeAdvisor/Angi (verified contractors)
  - Thumbtack (service professionals)
  - BBB (accredited businesses)

**Phase 2: Manual Additions**
- CSV import (already built)
- Manual entry form (already built)

**Why This Solves Your Speed Concerns**:
- ✅ **Parallel discovery**: Run Google AND Crawl4AI at same time
- ✅ **No single point of failure**: If Google is slow, Crawl4AI continues
- ✅ **Rate limit immunity**: Crawl4AI has no API limits like Google
- ✅ **More sources = faster results**: Get 20 contractors from Google + 30 from Houzz + 25 from Yelp = 75 total in same time Google alone gives you 20
- ✅ **Regional flexibility**: Some areas have better data on Yelp vs Google

**Benefits**:
- ✅ Maximum contractor coverage (100-200+ per search vs 60 from Google alone)
- ✅ **SPEED**: Parallel execution means faster results
- ✅ Cross-reference data for accuracy
- ✅ Backup if one source fails or is slow
- ✅ Diverse contractor types (residential, commercial, design-focused)
- ✅ Free discovery (no Google API costs for Crawl4AI portion)

**Data Merging Strategy**:
1. **Parallel search execution**: Launch all sources simultaneously
2. **Real-time deduplication**: Merge as results arrive
3. Use phone number as primary key for matching
4. Merge records with same phone or similar name+address
5. Prefer Google data for contact info (most accurate)
6. Prefer Houzz data for portfolio/design work
7. Combine reviews from all sources (weighted average)
8. Tag with multiple sources in database

**Database Schema Addition**:
```sql
-- Track multiple data sources per contractor
ALTER TABLE contractors ADD COLUMN sources TEXT[]; -- Array: ['google_places', 'houzz', 'yelp']
ALTER TABLE contractors ADD COLUMN source_data JSONB; -- Store raw data from each source
ALTER TABLE contractors ADD COLUMN last_updated_source TEXT; -- Which source last updated
ALTER TABLE contractors ADD COLUMN discovery_date TIMESTAMP; -- When first discovered
ALTER TABLE contractors ADD COLUMN last_verified TIMESTAMP; -- Last time data was verified
```

**Performance Optimization**:
- Run searches in parallel using asyncio
- Cache Crawl4AI results for 24 hours
- Use connection pooling for faster HTTP requests
- Implement smart retry logic for failed sources

---

## Recommended Implementation Path

### Phase 1: Quick Start (This Week)
**Goal**: Get real contractor data flowing immediately

1. **Get Google Places API key** (15 minutes)
   - Set up Google Cloud project
   - Enable Places APIs
   - Create API key
   - Add to `.env` file

2. **Test with real data** (5 minutes)
   - Run search: "bathroom remodeling Jacksonville FL"
   - Verify 20 real contractors appear
   - Check data quality (phone, website, ratings)

3. **Enrich 10 contractors** (10 minutes)
   - Run enrichment on contractors with websites
   - Verify Claude scores them correctly
   - Generate outreach materials

4. **Export to CSV** (5 minutes)
   - Export all enriched contractors
   - Share with sales team
   - Get feedback

**Total Time**: ~35 minutes
**Cost**: $0 (within free tier)

### Phase 2: Scale Up (Next Week)
**Goal**: Process larger batches, optimize costs

1. **Batch processing** (already built)
   - Discover 100-200 contractors
   - Use bulk enrichment
   - Generate outreach for all

2. **Monitor API costs** (use Settings page)
   - Check token usage dashboard
   - Calculate cost per contractor
   - Adjust batch sizes

3. **Optimize searches**
   - Test different queries
   - Find best contractor types
   - Filter by ratings/reviews

**Total Time**: ~2 hours
**Cost**: ~$5-10 (Google Places + Claude tokens)

### Phase 3: Multi-Source (Optional - Later)
**Goal**: Maximum coverage, diverse sources

1. **Upgrade Python to 3.10+** (30 minutes)
   - Install uv tool
   - Install Python 3.10
   - Reinstall dependencies
   - Test existing functionality

2. **Add crawl4ai** (1 hour)
   - Install library
   - Test basic scraping
   - Verify no conflicts

3. **Build Houzz scraper** (2-3 hours)
   - Study Houzz HTML structure
   - Write extraction logic
   - Test with multiple searches
   - Handle pagination

4. **Build Yelp scraper** (2-3 hours)
   - Similar process
   - Extract reviews
   - Handle rate limiting

5. **Build HomeAdvisor scraper** (2-3 hours)
   - Extract pro profiles
   - Get certifications
   - Parse service areas

6. **Implement merge logic** (1 hour)
   - Deduplicate by phone
   - Combine data from sources
   - Update database schema

**Total Time**: ~8-10 hours
**Cost**: $0 (no API costs)

---

## Cost Analysis

### Scenario 1: Small Agency (100 contractors/month)
**Option 1 (Google Places)**:
- Contractor discovery: Free (within 10,000 limit)
- Enrichment (Claude): ~$2.00-5.00
- **Total**: ~$2-5/month

**Option 2 (crawl4ai)**:
- Contractor discovery: Free
- Enrichment (Claude): ~$2.00-5.00
- Python upgrade: One-time (30 min)
- **Total**: ~$2-5/month + setup time

### Scenario 2: Medium Agency (500 contractors/month)
**Option 1 (Google Places)**:
- Contractor discovery: Free (within 10,000 limit)
- Enrichment (Claude): ~$10.00-25.00
- **Total**: ~$10-25/month

**Option 2 (crawl4ai)**:
- Contractor discovery: Free
- Enrichment (Claude): ~$10.00-25.00
- **Total**: ~$10-25/month

### Scenario 3: Large Agency (5,000 contractors/month)
**Option 1 (Google Places)**:
- Contractor discovery: Free (within 10,000 limit)
- Enrichment (Claude): ~$200-500
- **Total**: ~$200-500/month

**Option 2 (crawl4ai)**:
- Contractor discovery: Free
- Enrichment (Claude): ~$200-500
- **Total**: ~$200-500/month

**Note**: Most cost is Claude enrichment, not discovery. Google's free tier (10,000/month) covers most use cases!

---

## Legal and Ethical Considerations

### Google Places API
- ✅ Official API - no ToS violations
- ✅ Licensed for commercial use
- ✅ Reliable, supported
- ⚠️ Must comply with Google Maps Platform Terms

### Web Scraping (crawl4ai)
- ⚠️ Check each site's Terms of Service
- ⚠️ Respect robots.txt files
- ⚠️ Use reasonable rate limits
- ⚠️ Some sites explicitly prohibit scraping
- ✅ Public data is generally okay to scrape (check jurisdiction)

**Best Practices**:
1. Read Terms of Service for each site
2. Check robots.txt before scraping
3. Use 2-5 second delays between requests
4. Identify your bot with proper User-Agent
5. Don't overload servers
6. Cache results to minimize requests

**Sites to Avoid Scraping** (ToS violations):
- LinkedIn (explicitly prohibited)
- Facebook (rate limits, requires API)
- Some sites require written permission

---

## Technical Specifications

### Current Environment
- **Python**: 3.9.6
- **OS**: macOS (Darwin 25.0.0)
- **Database**: Supabase (PostgreSQL)
- **Framework**: Streamlit
- **API**: Anthropic Claude Sonnet 4

### Required for crawl4ai
- **Python**: 3.10+ or 3.11+
- **Dependencies**: crawl4ai>=0.7.0
- **Memory**: Recommended 4GB+ RAM
- **Storage**: ~500MB for crawl4ai + dependencies

### Google Places API Requirements
- **Google Cloud Project**: Free tier available
- **APIs to Enable**: Places API (New), Places API
- **Billing**: Credit card required (for free tier too)
- **Security**: API key restrictions recommended

---

## Decision Matrix

| Factor | Google Places | crawl4ai | Hybrid |
|--------|--------------|----------|--------|
| **Setup Time** | 15 min | 3-4 hours | 4-5 hours |
| **Python Upgrade** | No | Yes | Yes |
| **Monthly Cost** | $0-20 | $0 | $0-20 |
| **Data Sources** | Google only | Multiple | Multiple |
| **Reliability** | Very High | Medium | High |
| **Maintenance** | Low | Medium | Medium |
| **Contractor Coverage** | High | Very High | Very High |
| **Recommended For** | Quick start | Max coverage | Best quality |

---

## Next Steps

### Immediate Action Items

**If choosing Google Places API** (15 minutes):
1. [ ] Go to Google Cloud Console
2. [ ] Create/select project
3. [ ] Enable Places APIs
4. [ ] Create API key
5. [ ] Add to `.env` file: `GOOGLE_PLACES_API_KEY=your-key`
6. [ ] Restart Streamlit
7. [ ] Test with real search
8. [ ] Enrich 5-10 contractors
9. [ ] Generate outreach materials
10. [ ] Share with sales team

**If choosing crawl4ai** (4-5 hours):
1. [ ] Install uv tool
2. [ ] Install Python 3.10
3. [ ] Create new virtual environment
4. [ ] Reinstall dependencies
5. [ ] Test existing app functionality
6. [ ] Add crawl4ai to requirements
7. [ ] Build Houzz scraper
8. [ ] Build Yelp scraper
9. [ ] Test multi-source discovery
10. [ ] Implement merge logic

**If choosing Hybrid** (5-6 hours):
1. [ ] Start with Google Places (Phase 1)
2. [ ] Test and validate with sales team
3. [ ] Then upgrade Python (Phase 2)
4. [ ] Add crawl4ai sources (Phase 3)
5. [ ] Implement merge logic
6. [ ] Compare data quality

---

## Questions to Answer Before Proceeding

1. **How many contractors do you need per month?**
   - <500: Google Places free tier is perfect
   - 500-2000: Still free, but consider alternatives
   - >2000: Might need multiple sources or cheaper API

2. **Do you need data from specific sources?**
   - Just local businesses: Google Places
   - Design contractors: Add Houzz (requires crawl4ai)
   - Maximum coverage: Hybrid approach

3. **What's your budget for discovery?**
   - $0/month: Use free tiers or crawl4ai
   - $20-50/month: Google Places is fine
   - Unlimited: Hybrid with all sources

4. **How comfortable with Python upgrades?**
   - Not comfortable: Stick with Google Places (no upgrade)
   - Comfortable: Go for crawl4ai (upgrade required)

5. **Timeline?**
   - Need data today: Google Places (15 min setup)
   - Can wait a week: crawl4ai (more setup)

---

## Support and Resources

### Google Places API
- **Documentation**: https://developers.google.com/maps/documentation/places/web-service
- **Console**: https://console.cloud.google.com/
- **Pricing**: https://mapsplatform.google.com/pricing/
- **Support**: Google Maps Platform support

### crawl4ai
- **Documentation**: https://docs.crawl4ai.com/
- **GitHub**: https://github.com/unclecode/crawl4ai
- **Examples**: See GitHub repo examples folder
- **Discord**: Community support channel

### Python Upgrade
- **uv tool**: https://astral.sh/uv
- **Python.org**: https://www.python.org/downloads/macos/
- **pyenv**: https://github.com/pyenv/pyenv

---

## Conclusion

**For 90% of use cases, start with Google Places API**:
- Fastest time to production (15 minutes)
- No code changes
- No Python upgrade
- Reliable, high-quality data
- Free tier covers most needs (10,000/month)

**Consider crawl4ai later if you need**:
- More than 10,000 contractors/month
- Specific data from Houzz, Yelp, etc.
- Cross-reference data quality
- Zero API costs

**The app is already production-ready** - you just need to choose your discovery method!

---

**Ready to implement?** Pick an option above and follow the setup steps. All the code infrastructure is already in place!
