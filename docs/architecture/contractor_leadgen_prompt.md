# BUILD A GENERAL CONTRACTOR CONTACT DATABASE & OUTREACH TOOL

## Business Context
I run a glazing company (frameless showers, windows, storefront glass) in Jacksonville, FL. My sales team (1-3 people) needs to do cold outreach to general contractors in the area who might need our services as a subcontractor. Build a tool that finds contractors, enriches their contact info, generates personalized outreach, and provides a simple interface for my team to manage leads.

**Deployment Target**: Railway (cloud hosting)
**Users**: 1-3 sales reps accessing simultaneously

## Target Market
- General contractors (residential and commercial)
- Geographic area: Jacksonville, FL + surrounding areas (Fernandina Beach, Yulee, St. Johns County, Nassau County, Duval County, Orange Park, St. Augustine, Ponte Vedra)
- Goal: Build database of as many qualified contractors as possible in this area

---

## MODULE 1: Contractor Discovery with Crawl4AI

Use **Crawl4AI** library for all web scraping (not Playwright or BeautifulSoup).

### Target Geographic Areas (Florida Only)
- Jacksonville, FL
- Yulee, FL
- Fernandina Beach, FL
- Jacksonville Beach, FL
- Atlantic Beach, FL
- Neptune Beach, FL
- Ponte Vedra, FL
- Nocatee, FL

### Targeted Search Queries

**CRITICAL**: Only search for contractor types that need glazing services. Do NOT search for generic "general contractors" - too much noise.

**Residential Glazing Searches** (Frameless showers, cabinet glass, tabletops):
- "bathroom remodeling {city} FL"
- "kitchen remodeling {city} FL"
- "home remodeling {city} FL"
- "custom home builder {city} FL"
- "interior designer {city} FL"

**Commercial Glazing Searches** (Storefront, glass railings, protective tops):
- "commercial contractor {city} FL"
- "storefront contractor {city} FL"
- "tenant improvement contractor {city} FL"
- "retail construction {city} FL"
- "office renovation {city} FL"
- "restaurant contractor {city} FL"

**Specialty Glazing Searches** (Glass railings, protective tops):
- "deck builder {city} FL"
- "pool contractor {city} FL"
- "custom furniture {city} FL"

**Total Searches**: ~14 query types × 8 cities = 112 targeted searches

### Multi-Source Scraping Strategy

**Source 1: Google Maps (Primary - Highest Priority)**
For each search query + city combination:
- Use Crawl4AI to scrape Google Maps search results
- Extract: Business name, address, phone, website, Google rating, review count, business category
- Aim for top 20 results per search
- Store with source='google_maps'

Example implementation approach:
```python
cities = ["Jacksonville", "Yulee", "Fernandina Beach", "Jacksonville Beach", 
          "Atlantic Beach", "Neptune Beach", "Ponte Vedra", "Nocatee"]

residential_queries = [
    "bathroom remodeling",
    "kitchen remodeling", 
    "home remodeling",
    "custom home builder",
    "interior designer"
]

commercial_queries = [
    "commercial contractor",
    "storefront contractor",
    "tenant improvement contractor",
    "retail construction",
    "office renovation",
    "restaurant contractor"
]

specialty_queries = [
    "deck builder",
    "pool contractor",
    "custom furniture"
]

all_queries = residential_queries + commercial_queries + specialty_queries

for city in cities:
    for query in all_queries:
        search_term = f"{query} {city} FL"
        # Scrape Google Maps with Crawl4AI
        # Extract business listings
        # Save to database
        time.sleep(3)  # Rate limiting
```

**Source 2: Yelp (Secondary)**
- Same search queries as Google Maps
- Extract: Business name, phone, website, Yelp rating, category tags
- Store with source='yelp'
- Cross-reference with Google Maps data to avoid duplicates

