# Island Glass Seed Data Setup Instructions

## Overview
This will populate your database with all the pricing data, categories, and units needed for the Glass Calculator and Inventory Management features to work.

## Prerequisites

**CRITICAL:** You must run `complete_company_migration.sql` FIRST before running this seed data script!

### Quick Check: Has the migration been run?

Run `check_migration_status.sql` in Supabase SQL Editor to verify. You should see:
- ✅ companies table: EXISTS
- ✅ user_profiles.company_id column: EXISTS
- ✅ glass_config.company_id column: EXISTS
- ✅ Island Glass & Mirror company: EXISTS

If you see any ❌ MISSING messages, you need to run `complete_company_migration.sql` first!

### Other Prerequisites
- ✅ You have a user account created (you've logged into the app at least once)

## Step-by-Step Instructions

### Step 1: Get Your User ID

1. Open **Supabase Dashboard** → **SQL Editor**
2. Create a new query
3. Copy and paste the contents of `setup_company_data_PART1.sql`
4. Click **Run**
5. You'll see a table with your user account(s)
6. **Copy the `user_id`** value (it's a UUID like `abc-123-def-456...`)

Example output:
```
user_id                              | email                    | created_at
-------------------------------------|--------------------------|-------------
abc-123-def-456-ghi-789-jkl-012-345 | you@islandglass.com      | 2025-11-03
```

### Step 2: Prepare PART 2 Script

1. Open `setup_company_data_PART2.sql` in your text editor
2. Use **Find and Replace** (Cmd+F on Mac, Ctrl+F on Windows)
   - **Find:** `YOUR_USER_ID_HERE`
   - **Replace with:** Your actual UUID from Step 1 (paste it)
3. Click **Replace All**
4. You should see **8 replacements made**
5. Save the file

### Step 3: Run the Seed Data Script

1. Go back to **Supabase SQL Editor**
2. Create a new query
3. Copy and paste the **entire contents** of the modified `setup_company_data_PART2.sql`
4. Click **Run**
5. Wait for it to complete (should take 5-10 seconds)

### Step 4: Verify Success

Scroll to the bottom of the results panel. You should see a summary like this:

```
status          | glass_configs | markups | beveled_prices | corner_prices | categories | units
----------------|---------------|---------|----------------|---------------|------------|-------
Setup Complete! | 13            | 2       | 4              | 6             | 6          | 7
```

If you see these numbers, **SUCCESS!** 🎉

## What Just Happened?

Your database now has:

### Glass Calculator Data
- ✅ **13 glass configurations** - All thickness/type combinations with base prices
- ✅ **2 markups** - Tempered (35%) and Shape (25%) markups
- ✅ **4 beveled pricing records** - Pricing for beveled edges by thickness
- ✅ **6 clipped corner pricing records** - Pricing for corner clips

### Inventory Reference Data
- ✅ **6 inventory categories** - Spacers, Butyl, Desiccant, etc.
- ✅ **7 inventory units** - pieces, linear feet, pounds, etc.

### Company & User Setup
- ✅ **Island Glass & Mirror company record** created
- ✅ **Your user account linked to the company**
- ✅ **All data is company-scoped** (shared across all employees)
- ✅ **Audit trails set** (created_by tracks you as the creator)

## Testing the Results

### Test the Glass Calculator
1. Go to http://localhost:8050/calculator
2. You should now see dropdowns populated with:
   - Glass thicknesses (1/8", 3/16", 1/4", 3/8", 1/2")
   - Glass types (Clear, Bronze, Gray, Mirror)
   - Edge options (Flat Polish, Beveled)
3. Enter dimensions and generate a quote
4. It should calculate a price!

### Test Inventory Management
1. Go to http://localhost:8050/inventory
2. Click "Add Inventory Item"
3. You should see dropdowns populated with:
   - Categories (Spacers, Butyl, Desiccant, etc.)
   - Units (pieces, linear feet, pounds, etc.)
4. Add a test item to verify it works

## Troubleshooting

### Error: "violates foreign key constraint user_profiles_company_id_fkey"
**Problem:** The `companies` table doesn't exist yet, OR "Island Glass & Mirror" company wasn't created.

**Solution:**
1. Run `check_migration_status.sql` to verify migration status
2. If migration not run, go to Supabase SQL Editor and run `complete_company_migration.sql` FIRST
3. Wait for migration to complete (may take 30-60 seconds)
4. Then come back and run the seed data script

### Error: "invalid input syntax for type uuid"
- You forgot to replace `YOUR_USER_ID_HERE` with your actual UUID
- Go back to Step 2 and do the find/replace

### Error: "null value in column user_id violates not-null constraint"
- Same issue - you need to replace the placeholder with your real UUID
- Make sure you copied the UUID correctly (no extra spaces)

### No dropdowns showing in Calculator
- Run the verification queries at the bottom of PART2 script
- Check that all tables show data

### "Duplicate key value violates unique constraint"
- You've already run the script successfully before
- The data is already there, no need to run it again
- Check the app to verify the data is accessible

## Next Steps

After successfully running the seed data:

1. ✅ **Test CRUD operations** - Add/edit/delete clients and inventory items
2. ✅ **Test with multiple users** - Create another user account, verify they see the same pricing
3. ✅ **Start using the features** - Create real clients, generate quotes, track inventory
4. ✅ **Build Phase 2 features** - PO details, client details, activity logging

## Questions?

If you run into issues:
1. Check the Supabase logs for detailed error messages
2. Verify the migration script ran successfully first
3. Double-check you replaced ALL instances of `YOUR_USER_ID_HERE`
4. Make sure you're using the UUID from auth.users, not some other ID

---

**Happy quoting!** 🪟✨
