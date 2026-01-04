"""Authentication routes.

This module handles admin authentication, login, logout, and provides
dependency functions for route protection.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from typing import Optional
from app.auth import authenticate_admin, create_access_token, decode_access_token
from app.database import get_database
from app.templates_helpers import templates
from datetime import timedelta
from app.config import settings


router = APIRouter()


def get_current_admin(request: Request) -> dict[str, str]:
    """Get current admin from session token.
    
    Extracts and validates the admin JWT token from cookies.
    
    :param request: FastAPI request object
    :type request: Request
    :returns: Dictionary with admin email
    :rtype: dict[str, str]
    :raises HTTPException: If token is missing or invalid
    """
    token = request.cookies.get("admin_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return {"email": email}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def get_admin_optional(request: Request) -> Optional[dict[str, str]]:
    """Get current admin from session token if available.
    
    Non-blocking version that returns None if not authenticated.
    Used in public routes to conditionally show admin UI elements.
    
    :param request: FastAPI request object
    :type request: Request
    :returns: Dictionary with admin email if authenticated, None otherwise
    :rtype: Optional[dict[str, str]]
    """
    token = request.cookies.get("admin_token")
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            return None
        return {"email": email}
    except Exception:
        return None


@router.get("/admin/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    """Display login page.
    
    :param request: FastAPI request object
    :type request: Request
    :returns: HTML response with login page
    :rtype: HTMLResponse
    """
    return templates.TemplateResponse(request, "admin/login.html", {})


@router.post("/admin/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """Handle admin login.
    
    Authenticates the admin user and sets a secure HTTP-only cookie
    with the JWT access token.
    
    :param request: FastAPI request object
    :type request: Request
    :param email: Admin email address
    :type email: str
    :param password: Admin password
    :type password: str
    :returns: Redirect to admin dashboard on success, login page with error on failure
    :rtype: RedirectResponse | HTMLResponse
    """
    user = await authenticate_admin(email, password)
    if not user:
        return templates.TemplateResponse(
            request,
            "admin/login.html",
            {"error": "Incorrect email or password"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(hours=24)
    )
    
    response = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="admin_token",
        value=access_token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        path="/",  # Make cookie available across all routes
        max_age=86400,  # 24 hours
        domain=None,  # Allow cookie on localhost and all subdomains
    )
    return response


@router.get("/admin/logout")
async def logout() -> RedirectResponse:
    """Handle admin logout.
    
    Deletes the admin authentication cookie and redirects to login page.
    
    :returns: Redirect to login page
    :rtype: RedirectResponse
    """
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(
        "admin_token", 
        path="/",
        domain=None,  # Match the domain used when setting the cookie
        samesite="lax"
    )
    return response


async def require_admin(request: Request) -> dict[str, str]:
    """Dependency to require admin authentication.
    
    FastAPI dependency function that ensures the route is only accessible
    to authenticated admin users. Raises HTTPException if not authenticated.
    
    :param request: FastAPI request object
    :type request: Request
    :returns: Dictionary with admin email
    :rtype: dict[str, str]
    :raises HTTPException: If user is not authenticated
    """
    try:
        return get_current_admin(request)
    except HTTPException:
        # Re-raise to be handled by exception handler
        raise

