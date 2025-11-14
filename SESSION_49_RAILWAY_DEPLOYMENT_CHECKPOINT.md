# Session 49: Railway Deployment - CHECKPOINT

**Date**: November 14, 2025
**Status**: 🟡 In Progress - Troubleshooting Railway deployment

---

## Current Situation

We are **extremely close** to successfully deploying the Island Glass CRM to Railway. The app is built, configured, and environment variables are set. We're just debugging final deployment issues.

### Latest Commit
- **Commit**: `9694e88` - "Force Node 20+ for Railway deployment"
- **Branch**: `main`
- **Pushed to**: https://github.com/Kellum/islandGlass.git

---

## What We Accomplished This Session

### ✅ Completed
1. **Created Railway deployment configuration**
   - `railway.json` with build and deploy commands
   - `backend/requirements.txt` with Python dependencies
   - `.nvmrc` to force Node 20+

2. **Fixed TypeScript build errors**
   - Fixed unused imports in frontend files
   - Added type assertions for calendar component
   - Frontend builds successfully locally

3. **Updated code for production**
   - `backend/main.py` now serves React static files
   - `frontend/src/services/api.ts` auto-detects dev/prod environment
   - Production build works locally

4. **Environment variables configured in Railway**
   - `JWT_SECRET`: `bfxmsjWdsh2-OqN7h_Cugx5trj_K9MYSYhphxZmknMA`
   - `SUPABASE_URL`: `https://dgsjmsccpdrgnnpzlsgj.supabase.co`
   - `SUPABASE_KEY`: (anon key - set in Railway)
   - `SUPABASE_SERVICE_ROLE_KEY`: (service role key - set in Railway)

5. **Fixed multiple Railway deployment issues**
   - Removed conflicting `nixpacks.toml` (was using Node 18)
   - Removed old `railway.toml` (was trying to run streamlit)
   - Added `.nvmrc` with Node 20
   - Added `engines` field to `frontend/package.json` requiring Node >=20

---

## Current Issue

**Problem**: Railway is still using Node 18 instead of Node 20, causing:
- `patch-package: not found` error during npm install
- Engine compatibility warnings for vite, react-router, etc.

**Latest Error Log**:
```
npm warn EBADENGINE Unsupported engine { node: 'v18.20.5' }
npm error sh: 1: patch-package: not found
ERROR: failed to build: exit code: 127
```

**What Railway is detecting**:
```
setup      │ nodejs_18, npm-9_x
```

**What we need**:
```
setup      │ nodejs_20, npm-10_x
```

---

## Files Changed This Session

### Created
- `backend/requirements.txt` - Python dependencies
- `railway.json` - Railway build/deploy config
- `.nvmrc` - Force Node 20

### Modified
- `backend/main.py` - Added frontend static file serving
- `frontend/src/services/api.ts` - Production API URL detection
- `frontend/package.json` - Added engines field for Node 20+
- Fixed TS errors in: `JobForm.tsx`, `calendar.tsx`, `Dashboard.tsx`, `CalculatorSettings.tsx`, `calculator.ts`

### Deleted
- `nixpacks.toml` - Was forcing Node 18
- `railway.toml` - Was trying to run streamlit

---

## Railway Project Info

**Project Name**: Island Glass CRM (user's Railway project)
**Connected to**: `Kellum/islandGlass` GitHub repo
**Region**: us-east4
**Builder**: NIXPACKS

---

## Next Steps to Fix

### Option 1: Force Node 20 via Railway Settings (RECOMMENDED)
In Railway dashboard:
1. Go to service → Settings
2. Look for "Build Settings" or "Environment"
3. Add variable: `NIXPACKS_NODE_VERSION=20`
4. Redeploy

### Option 2: Create explicit nixpacks.toml with Node 20
Create `nixpacks.toml`:
```toml
[phases.setup]
nixPkgs = ["nodejs-20_x", "python39"]

[phases.install]
cmds = ["npm ci"]

[phases.build]
cmds = ["cd frontend && npm ci && npm run build && cd ../backend && pip install -r requirements.txt"]

[start]
cmd = "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
```

### Option 3: Use Buildpacks instead of Nixpacks
In Railway dashboard:
1. Settings → Build Settings
2. Change builder from NIXPACKS to BUILDPACKS
3. Redeploy

---

## System Architecture

### Production (Single Service - Railway)
```
Railway (single URL)
├── Frontend (/) → Static React files from frontend/dist/
└── Backend (/api/v1/*) → FastAPI endpoints → Supabase
```

### Local Development (Working)
```
Frontend: http://localhost:3001 (Vite dev server)
Backend: http://localhost:8000 (Uvicorn with --reload)
```

---

## Railway Build Process (Expected)

1. **Setup Phase**: Install Node 20 + Python 3.9
2. **Install Phase**: `npm ci` (root level, if package.json exists)
3. **Build Phase**:
   - `cd frontend && npm ci && npm run build`
   - `cd ../backend && pip install -r requirements.txt`
4. **Start Phase**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## Known Working Configuration

**Local `.env`** (contains all Supabase credentials):
```bash
SUPABASE_URL=https://dgsjmsccpdrgnnpzlsgj.supabase.co
SUPABASE_KEY=eyJhbG... (anon key)
SUPABASE_SERVICE_ROLE_KEY=eyJhbG... (service role key)
```

**Backend is working locally** on port 8000
**Frontend builds successfully** with `npm run build`
**Production build tested locally** - backend serves frontend correctly

---

## Quick Start Prompt for Next Session

```
Continue Railway deployment for Island Glass CRM. Latest commit: 9694e88.

Current issue: Railway still using Node 18 instead of Node 20, causing
"patch-package not found" error. We've tried:
- Added .nvmrc with "20"
- Added engines field to package.json
- Removed conflicting nixpacks.toml and railway.toml

Next: Try adding NIXPACKS_NODE_VERSION=20 as Railway environment variable,
or create new nixpacks.toml with nodejs-20_x explicitly.

Railway project is connected to GitHub, environment variables are set
(JWT_SECRET, SUPABASE_*). Just need to fix Node version detection.
```

---

## Useful Commands

```bash
# Generate new JWT secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Test local production build
cd frontend && npm run build
cd ../backend && uvicorn main:app --host 0.0.0.0 --port 8000

# Check Railway logs
# (in Railway dashboard → Deployments → Click latest → View Logs)

# Git status
git status
git log --oneline -5
```

---

## Important Links

- **GitHub Repo**: https://github.com/Kellum/islandGlass
- **Supabase Dashboard**: https://app.supabase.com
- **Railway Dashboard**: https://railway.app/dashboard
- **Deployment Plan**: See `SESSION_48_COMPLETE_DEPLOYMENT_PLAN.md`

---

## Summary

✅ **What's Working**:
- Frontend builds successfully (locally)
- Backend runs successfully (locally)
- Production build tested locally - works perfectly
- All Railway env vars configured
- Code pushed to GitHub and triggering Railway deploys

🟡 **What's Not Working**:
- Railway detecting Node 18 instead of Node 20
- Need to force Railway to use Node 20+

🎯 **We Are 95% There**: Just need Railway to use the correct Node version!

---

**Next Session**: Add `NIXPACKS_NODE_VERSION=20` to Railway environment variables and redeploy.
