# Session 48: Complete + Railway Deployment Plan

## Session Summary

### What Was Accomplished
1. ✅ Fixed foreign key constraint violation in job creation
2. ✅ Committed all code to git (368 files, 75,075 insertions)
3. ✅ Pushed to GitHub: `https://github.com/Kellum/islandGlass.git`
4. ✅ System fully functional locally
5. ✅ Created deployment strategy

### The Fix Applied
**File**: `backend/database.py` (line 1825-1838)

**Problem**: Foreign key constraint `jobs_company_id_fkey` violated because `company_id` from `user_profiles` didn't exist in `auth.users` table.

**Solution**: Simplified to always use authenticated `user_id` as `company_id` (guaranteed to exist).

**Before**:
```python
company_id = self.get_user_company_id(user_id)
if not company_id:
    company_id = user_id
```

**After**:
```python
# Use user_id as company_id since it's guaranteed to exist in auth.users
if user_id:
    job_data['company_id'] = user_id
    job_data['created_by'] = user_id
```

---

## Current System Status

### Backend (FastAPI + Supabase)
- ✅ Running on `http://localhost:8000`
- ✅ All endpoints functional
- ✅ PO auto-generation working
- ✅ Foreign key constraints satisfied
- ✅ Database: 8/8 tables migrated

### Frontend (React + TypeScript)
- ✅ Running on `http://localhost:3001`
- ✅ All pages functional
- ✅ PO generation UI working
- ✅ Job creation successful
- ✅ Client/Vendor management working

### Git Repository
- ✅ Committed: `fb943cf` - "Complete Island Glass CRM"
- ✅ Pushed to: `https://github.com/Kellum/islandGlass.git`
- ✅ Branch: `main`

---

## Railway Deployment Plan

### Strategy: Combined Deployment (Single Service)
**Decision**: Start with FastAPI serving the React frontend (Option 2)

**Why**:
- Simplest deployment
- Lowest cost (1 Railway service)
- Fastest to production
- Easy to separate later (5 min migration)

### Architecture
```
Railway Service (Single Instance)
├── FastAPI Backend (API routes at /api/v1/*)
└── React Frontend (Static files at /*)
```

---

## Deployment Steps

### Phase 1: Prepare for Deployment

#### Step 1: Create Railway Configuration Files

**File**: `backend/requirements.txt`
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
supabase==2.0.3
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

**File**: `railway.json` (root directory)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**File**: `nixpacks.toml` (root directory)
```toml
[phases.setup]
nixPkgs = ["python39", "nodejs-18_x"]

[phases.install]
cmds = [
  "cd frontend && npm install",
  "cd backend && pip install -r requirements.txt"
]

[phases.build]
cmds = ["cd frontend && npm run build"]

[start]
cmd = "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
```

#### Step 2: Update FastAPI to Serve React

**File**: `backend/main.py`

Add to imports:
```python
from fastapi.staticfiles import StaticFiles
import os
```

After all your routers, add at the END of the file:
```python
# Serve React frontend (must be LAST - after all API routes)
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
    print(f"✅ Serving frontend from {frontend_dist}")
else:
    print(f"⚠️  Frontend dist not found at {frontend_dist}")
```

#### Step 3: Update Frontend API Configuration

**File**: `frontend/src/services/api.ts`

Change line 3-4:
```typescript
// Use relative path in production, localhost in development
const API_BASE_URL = import.meta.env.VITE_API_URL || '';
const API_V1_PREFIX = '/api/v1';
```

This allows:
- **Development**: Uses `http://localhost:8000/api/v1`
- **Production**: Uses same domain `/api/v1`

#### Step 4: Add .env Files to .gitignore

**Verify**: `.gitignore` already has:
```
.env
.env.local
.env.production
.env.development
backend/.env
frontend/.env
```

---

### Phase 2: Deploy to Railway

#### Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose: `Kellum/islandGlass`
6. Railway auto-detects configuration

#### Step 2: Set Environment Variables

In Railway dashboard, add these variables:

**Required**:
```bash
SUPABASE_URL=https://xxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
JWT_SECRET=your-secret-key-here-min-32-chars
```

**Optional** (for production):
```bash
ENVIRONMENT=production
LOG_LEVEL=info
```

#### Step 3: Deploy

Railway will automatically:
1. Build frontend (`npm run build`)
2. Install Python dependencies
3. Start FastAPI with uvicorn
4. Assign a public URL

#### Step 4: Verify Deployment

Check Railway logs for:
```
✅ Serving frontend from /app/frontend/dist
INFO:     Uvicorn running on http://0.0.0.0:PORT
INFO:     Application startup complete
```

Visit your Railway URL - you should see the React app!

---

### Phase 3: Post-Deployment Testing

#### Test Checklist

**Frontend**:
- [ ] Login page loads
- [ ] Can authenticate
- [ ] Dashboard displays
- [ ] Jobs page works
- [ ] Clients page works
- [ ] Vendors page works

**Backend API**:
- [ ] Visit `https://your-app.railway.app/docs` - Swagger UI loads
- [ ] Auth endpoints work
- [ ] Jobs CRUD works
- [ ] PO generation works
- [ ] Calculator works

**PO System**:
- [ ] Can create client
- [ ] Can generate PO number
- [ ] Can create job with PO
- [ ] PO displays with badges
- [ ] Duplicate detection works

