"""
Authentication Router
Handles login, token refresh, and user session management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from jose import jwt
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config
from models.user import UserLogin, Token, RefreshTokenRequest, UserResponse, TokenData
from middleware.auth import get_current_user
from auth import AuthManager
from database import Database

router = APIRouter()


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=config.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Login endpoint - authenticate user and return JWT tokens

    Request body:
        {
            "email": "user@example.com",
            "password": "securepassword"
        }

    Returns:
        {
            "access_token": "eyJ...",
            "refresh_token": "eyJ...",
            "token_type": "bearer",
            "expires_in": 3600
        }
    """
    try:
        # Initialize auth with Supabase
        auth = AuthManager()

        # Attempt login with Supabase (login is the method name in AuthManager)
        result = auth.login(credentials.email, credentials.password)

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.get("error", "Invalid credentials"),
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract user data from Supabase response
        user_data = result.get("user", {})
        user_id = user_data.get("id")
        email = user_data.get("email")

        # Get user from database to get company_id
        db = Database()
        user = db.get_user_by_id(user_id)
        company_id = user.get("company_id") if user else None

        # Create JWT tokens
        token_data = {
            "sub": email,
            "user_id": user_id,
            "company_id": company_id,
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}",
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh token endpoint - exchange refresh token for new access token

    Request body:
        {
            "refresh_token": "eyJ..."
        }

    Returns:
        {
            "access_token": "eyJ...",
            "refresh_token": "eyJ...",
            "token_type": "bearer",
            "expires_in": 3600
        }
    """
    try:
        # Decode and verify refresh token
        payload = jwt.decode(request.refresh_token, config.SECRET_KEY, algorithms=[config.ALGORITHM])

        # Check if it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        # Extract user data
        email = payload.get("sub")
        user_id = payload.get("user_id")
        company_id = payload.get("company_id")

        if not email or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        # Create new tokens
        token_data = {
            "sub": email,
            "user_id": user_id,
            "company_id": company_id,
        }

        access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """
    Get current user information

    Requires: Authorization header with Bearer token

    Returns:
        {
            "id": "user-uuid",
            "email": "user@example.com",
            "full_name": "John Doe",
            "company_id": "company-uuid",
            "role": "admin",
            "department": "Sales",
            "created_at": "2024-01-01T00:00:00Z"
        }
    """
    try:
        # Get full user from database
        db = Database()
        user = db.get_user_by_id(current_user.user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return UserResponse(
            id=user.get("id"),
            email=user.get("email"),
            full_name=user.get("full_name"),
            company_id=user.get("company_id"),
            role=user.get("role"),
            department=user.get("department"),
            created_at=user.get("created_at"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}",
        )


@router.post("/logout")
async def logout(current_user: TokenData = Depends(get_current_user)):
    """
    Logout endpoint (for consistency - JWT tokens are stateless)

    In a JWT system, logout is typically handled client-side by deleting the token.
    This endpoint exists for:
    1. Future token blacklisting implementation
    2. Audit logging
    3. Client-side confirmation

    Returns:
        {
            "message": "Logged out successfully"
        }
    """
    # TODO: In future, add token to blacklist in Redis or database
    # For now, just return success (client should delete token)

    return {
        "message": "Logged out successfully",
        "user_id": current_user.user_id,
    }