**Source 3: Houzz (For High-End Residential)**
- Search: "contractors {city} FL", "designers {city} FL"
- Extract: Business name, website, portfolio links, services offered
- Store with source='houzz'
- Particularly valuable for custom home builders and designers who need cabinet glass/tabletops

**Source 4: Better Business Bureau (Optional - For Verification)**
- Search BBB directory for contractors in target cities
- Extract: Business name, phone, accreditation status, years in business
- Use for enrichment/verification rather than primary source
- Store with source='bbb'

### Duplicate Detection & Merging

**IMPORTANT**: Same business may appear across multiple sources. Implement deduplication:

1. **Primary matching**: Company name + phone number
2. **Secondary matching**: Company name + city + similar address
3. **Merge strategy**: Keep record with most complete data, combine sources in metadata

Example:
```python
# If "ABC Remodeling" found on both Google Maps and Yelp:
# - Keep Google Maps rating AND Yelp rating
# - Combine all available contact info
# - Mark as sources='google_maps,yelp'
```

### Scraping Implementation Details

**Rate Limiting (CRITICAL):**
- 2-3 second delay between requests to same source
- Rotate user agents
- Use Crawl4AI's built-in throttling
- If blocked, increase delays to 5-10 seconds

**Error Handling:**
- If search returns 0 results, log but continue
- If specific business data incomplete, save what you have
- Retry failed scrapes once before marking as failed
- Never crash - always log errors and continue

**Data Validation:**
- Phone numbers: Format as (XXX) XXX-XXXX, validate 10 digits
- Websites: Ensure http:// or https:// prefix
- City names: Normalize to match target list
- Remove duplicate entries within same source

### Manual Upload Option
- Accept CSV upload with columns: company_name, phone, email, website, city
- Validate data and insert into database
- Flag as source='manual_upload'

---

## MODULE 2: Contact Enrichment with Crawl4AI + Claude

For each contractor discovered:

### Website Crawling (if website exists)
Use Crawl4AI to fetch and parse the contractor's website:
```python
from crawl4ai import WebCrawler

# Crawl4AI should extract clean text from website
result = crawler.run(url=website_url)
clean_text = result.markdown  # or result.cleaned_html
```

### Claude Analysis
Send crawled website content to Claude API with this prompt structure:

```
Analyze this contractor's website and determine if they are a good fit for glazing services (frameless showers, cabinet glass, tabletops, protective glass tops, glass railings, storefront systems, window/IGU replacement).

Website content:
{clean_text}

Extract the following in JSON format:
{
  "contact_email": "primary email or null",
  "contact_person": "owner/manager name or null",
  "specializations": ["specific services like bathroom remodeling, custom homes, commercial buildouts, etc"],
  "company_type": "residential|commercial|both",
  "glazing_relevant_services": ["which of their services need our glazing products"],
  "glazing_opportunity_types": ["which glazing services they likely need: frameless_showers|cabinet_glass|tabletops|protective_tops|glass_railings|storefront|window_replacement"],
  "company_age": "years in business or null",
  "team_size_indicator": "small|medium|large or null",
  "project_examples": ["any bathroom/kitchen/commercial projects mentioned"],
  "uses_subcontractors": "likely|unlikely|unknown",
  "glazing_opportunity_score": 1-10 based on how much they need our services,
  "disqualify_reason": "if score <5, explain why they don't need glazing services, else null",
  "outreach_angle": "best hook mentioning their specific projects that need our glazing"
}

Scoring guide:
- 9-10: Does bathroom remodels, custom showers, or commercial storefront
- 7-8: Does kitchen remodels (cabinet glass), custom homes (multiple glass needs), or office buildouts
- 5-6: Does decks/pools (glass railings) or custom furniture (tabletops)
- 1-4: Roofing, HVAC, landscaping, foundation, electrical - does NOT need glazing

Be conservative with scoring - better to underscore than overscore.
```

