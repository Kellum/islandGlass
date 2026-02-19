# Session: February 19, 2026 - Pricing Fix & Suppliers System

## Session Goals
- Diagnose why the glass calculator was producing wildly incorrect prices (~$900 instead of ~$112 for a 30x30 1/4" tempered polished piece)
- Add sortable columns to the admin glass config table
- Add a suppliers management system for internal tracking of glass sources

## Work Completed

### Pricing Investigation
- Traced the full calculation formula step-by-step for 1/4" clear, 30x30, tempered, polished
- Identified root cause: seed data had **retail-level** base prices ($12.50/sqft) and polish prices ($0.85/inch) being treated as **wholesale** costs, then marked up again by ÷ 0.28
- Confirmed the code formula is correct — all wholesale math happens first, then ÷ 0.28 at the end
- Established correct wholesale values: 1/4" clear base = $4.05/sqft (tempered) / $3.45 (annealed), polish = $0.07/inch
- Calculated tempered markup percentages: 17.4% for 1/4" ($3.45→$4.05), 10.3% for 3/8" ($5.80→$6.40)
- Owner prefers a flat average tempered % (padded higher to cover freebies/goodwill discounts)

### Sortable Glass Config Table (`GlassConfigTable.tsx`)
- Added click-to-sort on Thickness, Type, Base $/sqft, Polish $/in columns
- Three-state toggle: ascending → descending → clear
- Thickness sorts by actual size order (1/8"→1/2"), not alphabetical
- Sort icons from lucide-react (ArrowUp, ArrowDown, ArrowUpDown)

### Suppliers System (new feature)
- Created `suppliers` table in Supabase (id, name, created_at)
- Added `supplier_id` foreign key to `glass_config` table
- Built full CRUD API with audit logging (`adminApi.ts`)
- Created `SuppliersTable.tsx` admin component with add/edit/delete
- Added "Suppliers" tab to admin panel
- Added sortable Supplier dropdown column to glass config table
- Initial suppliers: Crystal Tempering, M & F, Aldora, Cardinal

## Key Decisions
- **Pricing data is the problem, not the formula** — The ÷ 0.28 markup formula is correct; employees are updating wholesale costs through the admin panel
- **Flat tempered %** kept in settings — Owner prefers a single averaged percentage (padded for goodwill) rather than per-thickness rates
- **Suppliers as a separate table** — Instead of hardcoding supplier names, created a manageable table with its own admin tab so the list can grow without code changes
- **supplier_id on glass_config** — Foreign key approach allows clean sorting and future querying by supplier

## Challenges & Solutions
- **npm/rollup native module issue** — `@rollup/rollup-win32-x64-msvc` was missing after initial install. Fixed by deleting `node_modules` + `package-lock.json` and running `npm i` fresh
- **Flat polish rate confusion** — The code only uses `flat_polish_rate` for mirrors (via `is_flat = glass_type === 'mirror'`). For non-mirror glass, it uses `polish_price` from `glass_config`. User updated the DB value directly.

## Current State
- App running locally at localhost:5173
- Suppliers table created in Supabase with 4 initial suppliers
- `supplier_id` column added to `glass_config` in Supabase
- Admin panel has 5 tabs: Wholesale Pricing, Markup Formula, Edge Work, Suppliers, Audit Log
- Employees are actively updating wholesale costs in the admin panel
- All changes committed and pushed to GitHub

## Next Steps
- Employees finish entering correct wholesale costs for all glass types/thicknesses
- Owner sets the tempered markup % to desired value via admin panel
- Verify calculator produces correct quotes with updated wholesale data
- Consider per-thickness tempered pricing if flat % proves too inaccurate

## Files Modified
- `src/components/admin/GlassConfigTable.tsx` — sortable columns + supplier dropdown
- `src/components/admin/AdminPanel.tsx` — added Suppliers tab
- `src/components/admin/SuppliersTable.tsx` — **new file**, supplier CRUD UI
- `src/services/adminApi.ts` — supplier CRUD functions with audit logging
- `src/types/index.ts` — added SupplierRow type, supplier_id to GlassConfigRow
- `supabase/schema.sql` — suppliers table, supplier_id FK on glass_config, RLS policies
- `supabase/seed.sql` — initial 4 suppliers
