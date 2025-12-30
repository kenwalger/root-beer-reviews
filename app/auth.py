"""Authentication utilities."""
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import settings
from fastapi import HTTPException, status
from app.database import get_database
from app.models.admin_user import AdminUser
from bson import ObjectId


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        # Bcrypt expects bytes
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    # Bcrypt has a 72-byte limit, so truncate if password is too long
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode a JWT access token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


async def get_admin_user_by_email(email: str) -> AdminUser | None:
    """Get admin user by email."""
    db = get_database()
    user_doc = await db.admin_users.find_one({"email": email})
    if user_doc:
        user_doc["_id"] = str(user_doc["_id"])
        return AdminUser(**user_doc)
    return None


async def authenticate_admin(email: str, password: str) -> AdminUser | None:
    """Authenticate an admin user."""
    user = await get_admin_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


async def initialize_admin_user():
    """Initialize the admin user from environment variables if it doesn't exist."""
    db = get_database()
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

