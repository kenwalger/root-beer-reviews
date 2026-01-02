"""Main FastAPI application."""
from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from contextlib import asynccontextmanager
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import auth, admin, public
from app.auth import initialize_admin_user
from app.seed_data import seed_default_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
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
async def service_worker():
    """Serve the service worker file."""
    from fastapi.responses import FileResponse
    import os
    service_worker_path = os.path.join("app", "static", "service-worker.js")
    return FileResponse(
        service_worker_path,
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/"}
    )

# Serve favicon at root level (browsers automatically request /favicon.ico)
@app.get("/favicon.ico")
async def favicon():
    """Serve the favicon file."""
    from fastapi.responses import FileResponse
    import os
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
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Favicon not found")

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(public.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions, redirecting 401s to login for admin routes."""
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
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

