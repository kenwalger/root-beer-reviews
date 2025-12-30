"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.auth import authenticate_admin, create_access_token, decode_access_token
from app.database import get_database
from datetime import timedelta
from app.config import settings


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_current_admin(request: Request) -> dict:
    """Get current admin from session token."""
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


@router.get("/admin/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display login page."""
    return templates.TemplateResponse("admin/login.html", {"request": request})


@router.post("/admin/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """Handle admin login."""
    user = await authenticate_admin(email, password)
    if not user:
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "error": "Incorrect email or password"},
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
        max_age=86400,  # 24 hours
    )
    return response


@router.get("/admin/logout")
async def logout():
    """Handle admin logout."""
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("admin_token")
    return response


def require_admin(request: Request = Depends(get_current_admin)):
    """Dependency to require admin authentication."""
    return request

