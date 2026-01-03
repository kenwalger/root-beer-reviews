"""Main FastAPI application.

This module initializes the FastAPI application, configures logging,
sets up database connections, and registers all route handlers.
"""
from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.exceptions import HTTPException
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

from app.database import connect_to_mongo, close_mongo_connection
from app.routes import auth, admin, public
from app.auth import initialize_admin_user
from app.seed_data import seed_default_data


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup and shutdown.
    
    Handles application lifecycle events:
    - Startup: Connect to MongoDB, initialize admin user, seed default data
    - Shutdown: Close MongoDB connection
    
    :param app: FastAPI application instance
    :type app: FastAPI
    :yields: None
    :rtype: AsyncGenerator[None, None]
    """
    # Startup
    await connect_to_mongo()
    await initialize_admin_user()
    await seed_default_data()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title="Root Beer Review App",
    description="A structured, data-driven root beer review application",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Serve service worker at root level (required for PWA)
@app.get("/service-worker.js")
async def service_worker() -> FileResponse:
    """Serve the service worker file.
    
    :returns: Service worker JavaScript file
    :rtype: FileResponse
    """
    service_worker_path = os.path.join("app", "static", "service-worker.js")
    return FileResponse(
        service_worker_path,
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/"}
    )

# Serve favicon at root level (browsers automatically request /favicon.ico)
@app.get("/favicon.ico")
async def favicon() -> FileResponse:
    """Serve the favicon file.
    
    Attempts to locate favicon in multiple locations:
    1. Root directory (favicon.ico)
    2. app/static/icons/ (favicon.ico)
    3. Fallback to icon-192x192.png
    
    :returns: Favicon image file
    :rtype: FileResponse
    :raises HTTPException: If favicon is not found in any location
    """
    # Try multiple locations: root, then icons directory, then fall back to icon-192x192.png
    favicon_paths = [
        "favicon.ico",  # Root directory
        os.path.join("app", "static", "icons", "favicon.ico"),  # Icons directory
        os.path.join("app", "static", "icons", "icon-192x192.png"),  # Fallback
    ]
    for favicon_path in favicon_paths:
        if os.path.exists(favicon_path):
            return FileResponse(
                favicon_path,
                media_type="image/x-icon" if favicon_path.endswith(".ico") else "image/png"
            )
    # If nothing found, return 404
    raise HTTPException(status_code=404, detail="Favicon not found")

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(public.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, 
    exc: HTTPException
) -> RedirectResponse | dict:
    """Handle HTTP exceptions, redirecting 401s to login for admin routes.
    
    :param request: FastAPI request object
    :type request: Request
    :param exc: HTTP exception that was raised
    :type exc: HTTPException
    :returns: RedirectResponse for 401 on admin routes, JSONResponse otherwise
    :rtype: RedirectResponse | dict
    """
    # If it's a 401 and we're on an admin route, redirect to login
    if exc.status_code == status.HTTP_401_UNAUTHORIZED and request.url.path.startswith("/admin"):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    # Otherwise, return the default error response
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.
    
    :returns: Health status dictionary
    :rtype: dict[str, str]
    """
    return {"status": "healthy"}

