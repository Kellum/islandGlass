-- =====================================================
-- Migration: 013_create_companies_table
-- Purpose: Multi-tenant company records for SaaS
-- Created: 2025-11-19
-- Part of: Multi-tenant SaaS implementation
-- =====================================================

CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Basic Info
    company_name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE,  -- URL-friendly name (e.g., "island-glass")

    -- Primary Contact
    primary_contact_name VARCHAR(255),
    primary_contact_email VARCHAR(255) NOT NULL,
    primary_contact_phone VARCHAR(50),

    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'USA',

    -- Subscription & Billing
    plan_tier VARCHAR(50) DEFAULT 'trial',  -- trial, basic, pro, enterprise
    status VARCHAR(50) DEFAULT 'active',  -- active, suspended, cancelled
    trial_ends_at TIMESTAMP,
    billing_email VARCHAR(255),
    stripe_customer_id VARCHAR(255),  -- For future Stripe integration

    -- Settings (JSON for flexibility)
    settings JSONB DEFAULT '{}',

    -- Audit Fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,
    deleted_by UUID
);

-- Indexes for performance
CREATE INDEX idx_companies_slug ON companies(slug);
CREATE INDEX idx_companies_status ON companies(status);
CREATE INDEX idx_companies_created_at ON companies(created_at DESC);

-- Enable Row Level Security
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only view their own company
CREATE POLICY "Users can view their own company"
ON companies
FOR SELECT
USING (id = (current_setting('app.company_id', true)::UUID));

-- Comments for documentation
COMMENT ON TABLE companies IS 'Multi-tenant companies - each customer organization';
COMMENT ON COLUMN companies.slug IS 'URL-friendly identifier for subdomains (e.g., jacksonville-glass)';
COMMENT ON COLUMN companies.plan_tier IS 'Subscription tier: trial (14 days), basic, pro, enterprise';
COMMENT ON COLUMN companies.status IS 'Account status: active, suspended, cancelled';
COMMENT ON COLUMN companies.settings IS 'Company-specific settings as JSON';
