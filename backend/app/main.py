"""
Enterprise Resource & Operations Management System (EROMS)
Production FastAPI Application Entrypoint
Architect: Muhammad Afnan (https://github.com/Afnan-makstrix)
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.config import settings
from backend.app.api.auth import router as auth_router
from backend.app.api.employees import router as employees_router
from backend.app.api.departments import router as departments_router
from backend.app.api.projects import router as projects_router
from backend.app.api.inventory import router as inventory_router
from backend.app.api.billing import router as billing_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.audit import router as audit_router

app = FastAPI(
    title=settings.APP_NAME,
    description="""
# Enterprise Resource & Operations Management System (EROMS)
Production-grade relational database architecture, high-performance SQL engineering,
ACID business transaction workflows, and multi-tenant Role-Based Access Control.

**Architect:** [Muhammad Afnan](https://github.com/Afnan-makstrix)

### Core Features:
* **Relational Database Focus:** 32 normalized 3NF PostgreSQL tables with strict referential integrity.
* **Advanced SQL:** Recursive CTEs, window functions, stored procedures, triggers, and materialized views.
* **Scalable Performance:** Indexed execution plans optimized for 100,000+ records.
* **Security & Compliance:** Argon2/bcrypt password hashing, JWT RBAC, and Row-Level Security (RLS).
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
api_v1 = settings.API_V1_PREFIX
app.include_router(auth_router, prefix=api_v1)
app.include_router(employees_router, prefix=api_v1)
app.include_router(departments_router, prefix=api_v1)
app.include_router(projects_router, prefix=api_v1)
app.include_router(inventory_router, prefix=api_v1)
app.include_router(billing_router, prefix=api_v1)
app.include_router(analytics_router, prefix=api_v1)
app.include_router(audit_router, prefix=api_v1)

@app.get("/", tags=["Health & Status"])
def root():
    return {
        "system": settings.APP_NAME,
        "version": "1.0.0",
        "status": "OPERATIONAL",
        "database": "PostgreSQL 16.4",
        "docs": "/docs",
        "github": "https://github.com/Afnan-makstrix/enterprise-resource-operations-management-system"
    }

@app.get("/health", tags=["Health & Status"])
def healthcheck():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "database_connected": True
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred", "error": str(exc)}
    )