### Social Media Discovery
Use Crawl4AI or simple search to find:
- Facebook business page
- Instagram profile
- LinkedIn company page
- Method: Search "{company_name} Jacksonville Facebook" etc., extract first relevant result

### Lead Scoring Logic
Score contractors 1-10 based on:
- **9-10 (Hot Leads)**: Bathroom remodelers, shower specialists, commercial storefront contractors
- **7-8 (Warm Leads)**: Kitchen remodelers, custom home builders, restaurant/retail contractors, office renovation
- **5-6 (Possible Leads)**: Deck builders, pool contractors, custom furniture makers
- **1-4 (Cold/Disqualified)**: Roofing, HVAC, electrical, plumbing, foundation, landscaping specialists

**Auto-filter**: Only keep contractors with score ≥5 in the database

---

## MODULE 3: Personalized Outreach with Claude

For each contractor, use Claude API to generate:

### Email Templates (3 variations)
Prompt structure:
```
Generate 3 professional email templates for cold outreach from a glazing company to this contractor:

Contractor profile:
- Company: {company_name}
- Specialization: {specializations}
- Glazing opportunity: {glazing_opportunity_types}
- Type: {company_type}
- Location: {city}, Florida

Our glazing services:
- Frameless shower enclosures & glass shower doors
- Custom cabinet glass (kitchen & bathroom)
- Glass tabletops & protective glass countertops
- Glass railings (deck, stair, pool)
- Commercial storefront systems & entrances
- Window replacement & IGU (insulated glass unit) replacement

Requirements:
- Subject line + body for each email
- Reference their specific work that needs our glazing (e.g., "noticed you do bathroom remodels - we supply frameless showers")
- Mention Florida/Northeast Florida location relevance
- Professional but conversational tone (not salesy)
- Include [EDIT: project name] style placeholders where personalization needed
- Keep body under 120 words
- Include clear call-to-action (schedule call, get quote, etc.)
- Vary the approach across 3 emails (different hooks/angles)

Return as JSON:
{
  "email_1": {"subject": "...", "body": "..."},
  "email_2": {"subject": "...", "body": "..."},
  "email_3": {"subject": "...", "body": "..."}
}
```

### Call Scripts (2 variations)
Prompt structure:
```
Generate 2 cold call scripts for reaching this contractor about glazing services:

Contractor profile:
- Company: {company_name}
- Specialization: {specializations}
- Glazing opportunities: {glazing_opportunity_types}

Our glazing services:
- Frameless shower enclosures & glass shower doors
- Custom cabinet glass
- Glass tabletops & protective countertops  
- Glass railings
- Commercial storefront systems
- Window/IGU replacement

Requirements:
- Opening line (15-20 seconds) - personalized to their work
- Value proposition specific to the glazing products they need
- 2-3 discovery questions to qualify their needs
- Handle common objections (already have supplier, not interested)
- Clear next step/close (send samples, schedule meeting, etc.)
- Natural conversational language (not scripted-sounding)
- Include [PAUSE] markers for listening to response
- Reference their location in Jacksonville/NE Florida area

Return as JSON:
{
  "script_1": "full script text with [PAUSE] markers",
  "script_2": "full script text with different opening angle"
}
```

---

## MODULE 4: Streamlit Web Interface

Build a multi-page Streamlit app optimized for Railway deployment.

