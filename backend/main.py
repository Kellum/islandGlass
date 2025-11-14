"""
Island Glass CRM - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import config

# Import routers
from routers import auth, clients, jobs, vendors, material_templates, work_items, site_visits, job_comments, job_vendor_materials, job_schedule, job_files, calculator

app = FastAPI(
    title=config.PROJECT_NAME,
    version=config.VERSION,
    description=config.DESCRIPTION,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# CORS Middleware - Allow React app to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Health check endpoints
@app.get("/api/health")
async def root():
    """API health check endpoint"""
    return {
        "status": "online",
        "service": "Island Glass CRM API",
        "version": config.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    # TODO: Add database connection check
    return {
        "status": "healthy",
        "database": "connected",  # Will implement actual check
        "timestamp": "2025-11-07T00:00:00Z",
    }


# Include routers
app.include_router(auth.router, prefix=f"{config.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(clients.router, prefix=f"{config.API_V1_PREFIX}/clients", tags=["Clients"])
app.include_router(jobs.router, prefix=f"{config.API_V1_PREFIX}/jobs", tags=["Jobs"])
app.include_router(vendors.router, prefix=f"{config.API_V1_PREFIX}/vendors", tags=["Vendors"])
app.include_router(material_templates.router, prefix=f"{config.API_V1_PREFIX}/material-templates", tags=["Material Templates"])
app.include_router(work_items.router, prefix=f"{config.API_V1_PREFIX}/work-items", tags=["Work Items"])
app.include_router(site_visits.router, prefix=f"{config.API_V1_PREFIX}/site-visits", tags=["Site Visits"])
app.include_router(job_comments.router, prefix=f"{config.API_V1_PREFIX}/job-comments", tags=["Job Comments"])
app.include_router(job_vendor_materials.router, prefix=f"{config.API_V1_PREFIX}/jobs/{{job_id}}/vendor-materials", tags=["Job Vendor Materials"])
app.include_router(job_schedule.router, prefix=f"{config.API_V1_PREFIX}/jobs/{{job_id}}/schedule", tags=["Job Schedule"])
app.include_router(job_files.router, prefix=f"{config.API_V1_PREFIX}/jobs/{{job_id}}/files", tags=["Job Files"])
app.include_router(calculator.router, prefix=f"{config.API_V1_PREFIX}/calculator", tags=["Calculator"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch-all exception handler for unexpected errors"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": str(request.url),
        },
    )


# Serve React frontend (must be LAST - after all API routes)
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
    print(f"✅ Serving frontend from {frontend_dist}")
else:
    print(f"⚠️  Frontend dist not found at {frontend_dist}")


if __name__ == "__main__":
    import uvicorn

    # Run with: python3 backend/main.py
    # Or: uvicorn backend.main:app --reload --port 8000
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info",
    )
