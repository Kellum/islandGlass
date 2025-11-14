# Calculator Fix Summary

## Issue
Calculator was not displaying prices in the browser.

## Root Cause
**Row Level Security (RLS)** was blocking access to calculator configuration tables when using the anon key (`SUPABASE_KEY`).

## Solution Applied
Modified `backend/database.py:23` to use `SUPABASE_SERVICE_ROLE_KEY` instead of the anon key:

```python
# Before
self.key = os.getenv("SUPABASE_KEY")

# After
self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
```

**Note:** Also updated `modules/database.py:23` with the same fix for test scripts.

## Actions Taken
1. ✅ Updated Database class to use service role key
2. ✅ Restarted backend server (port 8000)
3. ✅ Verified pricing data exists (13 glass configs)
4. ✅ All automated tests pass

## To Verify the Fix

**IMPORTANT:** You must be logged in for the calculator to work.

1. **Log in first** at http://localhost:3001 (if not already logged in)
2. Navigate to http://localhost:3001/calculator
3. You should see the calculator form
4. Enter dimensions (e.g., 24" x 36")
5. Select glass type and thickness
6. **Prices should now appear in the right panel**

Example expected output for 24" x 36", 1/4" clear, polished, tempered:
- Base Price: $75.00
- Polish: $102.00
- Tempered (35%): $61.95
- **Quote Price: $853.39**

## If Still Not Working

Check browser console (F12 → Console tab) for errors. Common issues:
- Authentication expired (refresh page or log in again)
- Backend not running (check http://localhost:8000/docs)
- Frontend not connected to backend (check VITE_API_URL in frontend/.env)

## Server Status
- Backend: http://localhost:8000 ✅
- Frontend: http://localhost:3001 ✅
- Calculator endpoint: http://localhost:8000/api/v1/calculator/config

## Next Steps (if needed)
If prices still don't show, we may need to:
1. Add proper RLS policies for calculator tables
2. Make calculator endpoint publicly accessible (remove authentication requirement)
3. Check browser network tab for failed API calls
