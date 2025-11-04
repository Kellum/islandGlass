# Island Glass CRM

A comprehensive CRM system for glass contractors featuring lead generation, client management, window manufacturing order management, and automated label printing.

![Project Status](https://img.shields.io/badge/status-70%25%20complete-yellow)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![Dash](https://img.shields.io/badge/framework-Dash-blue)
![Supabase](https://img.shields.io/badge/database-Supabase-green)

---

## Features

### Contractor Lead Generation
- Multi-source discovery (Google Places API)
- AI-powered enrichment (Claude)
- Automated outreach generation
- Lead scoring and tracking

### Client Management
- PO client database
- Dynamic forms (Residential vs Commercial)
- Multiple contacts per client
- Interaction history tracking

### Window Manufacturing System
- Order entry with multi-window support
- Fraction-based measurements (1 1/2", 3/4")
- Automated ZPL label generation
- Zebra printer integration
- Order status tracking

### Glass Price Calculator
- Material cost calculations
- Custom pricing formulas
- Inventory management
- Square footage tracking

### Security & Access Control
- Row-Level Security (RLS) via Supabase
- Role-based permissions (Admin, Manager, Sales, Production)
- Department-based filtering
- Secure authentication

---

## Quick Start

### Prerequisites
- Python 3.9 or higher
- Supabase account
- API Keys: Anthropic, Google Places (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Kellum/islandGlass.git
   cd islandGlass
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your credentials:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key-here
   GOOGLE_PLACES_API_KEY=your-google-key-here
   ```

4. **Set up database**

   Run migrations in your Supabase SQL Editor (in order):
   - `database/migrations/001_initial_schema.sql`
   - `database/migrations/002_user_roles_departments.sql`
   - `database/migrations/003_window_manufacturing.sql`
   - `database/migrations/004_window_seed_data.sql`

   See [database/README.md](database/README.md) for detailed instructions.

5. **Run the application**
   ```bash
   python3 dash_app.py
   ```

6. **Open in browser**

   Navigate to http://localhost:8050

---

## Project Structure

```
islandGlass/
├── README.md                    # You are here
├── CONTRIBUTING.md              # Developer guide
├── dash_app.py                  # Main application entry point
├── requirements.txt             # Python dependencies
│
├── modules/                     # Business logic
│   ├── auth.py                 # Authentication
│   ├── database.py             # Supabase operations
│   ├── permissions.py          # Access control
│   ├── glass_calculator.py     # Pricing calculations
│   ├── zpl_generator.py        # Label generation
│   ├── label_printer.py        # Printer interface
│   ├── enrichment.py           # AI enrichment
│   ├── outreach.py             # Email generation
│   └── scraper.py              # Lead discovery
│
├── pages/                       # UI pages
│   ├── login.py                # Authentication
│   ├── dashboard.py            # Main dashboard
│   ├── contractors.py          # Lead management
│   ├── po_clients.py           # Client management
│   ├── window_order_entry.py   # Order creation
│   ├── inventory_page.py       # Inventory
│   └── calculator.py           # Price calculator
│
├── components/                  # Reusable UI components
├── database/                    # Database files
│   ├── migrations/             # SQL migrations
│   ├── utilities/              # Helper queries
│   └── archive/               # Historical files
│
├── docs/                        # Documentation
│   ├── sessions/               # Progress notes
│   ├── architecture/           # Technical docs
│   └── archive/               # Historical docs
│
├── tests/                       # Test files
└── labels_output/              # ZPL label output
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | Dash (Plotly) |
| UI Library | Dash Mantine Components |
| Database | Supabase (PostgreSQL) |
| Security | Row-Level Security (RLS) |
| AI/ML | Anthropic Claude |
| APIs | Google Places, Zebra ZPL |
| Language | Python 3.9+ |
| Deployment | Railway (optional) |

---

## Usage

### First Time Setup

1. **Create your company record**
   - Log in with Supabase credentials
   - System will prompt for company setup
   - Add user profile information

2. **Configure settings**
   - Navigate to Settings page
   - Set up API keys
   - Configure email templates
   - Customize pricing formulas

3. **Import initial data** (optional)
   - Use Import page for bulk contractor upload
   - CSV format supported
   - Automatic deduplication

### Daily Workflow

**For Sales Team:**
1. Discover new leads via Discovery page
2. Enrich with AI-powered insights
3. Generate personalized outreach
4. Track interactions and responses

**For Production Team:**
1. Create window orders via Order Entry
2. Review orders in Order Management
3. Print labels via Label Printing page
4. Update order status as work progresses

**For Managers:**
1. Monitor dashboard metrics
2. Review team activity
3. Manage clients and contacts
4. Oversee order pipeline

---

## Development

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guide.

**Quick reference:**
```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and test
python3 dash_app.py

# Run tests
python -m pytest tests/

# Commit and push
git commit -m "Add my feature"
git push origin feature/my-feature
```

### Current Status

**Phase**: Window Manufacturing System (70% complete)

**Completed:**
- ✅ Contractor lead generation
- ✅ AI enrichment & outreach
- ✅ PO client management
- ✅ Window order entry
- ✅ Glass calculator
- ✅ Label generation (ZPL)
- ✅ Authentication & RLS

**In Progress:**
- ⏳ Window Order Management page
- ⏳ Label Printing page
- ⏳ Navigation integration

See [docs/sessions/SESSION_13_START_HERE.md](docs/sessions/SESSION_13_START_HERE.md) for current session details.

---

## Documentation

### For Developers
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide
- [docs/architecture/TECH_STACK_GUIDE.md](docs/architecture/TECH_STACK_GUIDE.md) - Technical overview
- [database/README.md](database/README.md) - Database guide
- [docs/architecture/SECURITY.md](docs/architecture/SECURITY.md) - Security implementation

### For Users
- [docs/architecture/SETUP_INSTRUCTIONS.md](docs/architecture/SETUP_INSTRUCTIONS.md) - Initial setup
- [docs/architecture/CRUD_TESTING_GUIDE.md](docs/architecture/CRUD_TESTING_GUIDE.md) - Feature testing

### Project History
- [docs/sessions/](docs/sessions/) - Session-by-session progress
- [docs/architecture/](docs/architecture/) - Technical decisions

---

## Features in Detail

### Lead Generation
- **Discovery**: Search contractors by location/specialty
- **Enrichment**: AI analyzes websites for insights
- **Scoring**: Automatic lead quality assessment
- **Outreach**: Generate personalized emails and scripts

### Window Manufacturing
- **Order Entry**: Multi-window forms with fraction support
- **Label Printing**: Automated ZPL generation for Zebra printers
- **Tracking**: Order status workflow (Pending → Production → Complete)
- **Inventory**: Glass type and thickness management

### Permissions System
- **Roles**: Admin, Manager, Sales, Production
- **Departments**: Sales, Production, Accounting
- **Granular Access**: Page-level and feature-level controls
- **RLS**: Database-level security via Supabase

---

## Deployment

### Railway (Recommended)

1. Connect GitHub repository
2. Configure environment variables
3. Deploy automatically on push

See [docs/architecture/production_ready_plan.md](docs/architecture/production_ready_plan.md) for detailed deployment guide.

### Manual Deployment

Requirements:
- Python 3.9+ runtime
- PostgreSQL database (or Supabase)
- Environment variable support

---

## Support

### Common Issues

**"Not authenticated" errors**
- Ensure session_data is passed to page layouts
- Check Supabase credentials in .env

**Empty database queries**
- Verify RLS policies are active
- Check company_id is being passed correctly

**Import errors**
- Run from project root directory
- Verify all dependencies installed

### Getting Help

- Check [CONTRIBUTING.md](CONTRIBUTING.md) for development questions
- Review [docs/architecture/](docs/architecture/) for technical details
- See [docs/sessions/](docs/sessions/) for context on features

---

## License

Proprietary - Island Glass

---

## Acknowledgments

Built with:
- [Dash by Plotly](https://dash.plotly.com/)
- [Dash Mantine Components](https://www.dash-mantine-components.com/)
- [Supabase](https://supabase.com/)
- [Anthropic Claude](https://www.anthropic.com/)
- [Google Places API](https://developers.google.com/maps/documentation/places)

---

**Current Version**: 0.7.0 (Window Manufacturing System in progress)

**Last Updated**: November 2024
