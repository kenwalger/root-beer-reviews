"""Authentication utilities.

This module provides password hashing, JWT token creation/validation,
and admin user authentication functions.
"""
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings
from fastapi import HTTPException, status
from app.database import get_database
from app.models.admin_user import AdminUser
from bson import ObjectId


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.
    
    :param plain_password: Plain text password to verify
    :type plain_password: str
    :param hashed_password: Bcrypt hashed password
    :type hashed_password: str
    :returns: True if password matches, False otherwise
    :rtype: bool
    """
    try:
        # Bcrypt expects bytes
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt.
    
    Passwords longer than 72 bytes are truncated to meet bcrypt's limit.
    
    :param password: Plain text password to hash
    :type password: str
    :returns: Bcrypt hashed password as UTF-8 string
    :rtype: str
    """
    # Bcrypt has a 72-byte limit, so truncate if password is too long
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.
    
    :param data: Dictionary of data to encode in the token
    :type data: dict
    :param expires_delta: Optional expiration time delta (default: 24 hours)
    :type expires_delta: Optional[timedelta]
    :returns: Encoded JWT token string
    :rtype: str
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode a JWT access token.
    
    :param token: JWT token string to decode
    :type token: str
    :returns: Decoded token payload dictionary
    :rtype: dict
    :raises HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        # Raise exception that will be caught and handled by get_current_admin
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


async def get_admin_user_by_email(email: str) -> Optional[AdminUser]:
    """Get admin user by email.
    
    :param email: Admin user email address
    :type email: str
    :returns: AdminUser instance if found, None otherwise
    :rtype: Optional[AdminUser]
    """
    db = get_database()
    if not db:
        return None
    user_doc = await db.admin_users.find_one({"email": email})
    if user_doc:
        user_doc["_id"] = str(user_doc["_id"])
        return AdminUser(**user_doc)
    return None


async def authenticate_admin(email: str, password: str) -> Optional[AdminUser]:
    """Authenticate an admin user.
    
    Verifies the email and password against the database and checks
    if the user account is active.
    
    :param email: Admin user email address
    :type email: str
    :param password: Plain text password
    :type password: str
    :returns: AdminUser instance if authentication succeeds, None otherwise
    :rtype: Optional[AdminUser]
    """
    user = await get_admin_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


async def initialize_admin_user() -> None:
    """Initialize the admin user from environment variables if it doesn't exist.
    
    Creates the initial admin user from ADMIN_EMAIL and ADMIN_PASSWORD
    environment variables if they are set and no admin user exists yet.
    This is typically only needed for the first application startup.
    
    :raises Exception: If database operations fail
    """
    # Only initialize if admin_email and admin_password are provided
    if not settings.admin_email or not settings.admin_password:
        print("Skipping admin user initialization: ADMIN_EMAIL and ADMIN_PASSWORD not set")
        print("Note: If this is the first run, set these environment variables to create the initial admin user.")
        return
    
    db = get_database()
    if not db:
        print("Database not available for admin user initialization")
        return
    existing = await db.admin_users.find_one({"email": settings.admin_email})
    if not existing:
        admin_user = {
            "email": settings.admin_email,
            "hashed_password": get_password_hash(settings.admin_password),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": "system",
            "updated_by": "system",
        }
        await db.admin_users.insert_one(admin_user)
        print(f"Initialized admin user: {settings.admin_email}")
    else:
        print(f"Admin user already exists: {settings.admin_email}")

