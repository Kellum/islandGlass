-- =====================================================
-- Migration: 014_create_user_invitations_table
-- Purpose: User invitation system for adding team members
-- Created: 2025-11-19
-- Part of: Multi-tenant SaaS implementation
-- =====================================================

CREATE TABLE IF NOT EXISTS user_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    invited_by UUID REFERENCES users(user_id),

    -- Invitation Details
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,  -- admin, manager, sales, production
    department VARCHAR(100),

    -- Security Token
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,

    -- Status Tracking
    status VARCHAR(50) DEFAULT 'pending',  -- pending, accepted, expired, cancelled

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    accepted_at TIMESTAMP,

    -- Additional metadata (optional)
    metadata JSONB DEFAULT '{}'
);

-- Indexes
CREATE INDEX idx_invitations_token ON user_invitations(token);
CREATE INDEX idx_invitations_company_id ON user_invitations(company_id);
CREATE INDEX idx_invitations_email ON user_invitations(email);
CREATE INDEX idx_invitations_status ON user_invitations(status);
CREATE INDEX idx_invitations_expires_at ON user_invitations(expires_at);

-- Enable Row Level Security
ALTER TABLE user_invitations ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see invitations for their company
CREATE POLICY "Users can view their company's invitations"
ON user_invitations
FOR ALL
USING (company_id = (current_setting('app.company_id', true)::UUID));

-- Comments
COMMENT ON TABLE user_invitations IS 'Pending invitations for users to join a company';
COMMENT ON COLUMN user_invitations.token IS 'Secure random token for invitation link (used in URL)';
COMMENT ON COLUMN user_invitations.expires_at IS 'Invitation expires after 7 days by default';
