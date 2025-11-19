# Multi-Tenant Migration Guide

**Status:** Ready to apply
**Branch:** `feature/multi-tenant-saas`
**Migrations:** 013-021 (9 files)

---

## What These Migrations Do

Transform your Island Glass CRM from single-tenant to multi-tenant SaaS:

1. **Create companies table** - Core multi-tenant structure
2. **Create user_invitations table** - Team member onboarding
3. **Add company_id to users** - Multi-company auth support
4. **Add company_id to 4 critical tables** - Data isolation
5. **Seed Island Glass company** - Your foundational company record
6. **Backfill all data** - Assign existing data to your company

---

## Before You Start

### ⚠️ CRITICAL: Create Backup

1. Go to Supabase Dashboard → Database → Backups
2. Click "Create backup"
3. Download backup locally
4. Verify backup exists before proceeding

### Update Your Contact Info

Edit `020_seed_island_glass_company.sql` and update:
- Line 23: `primary_contact_email` - Your actual email
- Line 24: `primary_contact_phone` - Your actual phone number

---

## Option 1: Apply via Supabase Dashboard (Recommended)

### Step-by-Step

1. **Open Supabase SQL Editor**
   - Go to https://supabase.com/dashboard/project/dgsjmsccpdrgnnpzlsgj
   - Navigate to SQL Editor → New Query

2. **Run migrations in order (013-021)**

   **Migration 013:**
   ```sql
   -- Copy entire contents of database/migrations/013_create_companies_table.sql
   -- Paste into SQL Editor
   -- Click "Run"
   -- Verify: "Success. No rows returned"
   ```

   **Migration 014:**
   ```sql
   -- Copy entire contents of database/migrations/014_create_user_invitations_table.sql
   -- Paste and Run
   ```

   **Migration 015:**
   ```sql
   -- Copy entire contents of database/migrations/015_add_company_id_to_users.sql
   -- Paste and Run
   -- Should see trigger creation success
   ```

   **Migration 016:**
   ```sql
   -- Copy entire contents of database/migrations/016_add_company_id_to_contractors.sql
   -- Paste and Run
   ```

   **Migration 017:**
   ```sql
   -- Copy entire contents of database/migrations/017_add_company_id_to_api_usage.sql
   -- Paste and Run
   ```

   **Migration 018:**
   ```sql
   -- Copy entire contents of database/migrations/018_add_company_id_to_interaction_log.sql
   -- Paste and Run
   ```

   **Migration 019:**
   ```sql
   -- Copy entire contents of database/migrations/019_add_company_id_to_outreach_materials.sql
   -- Paste and Run
   ```

   **Migration 020 (IMPORTANT):**
   ```sql
   -- ⚠️ FIRST: Update your email and phone in this file!
   -- Copy entire contents of database/migrations/020_seed_island_glass_company.sql
   -- Paste and Run
   -- Should see: "Island Glass company created successfully"
   ```

   **Migration 021 (Finalizes everything):**
   ```sql
   -- Copy entire contents of database/migrations/021_backfill_company_ids.sql
   -- Paste and Run
   -- Should see: "Starting backfill...", "Updated X contractors", etc.
   -- Final message: "All company_id constraints verified successfully!"
   ```

3. **Verify Success**
   ```sql
   -- Check companies table
   SELECT * FROM companies;
   -- Should show Island Glass & Mirror

   -- Check contractors have company_id
   SELECT COUNT(*), company_id FROM contractors GROUP BY company_id;
   -- Should show 72 contractors with your company ID

   -- Check users have company_id
   SELECT user_id, email, company_id FROM users;
   -- Should show your users with company IDs
   ```

---

## Option 2: Apply via Supabase CLI

### Prerequisites
```bash
# Ensure you're on the feature branch
git checkout feature/multi-tenant-saas

# Supabase CLI already linked
npx supabase link --project-ref dgsjmsccpdrgnnpzlsgj
```

### Copy Migrations to Supabase Folder
```bash
# Copy each migration to supabase/migrations/ with timestamp
cd database/migrations/

# Generate timestamp
TIMESTAMP=$(date -u +"%Y%m%d%H%M%S")

# Copy migrations (one at a time to preserve order)
cp 013_create_companies_table.sql ../../supabase/migrations/${TIMESTAMP}_013_create_companies_table.sql
# Wait 1 second for new timestamp
sleep 1
TIMESTAMP=$(date -u +"%Y%m%d%H%M%S")
cp 014_create_user_invitations_table.sql ../../supabase/migrations/${TIMESTAMP}_014_create_user_invitations_table.sql
# ... repeat for each migration 015-021
```

