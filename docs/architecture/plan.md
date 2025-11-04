# Island Glass Leads CRM - Project Plan

**Created**: October 15, 2025
**Last Updated**: November 3, 2025 (Session 11)
**Status**: Window Manufacturing System Planned - Ready to Build

---

## Project Overview

**Purpose**: Comprehensive CRM system combining contractor lead generation (Island Glass Leads) with glass manufacturing/pricing management (GlassPricePro integration).

**Goals**:
1. **Lead Generation**: Automate contractor discovery, AI-powered enrichment, personalized outreach
2. **Manufacturing**: Glass pricing calculator, client/PO management, inventory tracking
3. **Unified System**: Single platform for sales team and manufacturing operations

**Current Stage**: Phase 1 Complete - All core features working in production

---

## Tech Stack

### Backend
- **Database**: Supabase (PostgreSQL) with Row Level Security (RLS)
- **Language**: Python 3.9.6
- **API Integrations**:
  - Google Places API (contractor discovery)
  - Anthropic Claude API (enrichment, outreach generation)
- **Authentication**: Supabase Auth with JWT tokens
- **Deployment**: Railway (planned)

### Frontend
- **Framework**: Dash 3.2.0 + Dash Mantine Components 2.3.0
- **Icons**: Dash Iconify (Solar icon set)
- **Theme**: Mantine light theme with Inter font
- **State Management**: dcc.Store (session storage)
- **Routing**: dcc.Location (client-side)

### Key Libraries
- `supabase` - Database client
- `anthropic` - Claude API client
- `dash`, `dash-mantine-components`, `dash-iconify` - UI framework
- `gunicorn` - Production server
- `pandas` - Data processing
- `aiohttp` - Async HTTP for enrichment

---

## Database Schema

### Original CRM Tables

**contractors** (main table)
- Contact info: company_name, phone, email, website, address, city, state
- Lead data: lead_score (1-10), lead_score_reasoning
- Enrichment: specializations, glazing_opportunities, use_subcontractors, profile_notes, outreach_angle
- Metadata: company_type, source, created_at, user_id

**outreach_emails**
- contractor_id (FK), subject_line, email_content, created_at

**call_scripts**
- contractor_id (FK), script_content, created_at

**interactions**
- contractor_id (FK), status, notes, user_name, timestamp, user_id

**api_usage**
- contractor_id (FK), action_type, model, input_tokens, output_tokens, total_tokens, estimated_cost, success, timestamp

**user_profiles**
- user_id (FK to auth.users), full_name, role, preferences

### GlassPricePro Tables (NEW)

**Glass Calculator:**
- `glass_config` - Base pricing matrix (thickness × type)
- `markups` - Tempered %, Shape % markups
- `beveled_pricing` - Beveled edge rates by thickness
- `clipped_corners_pricing` - Corner clipping rates

**PO Tracker:**
- `po_clients` - Customer/client information
- `po_purchase_orders` - Purchase orders
- `po_activities` - Activity logging (calls, emails, meetings)

**Inventory:**
- `inventory_items` - Inventory items with quantities
- `inventory_categories` - Categories (Spacers, Butyl, etc.)
- `inventory_units` - Units (pieces, feet, pounds, etc.)
- `suppliers` - Supplier information

All tables have RLS enabled with user_id isolation.

---

## Current Features (Phase 1 - COMPLETE ✅)

### Island Glass Leads CRM

#### 1. Dashboard (`/`)
- Total contractors count
- High priority leads (score 8+)
- Recent activity feed
- Lead score distribution chart
- Quick action cards

#### 2. Contractors Directory (`/contractors`)
- Card-based view with company info
- Search by name
- Filter by city, company type
- Lead score badges (color-coded)
- Detail modal with 4 tabs:
  - Contact: Full contact information
  - Profile: Enrichment data, specializations
  - Outreach: Generated emails and call scripts
  - Activity: Interaction history

#### 3. Discovery (`/discovery`)
- Google Places API search
- Search templates (e.g., "bathroom remodeler in Jacksonville, FL")
- Duplicate detection (checks existing contractors)
- Batch import from search results
- City, state, company type configuration

#### 4. Enrichment (`/enrichment`)
- Bulk website enrichment using Claude AI
- Automated lead scoring (1-10)
- Specialization detection
- Glazing opportunity analysis
- Subcontractor usage detection
- Progress tracking with queue display
- Error handling and retry logic