### App Configuration for Railway
```python
# config.toml for Streamlit
[server]
port = 8080
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

### Page 1: Dashboard
Display:
- Total contractors in database
- Breakdown by status (Not Contacted, Contacted, Follow-up, Won, Lost)
- High-priority leads (score 8+) in expandable section
- Recently added (last 7 days)
- Quick stats: Total contacts this week, response rate

Visual: Use Streamlit metrics and simple bar charts

### Page 2: Contractor Directory
**Search & Filter Section:**
- Text search: company name, city
- Filters: Lead score range (slider), Status (multiselect), Company type (residential/commercial/both), City (multiselect)
- Sort by: Date added, Lead score, Company name

**Results Table:**
Display as Streamlit dataframe with columns:
- Company Name (clickable)
- City
- Phone
- Email
- Score
- Status
- Last Updated

Click row → Navigate to detail view

### Page 3: Contractor Detail View
Layout in columns:

**Left Column - Contact Info:**
- Company name (header)
- Contact person
- Phone (click to copy)
- Email (click to copy)
- Website (clickable link)
- Address
- Social media links (icons/links)

**Right Column - Company Profile:**
- Lead score (with colored badge)
- Specializations (tags)
- Company type
- Profile notes (from Claude analysis)

**Outreach Materials Section:**
Tabs for:
- **Email Templates**: 3 expandable sections, each with editable text area + "Copy to Clipboard" button
- **Call Scripts**: 2 expandable sections, each with editable text area + "Copy to Clipboard" button

Changes to templates auto-save on edit (or have explicit Save button)

**Interaction Tracking:**
- Status dropdown: Not Contacted, Called - No Answer, Called - Connected, Email Sent, Follow-up Scheduled, Meeting Booked, Won, Lost
- Notes text area (for sales rep comments)
- "Log Interaction" button to save
- History table showing all past status changes with timestamps

**Action Buttons:**
- "Export This Contact" (downloads single-row CSV)
- "Generate New Outreach" (re-runs Claude generation)

### Page 4: Bulk Actions
- Display current filters from Directory page
- "Export Filtered Results" → CSV download with columns: Company, Contact, Phone, Email, Website, Score, Status, Specializations, Top Outreach Angle
- Bulk status update: Select multiple contractors (checkboxes) → Update status for all
- "Re-generate Outreach for Selected" button

### Page 5: Add/Import Contractors
Two sections:

**Manual Entry:**
- Form with fields: Company name, Contact person, Phone, Email, Website, City
- "Add & Enrich" button → Runs enrichment process

**CSV Upload:**
- File uploader
- Required columns: company_name, city
- Optional columns: phone, email, website, contact_person
- "Upload & Enrich" button → Processes all rows

Show progress bar during enrichment

### Page 6: Settings/Admin
- View API usage stats (Claude API calls this month)
- Database stats (total records, last enrichment run)
- "Re-enrich All" button (re-runs Claude analysis on all contractors)
- Export full database to CSV

---

## MODULE 5: Database Schema (Supabase PostgreSQL)

**Use Supabase** instead of SQLite for better Railway deployment and multi-user support.

### Setup Supabase
1. Create free account at supabase.com
2. Create new project
3. Copy connection string from Settings → Database
4. Install: `pip install supabase`

### Table: contractors
```sql
CREATE TABLE contractors (
    id BIGSERIAL PRIMARY KEY,
    company_name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    website TEXT,
    address TEXT,
    city TEXT,
    state TEXT DEFAULT 'FL',
    zip TEXT,
    google_rating REAL,
    review_count INTEGER,
    facebook_url TEXT,
    instagram_url TEXT,
    linkedin_url TEXT,
    specializations TEXT,  -- comma-separated
    glazing_opportunity_types TEXT,  -- frameless_showers, cabinet_glass, tabletops, etc.
    company_type TEXT,  -- residential|commercial|both
    lead_score INTEGER,  -- 1-10 (only store if ≥5)
    profile_notes TEXT,  -- Claude's analysis
    outreach_angle TEXT,  -- best hook for contact
    uses_subcontractors TEXT,  -- likely|unlikely|unknown
    disqualify_reason TEXT,  -- if score <5, why they don't fit
    date_added TIMESTAMP DEFAULT NOW(),
    date_last_updated TIMESTAMP DEFAULT NOW(),
    enrichment_status TEXT DEFAULT 'pending',  -- pending|completed|failed
    source TEXT  -- google_maps|manual_upload|csv_import
);

