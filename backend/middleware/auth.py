"""
Authentication Middleware for FastAPI
JWT token verification and user injection
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import sys
import os

# Add parent directory to path so we can import config and models
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config
from models.user import TokenData

# HTTP Bearer token scheme
security = HTTPBearer()


def verify_token(token: str) -> TokenData:
    """
    Verify JWT token and extract user data

    Args:
        token: JWT token string

    Returns:
        TokenData with user information

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])

        # Extract user data from token
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        company_id: str = payload.get("company_id")

        if email is None or user_id is None:
            raise credentials_exception

        return TokenData(email=email, user_id=user_id, company_id=company_id)

    except JWTError:
        raise credentials_exception


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """
    Dependency to get current authenticated user

    Usage in route:
        @app.get("/protected")
        async def protected_route(current_user: TokenData = Depends(get_current_user)):
            # current_user.user_id, current_user.email, current_user.company_id available
            return {"user_id": current_user.user_id}

    Args:
        credentials: HTTP Authorization header with Bearer token

    Returns:
        TokenData with user information

    Raises:
        HTTPException: If token is missing or invalid
    """
    token = credentials.credentials
    return verify_token(token)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[TokenData]:
    """
    Optional authentication - returns None if no token provided
    Useful for endpoints that work differently for authenticated vs anonymous users

    Usage:
        @app.get("/optional-auth")
        async def optional_auth_route(current_user: Optional[TokenData] = Depends(get_current_user_optional)):
            if current_user:
                return {"message": f"Hello {current_user.email}"}
            else:
                return {"message": "Hello guest"}
    """
    if credentials is None:
        return None

    try:
        return verify_token(credentials.credentials)
    except HTTPException:
        return None
