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

## 📚 Documentation for Developers

**NEW DEVELOPERS - START HERE:**

1. **[QUICK_START.md](QUICK_START.md)** ⭐ - **Get running in 5 minutes! (READ FIRST!)**
2. **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - **Complete tech stack & architecture guide**
3. **[checkpoint.md](checkpoint.md)** - Current project status and recent changes

**Additional Resources:**

- **[ARCHITECTURE_RULES.md](ARCHITECTURE_RULES.md)** - Code patterns and best practices
- **[docs/README.md](docs/README.md)** - Complete documentation index
- **[backend/README.md](backend/README.md)** - Backend API reference

### Quick Links by Task

| Task | Document |
|------|----------|
| **Writing new code** | [ARCHITECTURE_RULES.md](ARCHITECTURE_RULES.md) |
| **Debugging an issue** | [docs/TROUBLESHOOTING_LOG.md](docs/TROUBLESHOOTING_LOG.md) |
| **Learning patterns** | [docs/LESSONS_LEARNED.md](docs/LESSONS_LEARNED.md) |
| **Daily commands** | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| **Understanding Jobs/PO** | [docs/REVISED_PO_SYSTEM_SUMMARY.md](docs/REVISED_PO_SYSTEM_SUMMARY.md) |

---

## Quick Start

**⚡ Get started in 5 minutes - see [QUICK_START.md](QUICK_START.md)**

### Prerequisites
- Node.js 18+
- Python 3.9+
- Supabase account

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Kellum/islandGlass.git
   cd islandGlassLeads
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Start Frontend** (Terminal 1)
   ```bash
   cd frontend
   npm install
   npm run dev
   # → http://localhost:5173
   ```

4. **Start Backend** (Terminal 2)
   ```bash
   cd backend
   python3 -m uvicorn main:app --reload --port 8000
   # → http://localhost:8000
   # API docs → http://localhost:8000/docs
   ```

5. **Open in browser**

   Navigate to http://localhost:5173 and log in with your Supabase credentials

**For complete setup instructions, see [QUICK_START.md](QUICK_START.md)**

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

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React 19 + TypeScript |
| Build Tool | Vite |
| Styling | Tailwind CSS v3 |
| State Management | React Query |
| Routing | React Router v6 |
| HTTP Client | Axios |

### Backend
| Component | Technology |
|-----------|-----------|
| Framework | FastAPI (Python 3.9+) |
| Database | Supabase (PostgreSQL) |
| Authentication | JWT Tokens |
| Validation | Pydantic |
| API Docs | Swagger UI (auto-generated) |

### Infrastructure
| Component | Technology |
|-----------|-----------|
| Database | PostgreSQL (via Supabase) |
| Security | Row-Level Security (RLS) |
| Hosting | Supabase (database), TBD (app) |

**For detailed tech stack explanation, see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)**

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

**Phase**: Full-Stack React/FastAPI Application - Session 44 Complete ✅

**Frontend Features Complete:**
- ✅ React 19 + TypeScript + Tailwind CSS
- ✅ Authentication (Login/Logout with JWT)
- ✅ Dashboard with metrics
- ✅ Jobs list and detail pages
- ✅ Clients management
- ✅ Vendors management
- ✅ Schedule/Calendar view
- ✅ **Glass Price Calculator** (NEW! - Session 44)
- ✅ Responsive navigation with sidebar

**Backend API Complete:**
- ✅ 11 Production-Ready APIs (127 tests passing)
- ✅ FastAPI with auto-generated docs
- ✅ JWT authentication
- ✅ Full CRUD for all entities
- ✅ **Calculator config endpoint** (NEW! - Session 44)

**Documentation Complete:**
- ✅ **DEVELOPER_GUIDE.md** - Complete tech stack guide (NEW!)
- ✅ **QUICK_START.md** - 5-minute setup guide (NEW!)
- ✅ Backend README with API documentation
- ✅ Checkpoint tracking all sessions

**Next Steps:**
- ⏳ Create/Edit modals for all entities
- ⏳ File upload functionality
- ⏳ Enhanced job detail page with tabs
- ⏳ Production deployment

See [checkpoint.md](checkpoint.md) for latest session details.

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

**Current Version**: 0.95.0 (Window Manufacturing System - Ready for Testing)

**Last Updated**: November 4, 2024
