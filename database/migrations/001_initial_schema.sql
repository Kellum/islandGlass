-- Island Glass Leads - Supabase Database Schema
-- Run this in Supabase SQL Editor to create all tables

-- Table: contractors
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
    source TEXT  -- google_maps|yelp|houzz|bbb|manual_upload|csv_import
);

-- Add indexes for performance
CREATE INDEX idx_contractors_city ON contractors(city);
CREATE INDEX idx_contractors_score ON contractors(lead_score);
CREATE INDEX idx_contractors_status ON contractors(enrichment_status);
CREATE INDEX idx_contractors_company_name ON contractors(company_name);

-- Table: outreach_materials
CREATE TABLE outreach_materials (
    id BIGSERIAL PRIMARY KEY,
    contractor_id BIGINT NOT NULL,
    material_type TEXT NOT NULL,  -- email_1|email_2|email_3|script_1|script_2
    subject_line TEXT,  -- for emails only
    content TEXT NOT NULL,
    is_edited BOOLEAN DEFAULT FALSE,
    date_generated TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (contractor_id) REFERENCES contractors(id) ON DELETE CASCADE
);

-- Index for faster lookups by contractor
CREATE INDEX idx_outreach_contractor_id ON outreach_materials(contractor_id);

-- Table: interaction_log
CREATE TABLE interaction_log (
    id BIGSERIAL PRIMARY KEY,
    contractor_id BIGINT NOT NULL,
    status TEXT NOT NULL,
    notes TEXT,
    user_name TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (contractor_id) REFERENCES contractors(id) ON DELETE CASCADE
);

-- Index for faster lookups by contractor
CREATE INDEX idx_interaction_contractor_id ON interaction_log(contractor_id);
CREATE INDEX idx_interaction_timestamp ON interaction_log(timestamp DESC);

-- Table: app_settings
CREATE TABLE app_settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table: api_usage - Track Claude API token usage and costs
CREATE TABLE api_usage (
    id BIGSERIAL PRIMARY KEY,
    contractor_id BIGINT,  -- nullable for future non-contractor API calls
    action_type TEXT NOT NULL,  -- enrichment|email_generation|script_generation
    model TEXT NOT NULL,  -- claude-sonnet-4-20250514
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    estimated_cost DECIMAL(10, 6) NOT NULL,  -- cost in USD
    success BOOLEAN DEFAULT TRUE,
    timestamp TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (contractor_id) REFERENCES contractors(id) ON DELETE SET NULL
);

-- Indexes for api_usage
CREATE INDEX idx_api_usage_contractor_id ON api_usage(contractor_id);
CREATE INDEX idx_api_usage_action_type ON api_usage(action_type);
CREATE INDEX idx_api_usage_timestamp ON api_usage(timestamp DESC);
CREATE INDEX idx_api_usage_success ON api_usage(success);

-- Insert a test contractor record
INSERT INTO contractors (
    company_name,
    contact_person,
    phone,
    email,
    website,
    city,
    state,
    specializations,
    glazing_opportunity_types,
    company_type,
    lead_score,
    profile_notes,
    outreach_angle,
    enrichment_status,
    source
) VALUES (
    'Jacksonville Premium Remodeling',
    'John Smith',
    '(904) 555-0123',
    'john@jaxremodeling.com',
    'https://jaxremodeling.com',
    'Jacksonville',
    'FL',
    'bathroom remodeling, kitchen remodeling, custom showers',
    'frameless_showers, cabinet_glass',
    'residential',
    9,
    'Specializes in high-end bathroom and kitchen remodels. Strong focus on custom shower installations. Perfect fit for frameless shower enclosures and cabinet glass.',
    'Your custom bathroom projects would benefit from our premium frameless shower systems - installed weekly for Jacksonville contractors',
    'completed',
    'manual_upload'
);

-- Verify the insert
SELECT * FROM contractors;