-- Add indexes for performance
CREATE INDEX idx_contractors_city ON contractors(city);
CREATE INDEX idx_contractors_score ON contractors(lead_score);
CREATE INDEX idx_contractors_status ON contractors(enrichment_status);
```

### Table: outreach_materials
```sql
CREATE TABLE outreach_materials (
    id BIGSERIAL PRIMARY KEY,
    contractor_id INTEGER,
    material_type TEXT,  -- email_1|email_2|email_3|script_1|script_2
    subject_line TEXT,  -- for emails only
    content TEXT NOT NULL,
    is_edited BOOLEAN DEFAULT FALSE,
    date_generated TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (contractor_id) REFERENCES contractors(id) ON DELETE CASCADE
);
```

### Table: interaction_log
```sql
CREATE TABLE interaction_log (
    id BIGSERIAL PRIMARY KEY,
    contractor_id INTEGER,
    status TEXT NOT NULL,
    notes TEXT,
    user_name TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (contractor_id) REFERENCES contractors(id) ON DELETE CASCADE
);
```

### Table: app_settings
```sql
CREATE TABLE app_settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Supabase Connection (Python)
```python
from supabase import create_client, Client
import os

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Example query
contractors = supabase.table("contractors").select("*").eq("city", "Jacksonville").execute()
```

---

## MODULE 6: Railway Deployment Setup

### Project Structure
```
contractor-leadgen/
├── app.py                 # Main Streamlit app
├── requirements.txt
├── railway.toml           # Railway config
├── .streamlit/
│   └── config.toml
├── modules/
│   ├── scraper.py        # Crawl4AI scraping logic
│   ├── enrichment.py     # Claude enrichment
│   ├── database.py       # SQLite operations
│   └── outreach.py       # Claude outreach generation
├── data/
│   └── contractors.db    # SQLite database (persistent storage)
└── .env.example
```

### requirements.txt
```
streamlit==1.31.0
anthropic==0.18.1
crawl4ai==0.2.5
pandas==2.1.4
python-dotenv==1.0.0
playwright==1.41.0
supabase==2.3.4
```

