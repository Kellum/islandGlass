# Island Glass Calculator - Project Status

**Last Updated:** 2026-02-19
**Latest Session:** [2026-02-19 - Pricing Fix & Suppliers](sessions/2026-02-19-pricing-fix-and-suppliers.md)

## Tech Stack
- **Frontend:** React 19.2, TypeScript 5.9, Vite 7.3, Tailwind CSS v4, Framer Motion
- **Backend:** Supabase (PostgreSQL + Auth + RLS)
- **Deployment:** Netlify (auto-deploy from `main` branch)
- **Repo:** https://github.com/Kellum/islandGlass.git

## Feature Status Matrix

| Feature | Status | Notes |
|---------|--------|-------|
| Glass Calculator | Done | Full pricing with shapes, edge processing, tempered |
| Quote Management | Done | Save, list, detail view, PDF export |
| Admin Panel | Done | PIN-gated, markup/glass config/edge pricing/suppliers/audit log |
| Suppliers Management | Done | CRUD in admin panel, linked to glass config |
| Sortable Admin Tables | Done | Glass config table columns sortable asc/desc |
| Markup Settings | Done | Plain-English UI with percentage/dollar toggle |
| Dark Mode | Done | All 30+ components, localStorage persistence, system pref default |
| Netlify Deployment | Done | Auto-deploy from main, SPA routing |
| Multi-Tenant DB Migrations | Staged | Migrations 013-021 written but not yet applied |
| Client/Job/Vendor CRUD | Staged | Backend routers exist in feature branch history |

## Active TODO List
- [ ] Employees finish entering correct wholesale costs for all glass types/thicknesses
- [ ] Owner sets tempered markup % to desired value via admin panel
- [ ] Verify calculator produces correct quotes with updated wholesale data
- [ ] Visual QA dark mode across all pages in browser
- [ ] Apply multi-tenant database migrations (013-021)
- [ ] Build out multi-tenant features (company switching, user invitations)
- [ ] Add remaining CRUD pages (Clients, Jobs, Vendors, Schedule)

## Known Issues
- Large chunk warning on build (`react-pdf.browser` is 1.5MB) — consider lazy loading
- No server-side rendering — dark mode may flash on very slow connections (mitigated by inline script)

## Recent Session Summary

| Date | Summary |
|------|---------|
| 2026-02-19 | Diagnosed pricing formula issue (wrong wholesale data), added sortable glass config columns, built suppliers management system with admin CRUD |
| 2026-02-13 | Redesigned markup settings UI, added percentage toggle, deployed to Netlify, added full dark mode across 30+ components |