### Push to Production
```bash
# Push all pending migrations
npx supabase db push

# This will apply migrations in order
# Watch for success messages
```

---

## After Migration: Verify Everything Works

### 1. Test Your App
```bash
# Start backend and frontend
cd backend && python3 -m uvicorn main:app --reload --port 8000
cd frontend && npm run dev

# Login to your app
# Browse clients, jobs, contractors
# Everything should still work normally
```

### 2. Database Checks
```sql
-- Verify all tables have RLS enabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('companies', 'users', 'contractors', 'api_usage', 'interaction_log', 'outreach_materials')
ORDER BY tablename;
-- All should show rowsecurity = true

-- Check data counts
SELECT
    'companies' as table_name, COUNT(*) as rows FROM companies
UNION ALL
SELECT 'users', COUNT(*) FROM users WHERE company_id IS NOT NULL
UNION ALL
SELECT 'contractors', COUNT(*) FROM contractors WHERE company_id IS NOT NULL
UNION ALL
SELECT 'api_usage', COUNT(*) FROM api_usage WHERE company_id IS NOT NULL
UNION ALL
SELECT 'interaction_log', COUNT(*) FROM interaction_log WHERE company_id IS NOT NULL
UNION ALL
SELECT 'outreach_materials', COUNT(*) FROM outreach_materials WHERE company_id IS NOT NULL;
```

---

## Rollback Plan (If Needed)

If something goes wrong:

### Emergency Rollback via Backup
1. Go to Supabase Dashboard → Database → Backups
2. Select the backup you created before migration
3. Click "Restore"
4. Wait for restore to complete
5. Verify app is working

### Manual Rollback via SQL
```sql
-- Drop tables in reverse order
DROP TABLE IF EXISTS user_invitations CASCADE;
DROP TABLE IF EXISTS companies CASCADE;

-- Remove company_id columns
ALTER TABLE contractors DROP COLUMN IF EXISTS company_id;
ALTER TABLE api_usage DROP COLUMN IF EXISTS company_id;
ALTER TABLE interaction_log DROP COLUMN IF EXISTS company_id;
ALTER TABLE outreach_materials DROP COLUMN IF EXISTS company_id;
ALTER TABLE users DROP COLUMN IF EXISTS company_id;

-- Disable RLS
ALTER TABLE contractors DISABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage DISABLE ROW LEVEL SECURITY;
ALTER TABLE interaction_log DISABLE ROW LEVEL SECURITY;
ALTER TABLE outreach_materials DISABLE ROW LEVEL SECURITY;
```

---

## Next Steps After Successful Migration

### Phase 1: Backend Updates (Next Session)
Update Python backend code:
- Add `company_id` to JWT tokens
- Filter all queries by `company_id`
- Create company signup endpoint
- Create invitation endpoints

### Phase 2: Frontend Updates
- Build company signup page
- Build invitation management UI
- Update login flow

### Phase 3: Testing
- Create test company
- Verify data isolation
- Test invitation flow

---

## Reference

**Island Glass Company UUID:** `720d425e-bb02-4612-9b35-70bded465dca`
- Use this UUID in backend code
- All existing data now linked to this company
- Future companies will get new UUIDs

**Migration Sequence:** 013 → 014 → 015 → 016 → 017 → 018 → 019 → 020 → 021

**Important:** Migrations 013-020 can be run safely even if they partially fail. Migration 021 should only run AFTER migration 020 succeeds (company record must exist).

---

## Troubleshooting

### "Company not found" error during backfill (021)
- Migration 020 didn't run successfully
- Run migration 020 first
- Verify: `SELECT * FROM companies WHERE id = '720d425e-bb02-4612-9b35-70bded465dca'`

### "Column already exists" error
- Migration was partially applied before
- Check which columns exist: `\d contractors` in psql
- Either skip that migration or drop the column first

### RLS blocking your queries
- RLS is enabled but app code not updated yet
- Temporary fix: Disable RLS on specific table for testing
- Permanent fix: Update backend code to set `app.company_id` context

---

**Created:** 2025-11-19
**Author:** Claude Code
**Branch:** `feature/multi-tenant-saas`
**Status:** ✅ Ready to apply
