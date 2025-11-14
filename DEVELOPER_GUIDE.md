# Island Glass CRM - Developer Guide

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Getting Started](#getting-started)
5. [Frontend Development](#frontend-development)
6. [Backend Development](#backend-development)
7. [How Frontend & Backend Work Together](#how-frontend--backend-work-together)
8. [Common Tasks](#common-tasks)
9. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

Island Glass CRM is a **full-stack web application** with a clear separation between frontend and backend:

```
┌─────────────────────────────────────────────────────────────┐
│                         BROWSER                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           React Frontend (Port 5173)                 │   │
│  │  - TypeScript + React 19                             │   │
│  │  - Tailwind CSS for styling                          │   │
│  │  - User interface components                         │   │
│  └────────────────┬────────────────────────────────────┘   │
└───────────────────┼─────────────────────────────────────────┘
                    │ HTTP Requests (axios)
                    │ GET /api/v1/jobs, POST /api/v1/clients, etc.
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              REST API Server                         │   │
│  │  - Python + FastAPI                                  │   │
│  │  - JWT Authentication                                │   │
│  │  - Business logic & validation                       │   │
│  └────────────────┬────────────────────────────────────┘   │
└───────────────────┼─────────────────────────────────────────┘
                    │ SQL Queries
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              Supabase (PostgreSQL)                           │
│  - Database storage                                          │
│  - Row-Level Security (RLS)                                  │
│  - Authentication provider                                   │
└─────────────────────────────────────────────────────────────┘
```

### Key Concepts

**Frontend (React)**
- Runs in the user's browser
- Displays the user interface
- Handles user interactions (clicks, form inputs)
- Makes HTTP requests to the backend API
- Does NOT directly access the database

**Backend (FastAPI)**
- Runs on a server (your local machine during development)
- Provides REST API endpoints (URLs that the frontend calls)
- Handles authentication and authorization
- Performs business logic and data validation
- Directly communicates with the database

**Database (Supabase/PostgreSQL)**
- Stores all application data (clients, jobs, users, etc.)
- Only the backend can directly access it
- Ensures data integrity and security

---

## Tech Stack

### Frontend Technologies

| Technology | Purpose | Why We Use It |
|------------|---------|---------------|
| **React 19** | UI framework | Build interactive user interfaces with components |
| **TypeScript** | Programming language | Add type safety to JavaScript, catch bugs early |
| **Vite** | Build tool | Fast development server with Hot Module Replacement |
| **Tailwind CSS** | Styling framework | Utility-first CSS for rapid UI development |
| **React Router** | Navigation | Handle page routing (e.g., /jobs, /clients) |
| **React Query** | Data fetching | Manage server state, caching, and API calls |
| **Axios** | HTTP client | Make HTTP requests to the backend API |
| **Heroicons** | Icon library | Professional icons for UI |

### Backend Technologies

| Technology | Purpose | Why We Use It |
|------------|---------|---------------|
| **Python 3.9+** | Programming language | Powerful, readable, great ecosystem |
| **FastAPI** | Web framework | Modern, fast, automatic API documentation |
| **Pydantic** | Data validation | Type-safe request/response models |
| **JWT** | Authentication | Secure token-based authentication |
| **Uvicorn** | ASGI server | Run the FastAPI application |
| **Supabase Client** | Database access | Python SDK for PostgreSQL |

### Database & Infrastructure

| Technology | Purpose | Why We Use It |
|------------|---------|---------------|
| **Supabase** | Backend-as-a-Service | Hosted PostgreSQL with auth and storage |
| **PostgreSQL** | Database | Powerful, reliable relational database |
| **Row-Level Security** | Security | Database-level access control |

---

## Project Structure

```
islandGlassLeads/
│
├── frontend/                    # React application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   │   ├── Layout.tsx      # Page wrapper with header
│   │   │   ├── Sidebar.tsx     # Navigation sidebar
│   │   │   ├── ProtectedRoute.tsx  # Authentication guard
│   │   │   └── ui/             # Shared UI components
│   │   │
│   │   ├── pages/              # Full page components
│   │   │   ├── Login.tsx       # Login page
│   │   │   ├── Dashboard.tsx   # Home page
│   │   │   ├── Jobs.tsx        # Jobs list
│   │   │   ├── JobDetail.tsx   # Single job view
│   │   │   ├── Clients.tsx     # Clients list
│   │   │   ├── Vendors.tsx     # Vendors list
│   │   │   ├── Schedule.tsx    # Calendar view
│   │   │   └── Calculator.tsx  # Glass price calculator
│   │   │
│   │   ├── services/           # Business logic
│   │   │   ├── api.ts          # API client (axios)
│   │   │   └── calculator.ts   # Calculator logic
│   │   │
│   │   ├── context/            # React context providers
│   │   │   └── AuthContext.tsx # Authentication state
│   │   │
│   │   ├── types/              # TypeScript type definitions
│   │   │   └── index.ts        # Shared types
│   │   │
│   │   ├── App.tsx             # Main app component with routes
│   │   └── main.tsx            # Application entry point
│   │
│   ├── public/                 # Static assets
│   ├── index.html              # HTML template
│   ├── package.json            # Node.js dependencies
│   ├── tsconfig.json           # TypeScript configuration
│   ├── tailwind.config.js      # Tailwind CSS configuration
│   └── vite.config.ts          # Vite build configuration
│
├── backend/                    # FastAPI application
│   ├── routers/                # API endpoint handlers
│   │   ├── auth.py            # Login, logout, /me
│   │   ├── clients.py         # Client CRUD
│   │   ├── jobs.py            # Job CRUD
│   │   ├── vendors.py         # Vendor CRUD
│   │   ├── calculator.py      # Calculator config
│   │   ├── work_items.py      # Job work items
│   │   ├── site_visits.py     # Site visit tracking
│   │   ├── job_comments.py    # Job comments
│   │   ├── job_schedule.py    # Job scheduling
│   │   ├── job_files.py       # File attachments
│   │   ├── job_vendor_materials.py  # Materials tracking
│   │   └── material_templates.py    # Material templates
│   │
│   ├── models/                 # Pydantic data models
│   │   ├── user.py            # User and auth models
│   │   ├── client.py          # Client models
│   │   ├── job.py             # Job models
│   │   └── ...                # Other models
│   │
│   ├── middleware/             # Custom middleware
│   │   └── auth.py            # JWT verification
│   │
│   ├── main.py                # FastAPI app entry point
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database operations
│   └── auth.py                # Authentication logic
│
├── database/                   # Database files
│   ├── migrations/            # SQL migration files
│   └── seed_calculator_pricing.sql  # Calculator seed data
│
├── docs/                      # Documentation
│   ├── sessions/              # Development session notes
│   └── *.md                   # Various documentation
│
├── .env                       # Environment variables (DO NOT COMMIT)
├── README.md                  # Project overview
└── DEVELOPER_GUIDE.md        # This file
```

---

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

1. **Node.js** (v18 or higher)
   - Download from: https://nodejs.org/
   - Verify: `node --version`

2. **Python 3.9+**
   - Download from: https://www.python.org/
   - Verify: `python3 --version`

3. **Git**
   - Download from: https://git-scm.com/
   - Verify: `git --version`

4. **Code Editor**
   - Recommended: Visual Studio Code (https://code.visualstudio.com/)

### Initial Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/your-org/islandGlassLeads.git
cd islandGlassLeads
```

#### 2. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
# You'll need:
# - SUPABASE_URL (from your Supabase project)
# - SUPABASE_KEY (anon/public key)
# - SUPABASE_SERVICE_ROLE_KEY (service role key)
# - SECRET_KEY (generate with: openssl rand -hex 32)
```

#### 3. Set Up the Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (this downloads all required packages)
npm install

# Start the development server
npm run dev

# Frontend will be available at: http://localhost:5173
```

**What happens when you run `npm run dev`:**
- Vite starts a development server
- Your browser auto-refreshes when you save files (Hot Module Replacement)
- TypeScript is compiled in real-time
- You can access the app at http://localhost:5173

#### 4. Set Up the Backend

Open a **new terminal window** (keep the frontend running):

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip3 install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] python-multipart pydantic[email] python-dotenv supabase

# Start the backend server
python3 -m uvicorn main:app --reload --port 8000

# Backend will be available at: http://localhost:8000
```

**What happens when you run the backend:**
- FastAPI starts an HTTP server
- API endpoints become available (e.g., http://localhost:8000/api/v1/jobs)
- The server auto-restarts when you save files (--reload flag)
- You can view API documentation at http://localhost:8000/docs

#### 5. Verify Everything Works

1. **Check Frontend**: Open http://localhost:5173 in your browser
   - You should see the login page

2. **Check Backend**: Open http://localhost:8000/docs in your browser
   - You should see the Swagger API documentation

3. **Test Connection**: Try logging in with your Supabase credentials
   - The frontend will make a request to the backend
   - The backend will verify credentials with Supabase
   - You should be redirected to the dashboard

---

## Frontend Development

### How the Frontend Works

The frontend is a **Single Page Application (SPA)** built with React. This means:

1. When you visit the app, the entire React app is loaded once
2. As you navigate between pages, React updates the content without full page reloads
3. All data comes from API calls to the backend
4. The browser maintains a JWT token for authentication

### Key Frontend Concepts

#### Components

Components are reusable pieces of UI. Example:

```typescript
// A simple component
function Button({ text, onClick }: { text: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="px-4 py-2 bg-blue-600 text-white rounded"
    >
      {text}
    </button>
  );
}

// Usage
<Button text="Save" onClick={() => console.log('Saved!')} />
```

#### Pages

Pages are full-screen components that represent a route:

```typescript
// pages/Jobs.tsx
function Jobs() {
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    // Fetch jobs from API when page loads
    fetchJobs();
  }, []);

  return (
    <div>
      <h1>Jobs</h1>
      {jobs.map(job => (
        <JobCard key={job.id} job={job} />
      ))}
    </div>
  );
}
```

#### React Query (Data Fetching)

React Query manages server state:

```typescript
// Fetch data from API
const { data: jobs, isLoading, error } = useQuery({
  queryKey: ['jobs'],
  queryFn: () => api.jobs.getAll()
});

// React Query automatically:
// - Caches the data
// - Refetches when needed
// - Handles loading/error states
```

#### Routing

React Router handles navigation:

```typescript
// App.tsx defines routes
<Routes>
  <Route path="/login" element={<Login />} />
  <Route path="/jobs" element={<Jobs />} />
  <Route path="/jobs/:id" element={<JobDetail />} />
</Routes>

// Navigate programmatically
const navigate = useNavigate();
navigate('/jobs/123');
```

### Making API Calls

All API calls go through `/frontend/src/services/api.ts`:

```typescript
// services/api.ts
export const api = {
  jobs: {
    getAll: () => axios.get('/api/v1/jobs'),
    getById: (id: number) => axios.get(`/api/v1/jobs/${id}`),
    create: (data: CreateJobRequest) => axios.post('/api/v1/jobs', data),
    update: (id: number, data: UpdateJobRequest) =>
      axios.put(`/api/v1/jobs/${id}`, data),
    delete: (id: number) => axios.delete(`/api/v1/jobs/${id}`)
  }
};

// Usage in a component
const createJob = async (jobData) => {
  try {
    const response = await api.jobs.create(jobData);
    console.log('Job created:', response.data);
  } catch (error) {
    console.error('Failed to create job:', error);
  }
};
```

### Common Frontend Commands

```bash
# Install a new package
npm install package-name

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type check
npx tsc --noEmit

# Format code
npx prettier --write src/
```

---

## Backend Development

### How the Backend Works

The backend is a **REST API** built with FastAPI. This means:

1. It exposes URLs (endpoints) that the frontend can call
2. Each endpoint handles a specific operation (get jobs, create client, etc.)
3. It validates all incoming data
4. It performs business logic and database operations
5. It returns JSON responses

### API Endpoint Structure

Every endpoint follows this pattern:

```python
@router.get("/jobs/{job_id}")  # HTTP method and URL path
async def get_job(
    job_id: int,  # Path parameter
    current_user: TokenData = Depends(get_current_user)  # Auth required
):
    """
    Get a single job by ID.

    - **job_id**: The job's ID
    - Returns: JobResponse with full job details
    """
    # 1. Get user's company_id from JWT token
    company_id = current_user.company_id

    # 2. Fetch data from database
    db = Database()
    job = db.get_job_by_id(job_id, company_id)

    # 3. Handle not found
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 4. Return data (FastAPI automatically converts to JSON)
    return job
```

### Pydantic Models

Pydantic models define the shape of request/response data:

```python
# Input model (what the frontend sends)
class CreateJobRequest(BaseModel):
    client_id: int
    po_number: str
    job_date: Optional[date] = None
    total_estimate: Optional[Decimal] = None

    # Validation
    @field_validator('po_number')
    def po_number_valid(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('PO number required')
        return v.strip()

# Output model (what the backend returns)
class JobResponse(BaseModel):
    job_id: int
    client_id: int
    po_number: str
    job_date: Optional[str] = None
    total_estimate: Optional[float] = None
    created_at: str
    status: str
```

### Database Operations

All database operations are in `database.py`:

```python
# database.py
class Database:
    def get_jobs(self, company_id: str, filters: dict = None):
        """Fetch all jobs for a company"""
        query = self.client.table("jobs")\
            .select("*")\
            .eq("company_id", company_id)

        # Apply filters
        if filters and filters.get('status'):
            query = query.eq("status", filters['status'])

        response = query.execute()
        return response.data

    def insert_job(self, data: dict, user_id: str):
        """Create a new job"""
        # Add metadata
        data['created_by'] = user_id
        data['created_at'] = datetime.utcnow().isoformat()

        # Insert into database
        response = self.client.table("jobs").insert(data).execute()
        return response.data[0]
```

### Authentication Flow

1. **User logs in** → Frontend sends email/password to `/api/v1/auth/login`
2. **Backend verifies credentials** → Checks Supabase
3. **Backend generates JWT token** → Includes user_id, company_id, email
4. **Frontend stores token** → In localStorage
5. **Frontend includes token in requests** → `Authorization: Bearer <token>`
6. **Backend verifies token** → Using `get_current_user` dependency
7. **Backend allows/denies access** → Based on token validity

### Common Backend Commands

```bash
# Start the server
python3 -m uvicorn main:app --reload --port 8000

# Start with debug logging
python3 -m uvicorn main:app --reload --log-level debug

# Run tests
./test_clients.sh
./test_jobs.sh

# Install a new package
pip3 install package-name

# Generate requirements.txt
pip3 freeze > requirements.txt
```

---

## How Frontend & Backend Work Together

### Example: Creating a New Job

Let's walk through what happens when a user creates a new job:

#### 1. User Fills Out Form (Frontend)

```typescript
// pages/Jobs.tsx
const [formData, setFormData] = useState({
  client_id: 1,
  po_number: 'PO-12345',
  job_date: '2025-11-15',
  total_estimate: 5000
});

const handleSubmit = async () => {
  // Frontend calls API
  const response = await api.jobs.create(formData);
  console.log('Job created:', response.data);
};
```

#### 2. API Request Sent

```
POST http://localhost:8000/api/v1/jobs
Headers:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  Content-Type: application/json
Body:
  {
    "client_id": 1,
    "po_number": "PO-12345",
    "job_date": "2025-11-15",
    "total_estimate": 5000
  }
```

#### 3. Backend Receives Request

```python
# routers/jobs.py
@router.post("/", response_model=JobResponse)
async def create_job(
    job_data: CreateJobRequest,  # ← Pydantic validates this
    current_user: TokenData = Depends(get_current_user)  # ← Auth check
):
    # Convert Pydantic model to dict
    job_dict = job_data.model_dump()

    # Add company_id from JWT token
    job_dict['company_id'] = current_user.company_id

    # Save to database
    db = Database()
    new_job = db.insert_job(job_dict, current_user.user_id)

    # Return the created job
    return new_job
```

#### 4. Database Insert

```python
# database.py
def insert_job(self, data: dict, user_id: str):
    # Add metadata
    data['created_by'] = user_id
    data['created_at'] = datetime.utcnow().isoformat()

    # Convert date to string (Supabase requirement)
    if 'job_date' in data and data['job_date']:
        data['job_date'] = str(data['job_date'])

    # Insert into Supabase
    response = self.client.table("jobs").insert(data).execute()

    # Return the new record
    return response.data[0]
```

#### 5. Response Sent Back

```
HTTP 201 Created
{
  "job_id": 42,
  "client_id": 1,
  "po_number": "PO-12345",
  "job_date": "2025-11-15",
  "total_estimate": 5000.00,
  "status": "Quote",
  "created_at": "2025-11-13T20:00:00Z",
  "created_by": "user-uuid-123"
}
```

#### 6. Frontend Updates UI

```typescript
// React Query automatically refetches the jobs list
// UI updates to show the new job
```

### Complete Request/Response Cycle

```
┌─────────────┐                              ┌─────────────┐
│   Browser   │                              │   Backend   │
│  (Frontend) │                              │  (FastAPI)  │
└─────────────┘                              └─────────────┘
       │                                             │
       │  1. User clicks "Save"                     │
       │─────────────────────────────────────────►  │
       │                                             │
       │  2. POST /api/v1/jobs                      │
       │     + JWT token                             │
       │     + JSON body                             │
       │─────────────────────────────────────────►  │
       │                                             │
       │                                      3. Verify JWT token
       │                                      4. Validate input data
       │                                      5. Insert into database
       │                                             │
       │  6. HTTP 201 + Job data                    │
       │  ◄─────────────────────────────────────────│
       │                                             │
       │  7. Update UI with new job                 │
       │                                             │
```

---

## Common Tasks

### Task 1: Add a New Page

**Frontend:**

1. Create the page component:

```typescript
// frontend/src/pages/MyNewPage.tsx
export default function MyNewPage() {
  return (
    <div>
      <h1>My New Page</h1>
      <p>Content goes here</p>
    </div>
  );
}
```

2. Add route in App.tsx:

```typescript
// frontend/src/App.tsx
import MyNewPage from './pages/MyNewPage';

<Route path="/my-page" element={
  <ProtectedRoute>
    <Layout>
      <MyNewPage />
    </Layout>
  </ProtectedRoute>
} />
```

3. Add navigation link in Sidebar.tsx:

```typescript
// frontend/src/components/Sidebar.tsx
const navItems = [
  // ... existing items
  { path: '/my-page', label: 'My Page', icon: StarIcon },
];
```

### Task 2: Add a New API Endpoint

**Backend:**

1. Create Pydantic models:

```python
# backend/models/my_model.py
from pydantic import BaseModel
from typing import Optional

class MyModelCreate(BaseModel):
    name: str
    description: Optional[str] = None

class MyModelResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: str
```

2. Add database methods:

```python
# backend/database.py
def get_my_models(self, company_id: str):
    response = self.client.table("my_models")\
        .select("*")\
        .eq("company_id", company_id)\
        .execute()
    return response.data

def insert_my_model(self, data: dict, user_id: str):
    data['created_by'] = user_id
    response = self.client.table("my_models").insert(data).execute()
    return response.data[0]
```

3. Create router:

```python
# backend/routers/my_models.py
from fastapi import APIRouter, Depends
from models.my_model import MyModelCreate, MyModelResponse
from middleware.auth import get_current_user
from database import Database

router = APIRouter()

@router.get("/", response_model=list[MyModelResponse])
async def get_my_models(current_user = Depends(get_current_user)):
    db = Database()
    return db.get_my_models(current_user.company_id)

@router.post("/", response_model=MyModelResponse)
async def create_my_model(
    data: MyModelCreate,
    current_user = Depends(get_current_user)
):
    db = Database()
    model_dict = data.model_dump()
    model_dict['company_id'] = current_user.company_id
    return db.insert_my_model(model_dict, current_user.user_id)
```

4. Register router in main.py:

```python
# backend/main.py
from routers import my_models

app.include_router(
    my_models.router,
    prefix=f"{config.API_V1_PREFIX}/my-models",
    tags=["My Models"]
)
```

### Task 3: Fetch and Display Data

**Frontend:**

```typescript
// Using React Query
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

function MyComponent() {
  // Fetch data
  const { data, isLoading, error } = useQuery({
    queryKey: ['jobs'],  // Unique key for caching
    queryFn: () => api.jobs.getAll()
  });

  // Handle loading
  if (isLoading) return <div>Loading...</div>;

  // Handle error
  if (error) return <div>Error: {error.message}</div>;

  // Display data
  return (
    <div>
      {data.map(job => (
        <div key={job.job_id}>
          <h3>{job.po_number}</h3>
          <p>{job.status}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## Troubleshooting

### Frontend Issues

**Problem: "Cannot GET /" or blank white screen**

Solutions:
- Check if frontend dev server is running: `npm run dev`
- Check console for errors: Open DevTools (F12) → Console tab
- Try clearing cache and hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

**Problem: "Module not found" errors**

Solutions:
```bash
# Delete node_modules and reinstall
rm -rf node_modules
npm install
```

**Problem: "Network Error" or "ERR_CONNECTION_REFUSED"**

Solutions:
- Check if backend is running on port 8000
- Verify VITE_API_URL in .env or code
- Check CORS settings in backend

### Backend Issues

**Problem: "Command not found: uvicorn"**

Solutions:
```bash
# Use python module syntax instead
python3 -m uvicorn main:app --reload --port 8000

# Or install uvicorn
pip3 install uvicorn
```

**Problem: "Module 'X' has no attribute 'Y'"**

Solutions:
```bash
# Reinstall dependencies
pip3 install --upgrade fastapi uvicorn python-jose passlib
```

**Problem: Database connection errors**

Solutions:
- Verify .env file has correct SUPABASE_URL and SUPABASE_KEY
- Check Supabase project is active
- Verify database tables exist

### Common Errors

**TypeError: Object of type Decimal is not JSON serializable**

Solution: Convert Decimals to float in router before returning:

```python
if 'total_estimate' in job and job['total_estimate']:
    job['total_estimate'] = float(job['total_estimate'])
```

**TypeError: Object of type date is not JSON serializable**

Solution: Convert dates to strings in router before returning:

```python
if 'job_date' in job and job['job_date']:
    job['job_date'] = str(job['job_date'])
```

**401 Unauthorized errors**

Solutions:
- Check JWT token is being sent in Authorization header
- Verify token hasn't expired (tokens expire after 60 minutes)
- Re-login to get a fresh token

---

## Additional Resources

### Learning Resources

**React:**
- Official docs: https://react.dev/
- TypeScript + React: https://react.dev/learn/typescript

**FastAPI:**
- Official docs: https://fastapi.tiangolo.com/
- Tutorial: https://fastapi.tiangolo.com/tutorial/

**Tailwind CSS:**
- Official docs: https://tailwindcss.com/docs
- Cheatsheet: https://nerdcave.com/tailwind-cheat-sheet

### Useful Commands Reference

```bash
# FRONTEND COMMANDS
cd frontend
npm install                  # Install dependencies
npm run dev                 # Start dev server (port 5173)
npm run build              # Build for production
npm run preview            # Preview production build

# BACKEND COMMANDS
cd backend
python3 -m uvicorn main:app --reload --port 8000  # Start server
./test_clients.sh          # Run client tests
./test_jobs.sh            # Run job tests

# VIEW API DOCS
# Open in browser: http://localhost:8000/docs

# DATABASE MIGRATIONS
# Run migrations in Supabase SQL Editor:
# 1. Copy SQL from database/migrations/XXX.sql
# 2. Paste into Supabase SQL Editor
# 3. Run query
```

---

## Questions?

- Check the [checkpoint.md](checkpoint.md) for current project status
- Review [docs/sessions/](docs/sessions/) for detailed session notes
- Look at existing code for examples and patterns

**Pro Tip**: Use the browser DevTools Network tab to see actual HTTP requests between frontend and backend. This helps you understand exactly what data is being sent and received.