---

## Migration Path: Separating Services Later

### When to Separate
- Traffic increases significantly
- Need independent scaling
- Want faster frontend deployments
- Want to use Vercel for free frontend hosting

### How to Separate (5 Minutes)

#### Step 1: Deploy Frontend to Vercel
```bash
# In Vercel dashboard:
# - Connect GitHub repo
# - Root directory: frontend
# - Build command: npm run build
# - Output directory: dist
# - Add env var: VITE_API_URL=https://your-backend.railway.app
```

#### Step 2: Update Backend
Remove this from `backend/main.py`:
```python
# DELETE THESE LINES:
app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
```

#### Step 3: Deploy Backend Changes
```bash
git commit -m "Remove frontend serving from backend"
git push origin main
# Railway auto-deploys
```

**Done!** Frontend on Vercel (free), Backend on Railway (paid).

---

## Environment Variables Reference

### Supabase Variables

Get these from [Supabase Dashboard](https://app.supabase.com):

1. Go to your project
2. Click "Settings" → "API"
3. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon/public** key → `SUPABASE_KEY`
   - **service_role** key → `SUPABASE_SERVICE_ROLE_KEY`

### JWT Secret

Generate a secure secret:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy output to `JWT_SECRET`

---

## Files to Create Before Deployment

### 1. `backend/requirements.txt`
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
supabase==2.0.3
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

### 2. `railway.json` (root)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 3. Update `backend/main.py`
Add frontend serving (at the END, after all routes):
```python
from fastapi.staticfiles import StaticFiles
import os

# ... all your existing code ...

# Serve React frontend (LAST - after API routes)
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
```

### 4. Update `frontend/src/services/api.ts`
Change API_BASE_URL:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || '';
```

---

## Troubleshooting Guide

### Issue: Frontend Not Loading

**Check**:
```bash
# In Railway logs, look for:
✅ Serving frontend from /app/frontend/dist
```

**Fix**: Ensure build command ran successfully in Railway build logs.

### Issue: API Calls Failing

**Check**: Browser DevTools → Network tab → API calls

**Fix**:
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are set
- Check Railway logs for errors
- Visit `/docs` to test API directly

### Issue: Authentication Failing

**Check**:
- `JWT_SECRET` is set (min 32 chars)
- Supabase credentials are correct

**Fix**: Regenerate JWT secret, verify Supabase keys

### Issue: Database Connection Errors

**Check**:
- `SUPABASE_URL` format: `https://xxx.supabase.co`
- `SUPABASE_KEY` is the **anon** key (not service role)

**Fix**: Copy-paste directly from Supabase dashboard

---

## Quick Commands Reference

### Local Development
```bash
# Backend
cd backend
python3 -m uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm run dev
```

### Build Frontend Locally
```bash
cd frontend
npm run build
# Output in: frontend/dist/
```

### Test Production Build Locally
```bash
# Terminal 1 - Build frontend
cd frontend && npm run build

# Terminal 2 - Run backend (serves frontend)
cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000

# Visit: http://localhost:8000
```

### Git Commands
```bash
# Check status
git status

# Stage changes
git add .

# Commit
git commit -m "Your message"

# Push
git push origin main
```

---

## Next Session Checklist

When you return to deploy:

- [ ] Create `backend/requirements.txt`
- [ ] Create `railway.json`
- [ ] Update `backend/main.py` to serve frontend
- [ ] Update `frontend/src/services/api.ts` for production
- [ ] Commit and push changes
- [ ] Create Railway project
- [ ] Set environment variables in Railway
- [ ] Deploy and test
- [ ] Document production URL

---

## System Architecture

### Development (Current)
```
Frontend (localhost:3001) → Backend (localhost:8000) → Supabase
```

### Production (Single Service)
```
Railway (single URL)
├── Frontend (/) → Static React files
└── Backend (/api/v1/*) → FastAPI endpoints → Supabase
```

### Future (Separated Services)
```
Vercel (Frontend) → Railway (Backend) → Supabase
```

---

## Success Criteria

### Deployment Complete When:
- ✅ Railway URL loads React app
- ✅ Can login successfully
- ✅ Can create clients
- ✅ Can generate PO numbers
- ✅ Can create jobs
- ✅ All CRUD operations work
- ✅ Calculator functions
- ✅ No console errors

---

## Important URLs

**GitHub**: https://github.com/Kellum/islandGlass
**Railway Dashboard**: https://railway.app/dashboard
**Supabase Dashboard**: https://app.supabase.com

**Local Dev**:
- Frontend: http://localhost:3001
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Production** (after deployment):
- App: https://your-app-name.railway.app
- API Docs: https://your-app-name.railway.app/docs

---

## Contact for Next Session

**Current Status**: ✅ Code pushed to GitHub, ready for deployment

**Next Step**: Create Railway configuration files and deploy

**Estimated Time**: 30-45 minutes to complete deployment

**What You Need**:
- Railway account (free)
- Supabase credentials (you already have these)
- The configuration files listed above

---

**Session 48 Complete** ✅
**Date**: November 14, 2025
**Commit**: `fb943cf`
**GitHub**: https://github.com/Kellum/islandGlass

🚀 **Ready for Railway Deployment!**
