# Token Refresh Solution for Island Glass CRM

## Problem
JWT tokens from Supabase expire after 1 hour by default, causing "JWT expired" errors and forcing users to log back in frequently during long work sessions.

## Solution: Multi-Layered Approach

### Layer 1: Extend Token Lifetime in Supabase (EASIEST)
**Configure Supabase to issue longer-lived tokens**

#### Steps:
1. Go to Supabase Dashboard → Authentication → Settings
2. Find "JWT expiry limit" setting
3. Change from `3600` (1 hour) to `28800` (8 hours) or `86400` (24 hours)
4. Click Save

**Pros:**
- ✅ Zero code changes needed
- ✅ Immediate effect
- ✅ Simple to implement

**Cons:**
- ❌ Still need to log in daily
- ❌ Slightly less secure (longer window if token stolen)

**Recommendation:** Set to 8 hours (28800 seconds) for a full work day

---

### Layer 2: Automatic Token Refresh (BEST UX)
**Implement silent background token refresh**

Supabase provides a `refresh_token` with each login that can be used to get a new `access_token` without re-entering credentials.

#### Implementation Required:

1. **Add refresh method to auth.py**
```python
def refresh_session(self, refresh_token: str) -> Dict:
    """Refresh an expired session using refresh_token"""
    try:
        response = self.client.auth.refresh_session(refresh_token)
        return {
            'success': True,
            'session': {
                'access_token': response.session.access_token,
                'refresh_token': response.session.refresh_token,
                'expires_at': response.session.expires_at
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

2. **Add periodic refresh callback to dash_app.py**
```python
@app.callback(
    Output('session-store', 'data', allow_duplicate=True),
    Input('refresh-interval', 'n_intervals'),
    State('session-store', 'data'),
    prevent_initial_call=True
)
def refresh_token_periodically(n_intervals, session_data):
    """Refresh token every 50 minutes (before 60 min expiry)"""
    if not session_data or not session_data.get('session'):
        raise PreventUpdate

    refresh_token = session_data['session'].get('refresh_token')
    if not refresh_token:
        raise PreventUpdate

    auth = AuthManager()
    result = auth.refresh_session(refresh_token)

    if result['success']:
        # Update session with new tokens
        session_data['session'] = result['session']
        return session_data

    # Refresh failed - redirect to login
    return None
```

3. **Add dcc.Interval component**
```python
dcc.Interval(
    id='refresh-interval',
    interval=50*60*1000,  # 50 minutes in milliseconds
    n_intervals=0
)
```

**Pros:**
- ✅ User never gets logged out
- ✅ Works for multi-day sessions
- ✅ Like Gmail/Google Workspace

**Cons:**
- ❌ Requires code changes
- ❌ More complex to implement

---

### Layer 3: Graceful Error Handling (MINIMUM)
**Detect expired tokens and handle gracefully**

#### Implementation:

1. **Add error detection wrapper to database.py**
```python
def handle_jwt_expiry(func):
    """Decorator to catch JWT expiry and redirect to login"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            if 'JWT expired' in str(e) or e.code == 'PGRST303':
                # Return special error that triggers logout
                return {'error': 'SESSION_EXPIRED'}
            raise
    return wrapper
```

2. **Update all page callbacks to check for SESSION_EXPIRED**
```python
def calculate_price(...):
    db = get_authenticated_db(session_data)
    result = db.get_calculator_config()

    if isinstance(result, dict) and result.get('error') == 'SESSION_EXPIRED':
        return dmc.Notification(
            title="Session Expired",
            message="Your session has expired. Please log in again.",
            action="show",
            color="red",
            icon=DashIconify(icon="solar:logout-bold"),
            autoClose=3000
        )
    # ... rest of callback
```

3. **Add clientside callback to redirect on expiry**
```python
app.clientside_callback(
    """
    function(sessionData) {
        if (!sessionData || !sessionData.session) {
            window.location.href = '/login';
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('dummy', 'children'),
    Input('session-store', 'data')
)
```

**Pros:**
- ✅ Better UX than cryptic error
- ✅ User knows what happened
- ✅ Auto-redirects to login

**Cons:**
- ❌ Still have to log back in
- ❌ Lose unsaved work

---

## Recommended Implementation Plan

### Phase 1: Quick Fix (5 minutes)
**Extend token lifetime in Supabase to 8 hours**
- Go to Supabase Dashboard
- Authentication → Settings
- JWT expiry limit: `28800`
- Save

This gives you immediate relief for full work days.

### Phase 2: Token Refresh (1-2 hours development)
**Implement automatic background refresh**
- Add refresh method to AuthManager
- Add periodic callback
- Add dcc.Interval component
- Test with short expiry (5 min) to verify it works
- Deploy

This provides seamless multi-day sessions.

### Phase 3: Error Handling (30 minutes)
**Add graceful fallback for edge cases**
- Wrap database calls with error detection
- Show notification on expiry
- Auto-redirect to login
- Save form data to localStorage before redirect

This handles the rare case where refresh fails.

---

## Alternative: "Remember Me" Feature

Instead of long-lived tokens, implement a "Remember Me" checkbox:
- If checked: Store refresh_token in localStorage (persists across browser closes)
- On app load: Check for refresh_token, auto-login silently
- User effectively stays logged in for 30 days (Supabase refresh token lifetime)

This is how banking apps work - they're technically logged out but auto-login on open.

---

## Security Considerations

**Token Lifetime:**
- Longer tokens = slightly less secure
- 8 hours is reasonable for office environment
- 24 hours acceptable if network is trusted

**Token Storage:**
- Currently in sessionStorage (cleared on browser close)
- For "Remember Me", would move to localStorage
- Refresh tokens are more secure to store than passwords

**Best Practice:**
- Use HTTPS only (you should already)
- Implement auto-logout on idle (no activity for 30min)
- Add "Lock Screen" feature for quick away-from-desk protection

---

## Testing Plan

1. **Set JWT expiry to 5 minutes** (temporarily for testing)
2. Log in
3. Wait 6 minutes
4. Try to use calculator
5. **Expected:** Token should refresh automatically OR show nice error message
6. **Set JWT expiry back to 8 hours** for production

---

## Files to Modify

- `modules/auth.py` - Add refresh_session() method
- `dash_app.py` - Add refresh interval and callback
- `modules/database.py` - Add error handling wrapper
- All page files - Add SESSION_EXPIRED checks (optional)

---

## Estimated Time
- Phase 1 (Extend): 5 minutes ✅
- Phase 2 (Refresh): 1-2 hours
- Phase 3 (Errors): 30 minutes

**Total:** ~2-3 hours for complete solution

---

## Quick Start: Do This Now

**Immediate fix (5 minutes):**
1. Open Supabase Dashboard
2. Go to Project Settings → Authentication
3. Find "JWT Expiry Limit"
4. Change to `28800` (8 hours)
5. Click Save

This solves 90% of the problem immediately!
