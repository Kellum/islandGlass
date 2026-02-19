# Next Session Prompt

**Last Updated:** 2026-02-19
**Focus Area:** Wholesale pricing verification / Calculator accuracy

## What's Been Done
- Diagnosed calculator pricing issue: seed data had retail-level prices being treated as wholesale, then marked up again by ÷ 0.28
- Confirmed correct wholesale costs: 1/4" clear = $3.45 (annealed) / $4.05 (tempered), polish = $0.07/inch
- Employees are actively updating all glass type/thickness wholesale costs via admin panel
- Added sortable columns to glass config table (thickness, type, base price, polish price, supplier)
- Built full suppliers management system: suppliers table, admin CRUD tab, supplier dropdown on glass config
- Initial suppliers: Crystal Tempering, M & F, Aldora, Cardinal

## What to Do Next
1. **Verify pricing** — Once employees finish updating wholesale costs, test the calculator with known prices to confirm accuracy
2. **Tempered markup** — Owner needs to set the flat tempered % (currently 35%, real values are 10-17% depending on thickness, but owner pads it higher for goodwill discounts)
3. **Consider per-thickness tempered pricing** — If flat % is too inaccurate, may need to store separate annealed/tempered base prices per thickness instead of a single percentage
4. **Visual QA** — Dark mode across all pages still needs browser testing
5. **Multi-tenant migrations** — Database migrations 013-021 are staged but not applied

## Recently Changed Files
- `src/components/admin/GlassConfigTable.tsx` (sortable columns + supplier dropdown)
- `src/components/admin/AdminPanel.tsx` (Suppliers tab)
- `src/components/admin/SuppliersTable.tsx` (new — supplier CRUD)
- `src/services/adminApi.ts` (supplier CRUD functions)
- `src/types/index.ts` (SupplierRow, supplier_id on GlassConfigRow)
- `supabase/schema.sql` (suppliers table, supplier_id FK)
- `supabase/seed.sql` (initial suppliers)
