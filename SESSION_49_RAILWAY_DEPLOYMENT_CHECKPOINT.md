# Session 49: Railway Deployment - CHECKPOINT

**Date**: November 14, 2025
**Status**: ✅ COMPLETE - Successfully deployed to Railway!

---

## Current Situation

We are **extremely close** to successfully deploying the Island Glass CRM to Railway. The app is built, configured, and environment variables are set. We're just debugging final deployment issues.

### Latest Commit
- **Commit**: `926b777` - "Fix SPA routing: add catch-all route for React Router"
- **Branch**: `main`
- **Pushed to**: https://github.com/Kellum/islandGlass.git
- **Deployment**: ✅ Live on Railway

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

## All Issues Fixed - Deployment Complete! 🎉

### Issue 1: patch-package Not Found ✅
**Fixed in commit `4baa36d` & `d87d237`**:
- Changed `npm ci` to `npm ci --include=dev` in `railway.json`
- Added `patch-package` to frontend `devDependencies`
- Ensures all build tools available during Railway build

### Issue 2: pip Command Not Found ✅
**Fixed in commit `185d0fc` & `b375aed`**:
- Created `nixpacks.toml` to specify both Node.js and Python
- Used correct package names: `nodejs_20`, `python39`, `python39Packages.pip`
- Enables multi-language builds (Node + Python)

### Issue 3: Pip Externally-Managed Environment ✅
**Fixed in commit `851f9c7`**:
- Created Python virtual environment during build: `python -m venv .venv`
- Install deps in isolated venv: `.venv/bin/pip install -r requirements.txt`
- Run app with venv: `.venv/bin/uvicorn main:app`
- Production-ready Python environment isolation

### Issue 4: Missing email-validator Dependency ✅
**Fixed in commit `b8c3bba`**:
- Added `email-validator==2.1.0` to `backend/requirements.txt`
- Required by Pydantic's `EmailStr` type in User models
- App now starts successfully on Railway

### Issue 5: Frontend Not Serving (Health Check JSON) ✅
**Fixed in commit `4d9c803`**:
- Moved health check from `@app.get("/")` to `@app.get("/api/health")`
- Allows React frontend to be served at root path
- Backend serves frontend correctly

### Issue 6: CORS Blocking API Requests ✅
**Fixed in commit `39bfb87`**:
- Added dynamic CORS configuration using `RAILWAY_PUBLIC_DOMAIN`
- Railway auto-sets this variable with deployment URL
- Allows both HTTP and HTTPS for Railway domain
- Login and API calls work correctly

### Issue 7: SPA Routes Return 404 ✅
**Fixed in commit `926b777`**:
- Replaced `StaticFiles` mount with proper SPA routing
- Added `/assets` mount for static files (CSS, JS, images)
- Added catch-all route `/{full_path:path}` serving `index.html`
- Direct navigation to `/login` and other routes now works

**Final Status**: ✅ All systems operational on Railway!

---

## Files Changed This Session

### Created
- `backend/requirements.txt` - Python dependencies (FastAPI, Uvicorn, Supabase, etc.)
- `railway.json` - Railway build/deploy configuration
- `nixpacks.toml` - Multi-language build configuration (Node 20 + Python 3.9)

### Modified
- `railway.json` - Updated to use venv: `python -m venv .venv && .venv/bin/pip install`
- `backend/requirements.txt` - Added `email-validator==2.1.0` for Pydantic EmailStr
- `backend/main.py` - Fixed SPA routing with catch-all route, moved health check to `/api/health`
- `backend/config.py` - Added dynamic CORS for Railway URL using `RAILWAY_PUBLIC_DOMAIN`
- `frontend/package.json` - Added `patch-package` to devDependencies

### Key Configuration Files
- **nixpacks.toml**: Specifies `nodejs_20`, `python39`, `python39Packages.pip`
- **railway.json**: Build command creates venv, start command uses `.venv/bin/uvicorn`
- **.gitignore**: Already includes `.venv` (no changes needed)

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

## Deployment Complete - Summary

**7 commits deployed** (from `4baa36d` to `926b777`):
1. `4baa36d` - Include devDependencies in npm ci
2. `d87d237` - Add patch-package to devDependencies
3. `185d0fc` - Add nixpacks.toml for Node + Python
4. `b375aed` - Fix nixpacks package names
5. `851f9c7` - Use Python virtual environment
6. `b8c3bba` - Add email-validator dependency
7. `4d9c803` - Move health check endpoint
8. `39bfb87` - Fix CORS for Railway domain
9. `926b777` - Fix SPA routing

**Railway Environment Variables Set**:
- `SECRET_KEY` - JWT signing key
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon key
- `NIXPACKS_NODE_VERSION=20` - Force Node 20
- `RAILWAY_PUBLIC_DOMAIN` - Auto-set by Railway for CORS

**App is Live**: ✅ Login working, API calls working, SPA routing working

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

✅ **Fully Deployed and Working**:
- ✅ Frontend builds successfully on Railway (Node 20, Vite 7)
- ✅ Backend runs successfully on Railway (Python 3.9, FastAPI)
- ✅ React app loads at root path (/)
- ✅ Login and authentication working (JWT tokens, Supabase)
- ✅ API calls working (/api/v1/* endpoints)
- ✅ CORS configured correctly for Railway domain
- ✅ SPA routing working (direct navigation to /login, /dashboard, etc.)
- ✅ Static assets serving correctly (/assets/*)
- ✅ Health checks available (/health, /api/health)
- ✅ API documentation available (/docs)

🎯 **100% Complete**: Island Glass CRM is live on Railway!

---

## Key Learnings

1. **Multi-language Railway deploys**: Use `nixpacks.toml` to specify both Node.js and Python packages
2. **Python in Nix environments**: Always use virtual environments to avoid "externally-managed" errors
3. **npm ci in production**: Use `--include=dev` flag when dev dependencies are needed for builds
4. **SPA routing on FastAPI**: Use catch-all route after registering API routes, not StaticFiles mount
5. **Dynamic CORS**: Leverage Railway's auto-set environment variables like `RAILWAY_PUBLIC_DOMAIN`
6. **Build troubleshooting**: Check Railway logs carefully - errors appear at different build phases

---

**Next Steps**:
- Monitor app performance on Railway
- Set up custom domain (optional)
- Configure CI/CD for automated testing before deployment
- Add monitoring/logging (Sentry, LogRocket, etc.)
