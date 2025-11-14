# Island Glass CRM - FastAPI Backend

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip3 install fastapi uvicorn 'python-jose[cryptography]' 'passlib[bcrypt]' python-multipart 'pydantic[email]' python-dotenv

# Or from requirements.txt (once created)
pip3 install -r requirements.txt
```

### Running the Server

```bash
# From project root
cd backend
python3 main.py

# Or using uvicorn directly
uvicorn main:app --reload --port 8000

# Server will be available at: http://localhost:8000
```

### API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── config.py              # Environment variables and settings
├── auth.py                # Authentication logic (from modules/)
├── database.py            # Database methods (from modules/)
├── routers/
│   ├── auth.py           # Authentication endpoints (login, refresh, /me) ✅
│   ├── clients.py        # Client CRUD endpoints ✅ PRODUCTION READY
│   └── jobs.py           # Job/PO CRUD endpoints (TODO)
├── models/
│   ├── user.py           # User and auth Pydantic models
│   ├── client.py         # Client Pydantic models
│   └── job.py            # Job/PO Pydantic models
└── middleware/
    └── auth.py           # JWT verification middleware
```

## 🔐 Authentication Endpoints

### POST /api/v1/auth/login
Login with email and password, receive JWT tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Test with curl:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"yourpassword"}'
```

### POST /api/v1/auth/refresh
Exchange refresh token for new access token.

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### GET /api/v1/auth/me
Get current user information (requires authentication).

**Headers:**
```
Authorization: Bearer eyJ...
```

**Response:**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "company_id": "company-uuid",
  "role": "admin",
  "department": "Sales",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Test with curl:**
```bash
# First, login and save the token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"yourpassword"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Then use the token to access protected endpoints
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### POST /api/v1/auth/logout
Logout endpoint (for consistency - client should delete token).

**Headers:**
```
Authorization: Bearer eyJ...
```

**Response:**
```json
{
  "message": "Logged out successfully",
  "user_id": "user-uuid"
}
```

## 🔧 Configuration

Environment variables (loaded from `.env`):

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# JWT
SECRET_KEY=your-secret-key-change-in-production

# Other
GOOGLE_PLACES_API_KEY=your-google-api-key
ANTHROPIC_API_KEY=your-anthropic-key
```

## 📊 Database

Uses existing `database.py` module with all Supabase methods:
- Client management (CRUD)
- Job/PO management
- Work items, materials, site visits
- File references, comments, schedule
- User profiles and authentication

All database code from the Dash app is **100% reusable** - no changes needed!

## 🛠️ Development

### Testing Endpoints

Use the Swagger UI at http://localhost:8000/docs to test all endpoints interactively.

Or use curl:

```bash
# Health check
curl http://localhost:8000/
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Get user info (with token)
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Adding New Endpoints

1. Create Pydantic models in `models/`
2. Create router in `routers/`
3. Add router to `main.py`:

```python
from routers import auth, clients, jobs

app.include_router(clients.router, prefix=f"{config.API_V1_PREFIX}/clients", tags=["Clients"])
app.include_router(jobs.router, prefix=f"{config.API_V1_PREFIX}/jobs", tags=["Jobs"])
```

### Protected Routes

Use the `get_current_user` dependency for protected routes:

```python
from middleware.auth import get_current_user
from models.user import TokenData

@router.get("/protected")
async def protected_route(current_user: TokenData = Depends(get_current_user)):
    return {
        "message": f"Hello {current_user.email}",
        "user_id": current_user.user_id,
        "company_id": current_user.company_id
    }
```

## ✅ Session 31 Completed

**What We Built:**
- ✅ FastAPI backend structure with routers, models, middleware
- ✅ Authentication endpoints (login, refresh, /me, logout)
- ✅ JWT token generation and verification
- ✅ Pydantic models for User, Client, Job
- ✅ CORS configuration for React frontend
- ✅ Swagger UI documentation
- ✅ Database and auth modules integrated

**Server Status:**
- ✅ Running at http://localhost:8000
- ✅ Health check: http://localhost:8000/health
- ✅ API docs: http://localhost:8000/docs

**Next Steps (Week 1 Days 2-7):**
1. Test authentication with real Supabase user
2. Build Client endpoints (GET, POST, PUT, DELETE)
3. Build Job endpoints
4. Add file upload endpoint
5. Create Postman collection for testing
6. Build React frontend (Week 2)

## 👥 Client Endpoints (PRODUCTION READY ✅)

### GET /api/v1/clients/
List all clients with optional filtering.

**Query Parameters:**
- `client_type` (optional): Filter by type (residential, contractor, commercial)
- `city` (optional): Filter by city
- `search` (optional): Search in client_name or contact names

**Example:**
```bash
curl http://localhost:8000/api/v1/clients/?client_type=residential \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "client_type": "residential",
    "client_name": "John Doe",
    "address": "123 Main St",
    "city": "Jacksonville",
    "state": "FL",
    "zipcode": "32256",
    "company_id": "uuid",
    "created_at": "2025-11-07T12:00:00",
    "updated_at": "2025-11-07T12:00:00",
    "created_by": "user-uuid",
    "updated_by": null
  }
]
```

### GET /api/v1/clients/{id}
Get detailed client information including contacts and job statistics.

**Example:**
```bash
curl http://localhost:8000/api/v1/clients/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "id": 1,
  "client_type": "residential",
  "client_name": "John Doe",
  "contacts": [
    {
      "id": 1,
      "client_id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "555-1234",
      "is_primary": true,
      "created_at": "2025-11-07T12:00:00"
    }
  ],
  "job_count": 5,
  "total_revenue": 12500.00
}
```

### POST /api/v1/clients/
Create a new client with primary contact.

**Request Body:**
```json
{
  "client_type": "residential",
  "client_name": "Jane Smith",
  "address": "456 Oak Ave",
  "city": "Jacksonville",
  "state": "FL",
  "zipcode": "32256",
  "primary_contact": {
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com",
    "phone": "555-5678"
  },
  "additional_contacts": [
    {
      "first_name": "Bob",
      "last_name": "Smith",
      "email": "bob@example.com",
      "phone": "555-9999",
      "is_primary": false
    }
  ]
}
```

**Validation Rules:**
- `client_type`: Must be one of: residential, contractor, commercial
- `client_name`: Minimum 2 characters (if provided)
- `email`: Must be valid email format
- `first_name`, `last_name`: Minimum 2 characters, not empty
- `primary_contact`: Required

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/clients/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_type": "residential",
    "client_name": "Test Client",
    "primary_contact": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com"
    }
  }'
```

### PUT /api/v1/clients/{id}
Update an existing client (partial updates supported).

**Request Body (all fields optional):**
```json
{
  "client_name": "Updated Name",
  "city": "New City",
  "state": "GA"
}
```

**Example:**
```bash
curl -X PUT http://localhost:8000/api/v1/clients/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"client_name": "Updated Name"}'
```

### DELETE /api/v1/clients/{id}
Soft delete a client (sets `deleted_at` timestamp).

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/clients/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:** 204 No Content

---

## 📝 Notes

- All existing `database.py` methods work as-is
- No changes needed to database schema
- JWT tokens expire after 60 minutes
- Refresh tokens expire after 7 days
- CORS allows localhost:3000 (React), localhost:5173 (Vite), localhost:8050 (Dash)
- Deleted clients return 404 (soft delete with `deleted_at`)
- All endpoints validate input and return clear error messages
- Comprehensive test suite available: `./test_clients.sh` and `./test_clients_edge_cases.sh`
