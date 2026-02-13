-- Migration: Add vendor_contacts table for multiple contacts per vendor
-- Date: November 17, 2025
-- Description: Create vendor_contacts table similar to po_client_contacts
--              to support multiple contacts with job titles per vendor

-- Create vendor_contacts table
CREATE TABLE IF NOT EXISTS vendor_contacts (
  id SERIAL PRIMARY KEY,
  vendor_id INTEGER NOT NULL REFERENCES vendors(vendor_id) ON DELETE CASCADE,

  -- Contact information
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  job_title TEXT,  -- e.g., "Sales Rep", "Account Manager", "Owner"
  is_primary BOOLEAN DEFAULT FALSE,

  -- Company scoping + audit trails
  company_id TEXT,
  created_by TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_by TEXT,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_vendor_contacts_vendor_id ON vendor_contacts(vendor_id);
CREATE INDEX IF NOT EXISTS idx_vendor_contacts_company_id ON vendor_contacts(company_id);
CREATE INDEX IF NOT EXISTS idx_vendor_contacts_is_primary ON vendor_contacts(is_primary);

-- Add RLS (Row Level Security) policy
ALTER TABLE vendor_contacts ENABLE ROW LEVEL SECURITY;

-- Policy: Users can access vendor contacts from their own company
CREATE POLICY vendor_contacts_company_isolation ON vendor_contacts
  FOR ALL
  USING (company_id = current_setting('app.current_company_id', TRUE));

-- Trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_vendor_contacts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER vendor_contacts_updated_at
BEFORE UPDATE ON vendor_contacts
FOR EACH ROW
EXECUTE FUNCTION update_vendor_contacts_updated_at();

-- Comments for documentation
COMMENT ON TABLE vendor_contacts IS 'Multiple contacts per vendor (similar to client contacts)';
COMMENT ON COLUMN vendor_contacts.vendor_id IS 'Foreign key to vendors table';
COMMENT ON COLUMN vendor_contacts.job_title IS 'Contact job title (e.g., Sales Rep, Account Manager, Owner)';
COMMENT ON COLUMN vendor_contacts.is_primary IS 'Primary contact for this vendor';
