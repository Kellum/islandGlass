-- Temporarily disable RLS for testing
-- WARNING: This disables security - only use for development/testing

ALTER TABLE po_clients DISABLE ROW LEVEL SECURITY;
ALTER TABLE po_client_contacts DISABLE ROW LEVEL SECURITY;

-- You can re-enable later with:
-- ALTER TABLE po_clients ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE po_client_contacts ENABLE ROW LEVEL SECURITY;
