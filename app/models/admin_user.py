"""Admin user models."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId


class AdminUserBase(BaseModel):
    """Base admin user schema."""
    email: EmailStr
    is_active: bool = True


class AdminUserCreate(AdminUserBase):
    """Schema for creating an admin user."""
    password: str = Field(..., min_length=8)


class AdminUser(AdminUserBase):
    """Admin user model."""
    id: str = Field(alias="_id")
    hashed_password: str
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
        }


class AdminUserLogin(BaseModel):
    """Schema for admin login."""
    email: EmailStr
    password: str