#### 5. Bulk Actions (`/bulk-actions`)
- CSV export with multiple scopes:
  - All contractors
  - High priority leads
  - By city
  - By company type
  - Unenriched only
- Customizable column selection

#### 6. Import Contractors (`/import`)
- Manual entry form
- CSV bulk upload
- Preview and validation
- Duplicate detection
- Batch processing

#### 7. Settings (`/settings`)
- API usage tracking
- Cost monitoring (per action, per contractor)
- Database statistics
- User profile management

#### 8. Authentication (`/login`)
- Email/password login
- User registration
- Session management
- RLS-protected data

### GlassPricePro Features (NEW ✅)

#### 9. Glass Calculator (`/calculator`)
- Dimension inputs with fraction support ("24 1/2", "3/4")
- Glass types: Clear, Bronze, Gray, Mirror
- Thickness: 1/8", 3/16", 1/4", 3/8", 1/2"
- Shapes: Rectangular, Circular, Non-Rectangular
- Edge processing:
  - Polish (standard or flat for mirrors)
  - Beveled (not available for 1/8")
  - Clipped corners (1-4, under/over 1")
- Tempered markup (35%)
- Shape markup (25%)
- Contractor discount (15%)
- Real-time price breakdown
- **ULTIMATE FORMULA: Quote Price = Total ÷ 0.28**

#### 10. PO Tracker (`/po-clients`)
- Client management with card view
- Company, contact, location tracking
- PO count per client
- Search by company/contact name
- Filter by city and client type
- Add/edit/delete clients
- Client type badges (contractor, residential, commercial)

#### 11. Inventory Management (`/inventory`)
- Track IGU manufacturing supplies
- Category-based organization
- Quantity tracking with custom units
- Cost per unit and total value calculation
- Low stock alerts (red badge when qty < threshold)
- Category filtering
- Sortable table view
- Add/edit/delete items

---

## Roadmap

### ✅ Phase 1: Core CRM (COMPLETE)
**Status**: All features working in production
- [x] Database setup (Supabase)
- [x] Google Places API integration
- [x] Claude AI enrichment
- [x] Lead scoring system
- [x] Outreach generation
- [x] Dash Mantine UI
- [x] Dashboard page
- [x] Contractors directory
- [x] Discovery page
- [x] Enrichment page
- [x] Bulk actions
- [x] Import contractors
- [x] Settings page
- [x] Authentication & RLS
- [x] Session management

### ✅ Phase 1.5: GlassPricePro Integration (COMPLETE)
**Status**: Prototype complete, ready for testing
- [x] Database migration (11 new tables)
- [x] Fraction utilities module
- [x] Glass calculator logic
- [x] Database methods (40+ new)
- [x] Glass Calculator page
- [x] PO Tracker page
- [x] Inventory Management page
- [x] Navigation integration
- [x] Authentication integration
- [x] Testing & bug fixes

### 🚀 Phase 1.6: Window Manufacturing System (IMMEDIATE - Session 12)
**Target**: 1 session (6-8 hours)
**Priority**: CRITICAL
**Status**: Fully planned, ready to implement

#### Overview
Complete window ordering and Zebra label printing system with role-based access control.

#### Components to Build
1. **User Role System** (30 min)
   - Extend user_profiles with department column
   - Update role values (owner, admin, manufacturing_admin, employee)
   - Create permissions.py access control helper

2. **Database Schema** (45 min)
   - window_orders table (PO, customer, status)
   - window_order_items table (specs, quantity)
   - window_labels table (ZPL, print status, history)
   - label_printer_config table (printer settings)
   - All with company_id scoping and audit trails

3. **Backend Modules** (1-1.5 hrs)
   - Extend database.py with window CRUD methods
   - zpl_generator.py for Zebra label generation
   - label_printer.py for network printing (mock mode)
   - Fuzzy matching for customer autocomplete

4. **UI Pages** (2-3 hrs)
   - window_order_entry.py - Multi-window order form with fractions
   - window_order_management.py - Order dashboard
   - window_label_printing.py - Print queue and history

5. **Access Control** (30 min)
   - Role-based navigation filtering
   - Protected routes
   - Permission checks in callbacks

#### Key Features
- ✅ Multi-window orders under single PO
- ✅ Fraction measurement support (1 1/2", 36 1/4")
- ✅ Customer autocomplete with "did you mean" suggestions
- ✅ ZPL label generation for Zebra ZD421 (3x2" labels)
- ✅ 1 label per physical window (4 windows = 4 labels)
- ✅ Print queue with batch printing
- ✅ Print history tracking
- ✅ Optional link to po_clients table
- ✅ QuickBooks integration placeholder

#### User Access
- **Owners**: Everything app-wide
- **Manufacturing Admin**: All window features + other sections
- **IG Admin**: Everything except window manufacturing
- **IG Employee**: Window order entry only
- **Sales** (future): CRM only

See `SESSION_11_WINDOW_MANUFACTURING_PLAN.md` for complete specification.

### 🔄 Phase 2: GlassPricePro Expansion (DEFERRED)
**Target**: 2-3 weeks
**Priority**: Medium (after window system)

#### High Priority
1. **PO Detail Pages** (Est: 2-3 days)
   - Full purchase order view
   - Line items with glass calculations
   - Status tracking (quoted, ordered, in production, completed, invoiced)
   - Due date management
   - Notes and attachments
   - Print/export PO

2. **Client Detail Pages** (Est: 2-3 days)
   - Complete client profile
   - PO list with status
   - Activity timeline
   - Contact history
   - Notes system
   - Quick actions (call, email, add PO)

3. **Activity Logging System** (Est: 1-2 days)
   - Log calls, emails, meetings, notes
   - Activity timeline per client
   - Activity timeline per PO
   - Filter and search activities
   - Quick log from client/PO pages

4. **Admin Pricing Configuration** (Est: 2-3 days)
   - UI to edit glass_config table
   - Manage markups (tempered %, shape %)
   - Edit beveled pricing
   - Edit clipped corners pricing
   - Import/export pricing
   - Pricing history

#### Medium Priority
5. **Shopping Cart System** (Est: 3-4 days)
   - Add multiple items to quote
   - Edit quantities
   - Line item totals
   - Cart subtotal and total
   - Save cart to PO
   - Clear cart

6. **PDF Quote Generation** (Est: 2-3 days)
   - Professional quote template
   - Company logo and branding
   - Line items with descriptions
   - Pricing breakdown
   - Terms and conditions
   - Email PDF to client

7. **CRM Integration** (Est: 1-2 days)
   - Convert contractor → PO client
   - Link contractors to clients
   - Unified search across both
   - Cross-reference display

#### Low Priority (Optional)
8. **IGU Calculator** (Est: 4-5 days)
   - Insulated Glass Units calculator
   - Muntin/grid options
   - Glass pane selection
   - Spacer calculations
   - Integration with inventory

9. **Spacer Calculator** (Est: 2-3 days)
   - Cutting optimization
   - Minimize waste
   - Bar length management
   - Cut list generation

10. **Production Kanban** (Est: 5-7 days)
    - Drag-and-drop workflow board
    - Job cards with details
    - Status tracking
    - Notes and photos
    - Timeline view

### 🔮 Phase 3: Advanced Features (FUTURE)
**Target**: TBD

#### Analytics & Reporting
- Lead conversion tracking
- Sales pipeline reporting
- Revenue forecasting
- Activity reports
- Custom dashboards
- Export to Excel/PDF

#### Communication Integration
- Email integration (send from app)
- SMS notifications
- Calendar integration
- Reminders and tasks
- Automated follow-ups

#### Mobile & Performance
- Mobile-responsive improvements
- Offline mode
- Performance optimization
- Caching strategies

#### AI Enhancements
- Predictive lead scoring
- Automated follow-up suggestions
- Smart quote recommendations
- Inventory forecasting

---

## Development Guidelines

### Code Organization
- **Modules**: Business logic, external integrations
- **Pages**: Full-page layouts and callbacks
- **Components**: Reusable UI elements
- **Separation**: Keep UI and logic separate

### Database Patterns
- Always use RLS-enabled queries
- Use `get_authenticated_db(session_data)` for user-specific data
- Include `user_id` in all inserts
- Handle errors gracefully

### UI/UX Standards
- Use Dash Mantine Components v2.3.0 patterns
- Solar icon set for consistency
- Blue color scheme for primary actions
- Status-based color coding (green=success, red=danger, etc.)
- Responsive design (mobile, tablet, desktop)

### Authentication
- All pages require authentication (except /login)
- Use session-store for user data
- JWT tokens for Supabase RLS
- Logout clears session and redirects

---

## Testing Strategy

### Before Production
- [ ] Run database migration on staging Supabase
- [ ] Test all calculator formulas with real data
- [ ] Verify RLS policies work correctly
- [ ] Test all CRUD operations
- [ ] Verify low stock alerts
- [ ] Test fraction parsing edge cases
- [ ] Load test with 1000+ clients
- [ ] Cross-browser testing
- [ ] Mobile responsiveness

### User Acceptance Testing
- [ ] Sales team tests lead generation flow
- [ ] Manufacturing team tests calculator
- [ ] Admin tests pricing configuration
- [ ] Test data import/export
- [ ] Verify PDF generation (Phase 2)
- [ ] Test email integration (Phase 2)

---

## Deployment Plan

### Prerequisites
1. Supabase project configured
2. Google Places API key
3. Anthropic API key
4. Environment variables set

### Database Migration
1. Run `glassprice_migration.sql` in Supabase SQL Editor
2. Add seed data with actual user_id
3. Verify RLS policies
4. Test queries with authenticated user

### Application Deployment (Railway)
1. Connect GitHub repository
2. Configure environment variables
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn dash_app:server -b 0.0.0.0:$PORT`
5. Deploy and test

### Post-Deployment
1. Monitor error logs
2. Track API costs
3. Gather user feedback
4. Performance monitoring

---

## Cost Estimates

### Current API Costs
- **Claude Enrichment**: ~$0.03 per contractor
- **Claude Outreach**: ~$0.03 per contractor
- **Google Places**: Free tier (no billing yet)

### Projected Monthly Costs (Phase 2)
- **Claude API**: ~$50-100 (depending on usage)
- **PDF Generation**: Free (ReportLab) or ~$10 (paid service)
- **Supabase**: Free tier → Pro ($25/month) if needed
- **Railway Hosting**: ~$5-20/month

### Total Estimated: $80-155/month

---

## Success Metrics

### Lead Generation CRM
- [x] 72 contractors imported
- [x] AI enrichment working
- [x] Lead scoring automated
- [x] Outreach generation functional
- [ ] 90%+ user satisfaction
- [ ] <2s page load times
- [ ] Zero data loss

### GlassPricePro
- [x] Calculator accurate to 2 decimals
- [x] Fraction parsing 100% accurate
- [x] PO tracker functional
- [x] Inventory alerts working
- [ ] 50+ clients in system
- [ ] 200+ quotes generated
- [ ] PDF quotes working (Phase 2)

---

## Known Issues & Technical Debt

### Current Limitations
1. **No seed data yet** - Manual SQL required
2. **Basic UI on new pages** - Can be enhanced
3. **No PDF generation** - Planned for Phase 2
4. **No shopping cart** - Single item quotes only
5. **No PO detail pages** - List view only

### Technical Debt
- Refactor database.py (730+ lines)
- Add comprehensive error handling
- Improve loading states
- Add unit tests
- Document all callbacks
- Type hints consistency

### Performance Optimization
- Implement query caching
- Optimize large table loads
- Add pagination
- Lazy load modals
- Compress images

---

## Documentation

### Project Documentation
- `checkpoint.md` - Current status and session history
- `plan.md` - This file (roadmap and architecture)
- `MIGRATION_COMPLETE.md` - GlassPricePro setup guide
- `TECH_STACK_GUIDE.md` - Tech stack reference
- `GLASSPRICEPRO_MIGRATION_GUIDE.md` - Original migration plan

### Code Documentation
- Inline docstrings for all functions
- Type hints where applicable
- README files for complex modules
- Comments for business logic

### User Documentation (TODO)
- User manual
- Video tutorials
- FAQ
- Troubleshooting guide

---

## Team & Roles

### Development
- **Developer**: Claude Code (AI) + Ryan Kellum
- **Testing**: Sales team (4 people)
- **Feedback**: Manufacturing team

### Responsibilities
- **Sales Team**: Lead gen, enrichment, outreach
- **Manufacturing**: Quotes, POs, inventory
- **Admin**: Pricing config, user management

---

## Next Session Checklist

### Before Starting Work
1. ✅ Read `checkpoint.md` for current status
2. ✅ Review `plan.md` for roadmap
3. ✅ Check `MIGRATION_COMPLETE.md` for setup status
4. ⏳ Run database migration if not done
5. ⏳ Test new features

### During Session
1. Update todos with TodoWrite
2. Document changes in checkpoint.md
3. Update plan.md if roadmap changes
4. Commit frequently with clear messages

### End of Session
1. Update checkpoint.md with session summary
2. Archive old sessions if needed
3. Update plan.md with next steps
4. Document known issues

---

**Last Updated**: November 2, 2025
**Next Major Milestone**: Phase 2 - PO Detail Pages & Client Management
**Estimated Completion**: 2-3 weeks
