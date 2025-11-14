# Island Glass CRM - Quick Start Guide

## 🚀 Get Up and Running in 5 Minutes

### Prerequisites Check

```bash
# Verify you have these installed:
node --version    # Should be v18 or higher
python3 --version # Should be 3.9 or higher
git --version     # Any recent version
```

### Step 1: Environment Setup (1 minute)

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Supabase credentials
# You need: SUPABASE_URL, SUPABASE_KEY, SECRET_KEY
```

### Step 2: Start Frontend (2 minutes)

```bash
# Open Terminal 1
cd frontend
npm install        # First time only (downloads packages)
npm run dev       # Starts dev server

# ✅ Frontend running at: http://localhost:5173
```

### Step 3: Start Backend (2 minutes)

```bash
# Open Terminal 2 (new terminal window)
cd backend
python3 -m uvicorn main:app --reload --port 8000

# ✅ Backend running at: http://localhost:8000
# ✅ API docs at: http://localhost:8000/docs
```

### Step 4: Test It Works

1. Open browser to http://localhost:5173
2. You should see the login page
3. Log in with your Supabase credentials
4. You should see the dashboard

---

## 📝 Daily Development Commands

### Frontend (Terminal 1)

```bash
cd frontend

# Start dev server (hot reload enabled)
npm run dev

# Install a new package
npm install package-name

# Build for production
npm run build
```

### Backend (Terminal 2)

```bash
cd backend

# Start API server (auto-reload enabled)
python3 -m uvicorn main:app --reload --port 8000

# Run tests
./test_clients.sh
./test_jobs.sh

# Install a new package
pip3 install package-name
```

---

## 🎯 Current URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:5173 | Main app UI |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **API Docs (Alt)** | http://localhost:8000/redoc | ReDoc UI |

---

## 🛠️ Tech Stack Summary

### Frontend
- **React 19** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool (fast hot reload)
- **Tailwind CSS** - Styling
- **React Query** - Data fetching
- **React Router** - Navigation

### Backend
- **FastAPI** - Python web framework
- **Pydantic** - Data validation
- **JWT** - Authentication tokens
- **Supabase** - PostgreSQL database

---

## 📂 Key Files to Know

```
islandGlassLeads/
├── frontend/
│   ├── src/
│   │   ├── pages/          # Full page components
│   │   ├── components/     # Reusable UI components
│   │   ├── services/api.ts # API client (axios)
│   │   └── App.tsx         # Main app with routes
│   └── package.json        # Frontend dependencies
│
├── backend/
│   ├── routers/            # API endpoints
│   ├── models/             # Pydantic models
│   ├── database.py         # Database operations
│   └── main.py             # FastAPI app
│
├── .env                    # Environment variables (DO NOT COMMIT)
├── DEVELOPER_GUIDE.md      # Full documentation (READ THIS!)
└── checkpoint.md           # Current project status
```

---

## 🐛 Common Issues & Quick Fixes

### "Cannot GET /" or blank screen
```bash
# Make sure frontend is running
cd frontend
npm run dev
```

### "ERR_CONNECTION_REFUSED" errors
```bash
# Make sure backend is running
cd backend
python3 -m uvicorn main:app --reload --port 8000
```

### "Module not found" errors (Frontend)
```bash
cd frontend
rm -rf node_modules
npm install
```

### "Command not found: uvicorn"
```bash
# Use python module syntax instead
python3 -m uvicorn main:app --reload --port 8000
```

### White screen after code changes
```bash
# Hard refresh browser
# Mac: Cmd + Shift + R
# Windows: Ctrl + Shift + R
```

---

## 📚 Next Steps

1. **Read the full guide**: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
2. **Check current status**: [checkpoint.md](checkpoint.md)
3. **View session history**: [docs/sessions/](docs/sessions/)

---

## 🎓 Learning Path

### For Complete Beginners

1. **Day 1**: Run the app, explore the UI
2. **Day 2**: Read DEVELOPER_GUIDE.md sections 1-3
3. **Day 3**: Make a small UI change (edit a page)
4. **Day 4**: Add a new page to the frontend
5. **Day 5**: Read about how API requests work

### For Experienced Devs

1. **15 min**: Read DEVELOPER_GUIDE.md sections 1-2 (Architecture & Tech Stack)
2. **15 min**: Browse the codebase structure
3. **30 min**: Try adding a new API endpoint
4. **30 min**: Integrate the endpoint in the frontend

---

## 💡 Pro Tips

1. **Keep both servers running** - Frontend (port 5173) + Backend (port 8000)
2. **Use the browser DevTools** - Network tab shows API requests
3. **Check the API docs** - http://localhost:8000/docs is interactive
4. **Read error messages** - They usually tell you exactly what's wrong
5. **Git commit often** - Small, frequent commits are better

---

## 🆘 Need Help?

- **API not working?** → Check http://localhost:8000/docs to test endpoints
- **UI not updating?** → Check browser console (F12) for errors
- **Database issues?** → Verify .env has correct Supabase credentials
- **General questions?** → Read the [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

---

**Remember**: Both servers must be running at the same time for the app to work!

✅ **Frontend**: http://localhost:5173 (React UI)
✅ **Backend**: http://localhost:8000 (FastAPI)
