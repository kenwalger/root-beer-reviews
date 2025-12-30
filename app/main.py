"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import auth, admin, public
from app.auth import initialize_admin_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    await connect_to_mongo()
    await initialize_admin_user()
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

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(public.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