### railway.toml
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "streamlit run app.py --server.port $PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[env]
PYTHONUNBUFFERED = "1"
```

### Environment Variables (Set in Railway Dashboard)
```
ANTHROPIC_API_KEY=your_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
```

---

## BUILD SEQUENCE

### Step 1: Local Setup & Database
- Create Supabase project and tables (run SQL schema)
- Build basic Streamlit app with navigation
- Test database connection and CRUD operations
- Implement session state management

### Step 2: Contractor Discovery
- Integrate Crawl4AI
- Build scraping functions for Google Maps, Yelp, and Houzz
- Implement targeted search queries (bathroom remodeling, commercial contractor, etc.)
- Test with one city + one query type (e.g., "bathroom remodeling Jacksonville FL")
- Save 10-20 results to Supabase
- Implement deduplication logic
- Verify data quality and relevance

### Step 3: Website Enrichment
- For contractors with websites, use Crawl4AI to fetch content
- Build Claude integration for website analysis with glazing-focused scoring
- Test with 5-10 contractor websites from different specialties
- Verify Claude correctly identifies glazing opportunities (scores bathroom remodelers high, roofers low)
- Save enriched data to Supabase
- Verify lead scoring accuracy

### Step 4: Outreach Generation
- Build Claude prompts for email/script generation with glazing service details
- Generate materials for 5-10 existing contractors with different specialties
- Verify emails reference correct glazing products (showers for bathroom remodelers, storefront for commercial, etc.)
- Save to outreach_materials table
- Test template quality and personalization with sales team

### Step 5: UI - Contractor Detail View
- Build detail page layout
- Display all contractor info
- Show outreach materials in editable text boxes
- Implement save functionality
- Add interaction tracking

### Step 6: UI - Directory & Search
- Build searchable/filterable table
- Add filters: Lead score, glazing opportunity type, city, company type
- Implement sorting
- Add navigation to detail view
- Test with full dataset from multiple sources

### Step 7: UI - Dashboard & Bulk Actions
- Build dashboard with stats
- Implement CSV export
- Add bulk status updates
- Create manual add form

### Step 8: Railway Deployment
- Test locally with Supabase connection
- Configure Railway project
- Set environment variables (ANTHROPIC_API_KEY, SUPABASE_URL, SUPABASE_KEY)
- Deploy and test
- Configure custom domain (optional)

### Step 9: Testing & Refinement
- Run full scraping cycle across all 8 cities
- Verify 200+ high-quality leads collected
- Test lead scoring accuracy (bathroom remodelers should score 9-10, roofers should be filtered out)
- Refine Claude prompts based on output
- Optimize database queries
- Add error handling and user feedback
- Get sales team feedback on outreach quality

---

## CRITICAL REQUIREMENTS

### For Crawl4AI Integration
- Use async mode for better performance
- Implement retry logic (3 attempts)
- Handle timeouts gracefully
- Cache crawled content to avoid re-fetching
- Respect 2-3 second delays between requests

### For Claude API Usage
- Use claude-sonnet-4-20250514 model
- Set max_tokens=2000 for enrichment, 1000 for outreach
- Implement exponential backoff on rate limits
- Cache results to avoid duplicate API calls
- Track token usage for cost monitoring

### For Railway Deployment
- Supabase handles database persistence automatically
- Implement health check endpoint
- Handle cold starts gracefully
- Set appropriate memory limits (1GB minimum)
- Enable automatic restarts on failure

### For Multi-User Support
- Supabase handles concurrent access automatically
- Use Streamlit session state for UI state only
- Add user identification (simple dropdown on first load)
- Log which user made which changes in interaction_log table
- Real-time updates via Supabase subscriptions (optional advanced feature)

### Error Handling
- Never crash the app - always show user-friendly errors
- Log all errors to console for debugging
- If enrichment fails, mark contractor but keep in database
- If Claude API is down, queue requests for later
- Provide clear feedback on all actions

### Performance Optimization
- Lazy load contractor details (only when viewed)
- Paginate directory results (50 per page)
- Cache frequently accessed data in session state
- Supabase automatically indexes primary/foreign keys
- Add custom indexes for city, lead_score, enrichment_status
- Limit Claude API calls during bulk operations

---

## SUCCESS CRITERIA

- Successfully discover and store 200+ qualified contractors from target cities
- **Lead relevance >85%**: Contractors scraped actually need glazing services (verified by sales team)
- **Scoring accuracy >90%**: Bathroom remodelers score 8-10, roofers/HVAC filtered out or score <5
- Contact enrichment success rate >70%
- Outreach materials rated as "useful and relevant" by sales team
- All 3 users can access simultaneously without issues
- Directory page loads in <3 seconds
- Detail page loads in <2 seconds
- Zero data loss (Supabase handles backups)
- App remains stable under normal usage (no crashes)
- **Geographic accuracy 100%**: All contractors are actually in the 8 target Florida cities

---

## TESTING CHECKLIST

Before marking as complete, verify:
- [ ] Can discover contractors from Google Maps
- [ ] Can upload CSV and enrich
- [ ] Website enrichment works for 10 different contractor sites
- [ ] Outreach generation produces relevant, personalized content
- [ ] All filters and search work correctly
- [ ] Status tracking and notes save properly
- [ ] CSV export includes all necessary fields
- [ ] Multiple users can edit different contractors simultaneously
- [ ] Database persists after Railway restart
- [ ] All error cases handled gracefully
- [ ] Mobile/tablet responsive (basic functionality)

---

## START HERE

Build this iteratively. Begin with Step 1:
1. Create Supabase account and project
2. Run the SQL schema to create tables
3. Create basic Streamlit app that connects to Supabase
4. Display one hardcoded contractor record from the database

Show me that working before proceeding to contractor discovery.