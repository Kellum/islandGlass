"""
Session Middleware for Island Glass CRM

This module provides automatic user_id injection into all callbacks,
solving the State("session-store", "data") blocking issue that plagued v1.

Usage in callbacks:
    from modules.session_middleware import require_auth

    @callback(...)
    @require_auth
    def my_callback(..., current_user=None):
        # current_user is automatically injected!
        # Contains: {id, email, company_id}
        user_id = current_user['id']
        company_id = current_user['company_id']
"""

from functools import wraps
from flask import session as flask_session
from dash import callback_context, no_update
import dash
import jwt
import os


def get_current_user_from_session():
    """
    Extract current user from Flask session

    Returns:
        dict: User data {id, email, company_id} or None if not authenticated
    """
    try:
        # Check if we're in a request context
        if not callback_context.triggered:
            return None

        # Get session data from Flask session
        session_data = flask_session.get('session_data')

        if not session_data:
            return None

        if not session_data.get('authenticated'):
            return None

        # Extract user info
        user = session_data.get('session', {}).get('user', {})

        if not user or not user.get('id'):
            return None

        return {
            'id': user.get('id'),
            'email': user.get('email'),
            'company_id': user.get('company_id')
        }

    except Exception as e:
        print(f"⚠️  Error getting current user: {e}")
        return None


def require_auth(callback_func):
    """
    Decorator that injects current_user into callback

    Usage:
        @callback(...)
        @require_auth
        def my_callback(n_clicks, current_user=None):
            user_id = current_user['id']  # Automatically available!
            ...

    If user is not authenticated, callback returns no_update for all outputs.
    """
    @wraps(callback_func)
    def wrapper(*args, **kwargs):
        # Get current user
        current_user = get_current_user_from_session()

        if not current_user:
            print(f"⚠️  {callback_func.__name__}: No authenticated user, returning no_update")
            # Return no_update for all outputs
            return dash.no_update

        # Inject current_user into kwargs
        kwargs['current_user'] = current_user

        # Log for debugging
        print(f"✅ {callback_func.__name__}: User {current_user['email']} ({current_user['id']})")

        # Call original callback with injected user
        return callback_func(*args, **kwargs)

    return wrapper


def optional_auth(callback_func):
    """
    Decorator that injects current_user but doesn't block if not authenticated

    Usage:
        @callback(...)
        @optional_auth
        def my_callback(n_clicks, current_user=None):
            if current_user:
                user_id = current_user['id']
            else:
                # Show login prompt or limited functionality
                ...
    """
    @wraps(callback_func)
    def wrapper(*args, **kwargs):
        # Get current user (may be None)
        current_user = get_current_user_from_session()

        # Inject current_user into kwargs (may be None)
        kwargs['current_user'] = current_user

        if current_user:
            print(f"✅ {callback_func.__name__}: User {current_user['email']}")
        else:
            print(f"ℹ️  {callback_func.__name__}: No authenticated user (optional)")

        # Call original callback
        return callback_func(*args, **kwargs)

    return wrapper


def store_session_in_flask(session_data):
    """
    Store session data in Flask session (called by login callback)

    Args:
        session_data (dict): Session data from Supabase auth
    """
    flask_session['session_data'] = session_data
    flask_session.permanent = True  # Make session persistent
    print(f"✅ Session stored in Flask for user: {session_data.get('session', {}).get('user', {}).get('email')}")


def clear_flask_session():
    """Clear Flask session (called by logout)"""
    flask_session.clear()
    print("✅ Flask session cleared")
