"""
FastAPI Configuration
Environment variables and settings for the Island Glass CRM backend
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Supabase Configuration (from existing .env)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://localhost:3001",  # React dev server (alternate port)
    "http://localhost:5173",  # Vite dev server
    "http://localhost:8050",  # Old Dash app (for transition)
]

# File Upload Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]

# Database Configuration
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20

# API Configuration
API_V1_PREFIX = "/api/v1"
PROJECT_NAME = "Island Glass CRM API"
VERSION = "1.0.0"
DESCRIPTION = """
Island Glass CRM Backend API

Features:
- JWT Authentication
- Client Management (CRUD)
- Job/PO Management
- File Upload
- Calculator Operations
- QuickBooks Integration (future)
- Lead Scraping (future)
"""
