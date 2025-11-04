# Database Migrations Guide

This directory contains all SQL migration files and utilities for the Island Glass CRM database.

---

## Directory Structure

```
database/
├── README.md              # This file
├── migrations/            # Versioned SQL migrations (run in order)
├── utilities/             # Helper queries and checks
└── archive/              # Historical/deprecated migrations
```

---

## Running Migrations

### Initial Setup (New Database)

Run these migrations in your Supabase SQL Editor **in numerical order**:

1. **001_initial_schema.sql**
   - Creates base tables: contractors, outreach_materials, interaction_log, etc.
   - Sets up initial RLS policies
   - Required for: All functionality

2. **002_user_roles_departments.sql**
   - Creates user_profiles table with roles and departments
   - Adds company_id for multi-tenancy
   - Required for: Authentication, permissions

3. **003_window_manufacturing.sql**
   - Creates window system tables: po_clients, window_orders, window_order_items, window_labels
   - Sets up RLS policies for window manufacturing
   - Required for: Window manufacturing features

4. **004_window_seed_data.sql**
   - Adds reference data: window types, glass types, printer status
   - Required for: Window order entry, label printing

### How to Run a Migration

1. Open [Supabase Dashboard](https://supabase.com/dashboard)
2. Navigate to your project
3. Go to **SQL Editor** in left sidebar
4. Click **New Query**
5. Copy/paste the entire migration file
6. Click **Run** (or press Cmd/Ctrl + Enter)
7. Check output for errors
8. Verify success message appears

### Verification

After running migrations, verify tables exist:

```sql
-- List all tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Check RLS is enabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
```

---

## Migration Files

### 001_initial_schema.sql
**Purpose**: Foundation tables for contractor lead generation system

**Tables Created:**
- `contractors` - Contractor lead records
- `outreach_materials` - Generated emails and scripts
- `interaction_log` - Communication tracking
- `app_settings` - Application configuration
- `api_usage` - API token tracking

**RLS Policies**: Permissive (allow all for single-company use)

**Indexes**:
- contractors(company_name)
- contractors(created_at)
- interaction_log(contractor_id)

---

### 002_user_roles_departments.sql
**Purpose**: User authentication and role-based access control

**Tables Created:**
- `user_profiles` - User metadata, roles, departments

**Roles Added:**
- `admin` - Full system access
- `manager` - Team management
- `sales` - Lead generation & CRM
- `production` - Manufacturing operations

**Departments:**
- `sales` - Sales team
- `production` - Manufacturing team
- `accounting` - Financial operations

**RLS Policies**: Company-scoped (users see only their company data)

---

### 003_window_manufacturing.sql
**Purpose**: Window manufacturing order management system

**Tables Created:**
- `po_clients` - Purchase order customers
- `po_client_contacts` - Multiple contacts per client
- `window_orders` - Order headers
- `window_order_items` - Individual windows
- `window_labels` - Printable labels
- `window_types` - Window type reference
- `glass_types` - Glass inventory
- `label_printers` - Printer configuration

**Features:**
- Multi-window orders
- Fraction-based measurements
- Automated label generation
- Status workflow (pending → in_production → completed → shipped)

**RLS Policies**: Company-scoped with role checks

---

### 004_window_seed_data.sql
**Purpose**: Reference data for window manufacturing

**Data Added:**
- Window types: Rectangle, Circle, Triangle, etc.
- Glass types: Clear, Tinted, Laminated, Tempered, etc.
- Default printer configuration

**Notes**: Safe to run multiple times (uses INSERT ... ON CONFLICT)

---

## Utilities

### Checking Migration Status

```sql
-- Check what tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Count records in each table
SELECT
    schemaname,
    tablename,
    n_live_tup as row_count
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY tablename;
```

### Testing RLS Policies

```sql
-- Test as authenticated user
SET request.jwt.claims TO '{"sub": "user-id-here", "email": "test@example.com"}';

-- Try to select data
SELECT * FROM contractors LIMIT 5;

-- Reset
RESET request.jwt.claims;
```

### Company Setup

After migrations, you'll need to create company and user records:

```sql
-- Check if company exists
SELECT * FROM companies WHERE name = 'Your Company';

-- Check user profile
SELECT * FROM user_profiles WHERE auth_user_id = 'your-auth-id';
```

---

## Troubleshooting

### Common Issues

**Error: "relation already exists"**
- Table already created
- Solution: Skip that migration or drop table first

**Error: "permission denied for table"**
- RLS policy blocking access
- Solution: Use Supabase service role key or check policies

**Error: "column does not exist"**
- Migration run out of order
- Solution: Run previous migrations first

**No data returned from queries**
- RLS blocking access
- Solution: Check company_id and user authentication

### Rollback

To rollback a migration:
```sql
DROP TABLE IF EXISTS table_name CASCADE;
```

**Warning**: This deletes all data in the table!

### Archive Folder

The `archive/` folder contains:
- Old migration attempts
- Deprecated schemas
- Testing queries
- Development utilities

**Do not run files from archive/** unless specifically instructed.

---

## Development Workflow

### Creating a New Migration

1. Create file: `migrations/00X_description.sql`
2. Use next available number (005, 006, etc.)
3. Include:
   - Table creation
   - Indexes
   - RLS policies
   - Comments

4. Test on development database first
5. Document in this README
6. Commit to git

### Migration Template

```sql
-- Migration: 00X_feature_name
-- Purpose: Brief description
-- Created: YYYY-MM-DD

-- ============================================
-- Tables
-- ============================================

CREATE TABLE IF NOT EXISTS my_table (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Indexes
-- ============================================

CREATE INDEX IF NOT EXISTS idx_my_table_company
    ON my_table(company_id);

-- ============================================
-- RLS Policies
-- ============================================

ALTER TABLE my_table ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Company isolation"
    ON my_table
    FOR ALL
    USING (company_id = current_setting('app.company_id')::BIGINT);

-- ============================================
-- Comments
-- ============================================

COMMENT ON TABLE my_table IS 'Description of table purpose';
```

---

## RLS Best Practices

### Always Include Company Scope

```sql
CREATE POLICY "company_access"
    ON table_name
    FOR ALL
    USING (company_id = current_setting('app.company_id')::BIGINT);
```

### Role-Based Policies

```sql
CREATE POLICY "admin_full_access"
    ON table_name
    FOR ALL
    USING (
        current_setting('app.user_role') = 'admin'
        AND company_id = current_setting('app.company_id')::BIGINT
    );
```

### Department Filtering

```sql
CREATE POLICY "department_access"
    ON table_name
    FOR SELECT
    USING (
        department = current_setting('app.user_department')
        AND company_id = current_setting('app.company_id')::BIGINT
    );
```

---

## Database Maintenance

### Backup Before Changes

```bash
# Export schema
pg_dump -h db.xxx.supabase.co -U postgres -d postgres \
    --schema-only --no-owner --no-acl > schema_backup.sql

# Export data
pg_dump -h db.xxx.supabase.co -U postgres -d postgres \
    --data-only --no-owner --no-acl > data_backup.sql
```

### Analyze Performance

```sql
-- Check slow queries
SELECT * FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- Check table sizes
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Additional Resources

- [Supabase RLS Documentation](https://supabase.com/docs/guides/auth/row-level-security)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Project Security Guide](../docs/architecture/SECURITY.md)

---

**Last Updated**: November 2024
**Maintained By**: Island Glass Development Team
