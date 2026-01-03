"""Admin user models.

This module defines Pydantic models for admin user accounts,
including authentication and user management schemas.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId


class AdminUserBase(BaseModel):
    """Base admin user schema.
    
    Contains basic admin user information without sensitive data.
    """
    email: EmailStr
    is_active: bool = True


class AdminUserCreate(AdminUserBase):
    """Schema for creating an admin user.
    
    Includes password field which will be hashed before storage.
    """
    password: str = Field(..., min_length=8)  #: Plain text password (min 8 characters)


class AdminUser(AdminUserBase):
    """Admin user model.
    
    Complete admin user model with hashed password. The password
    is never returned in API responses for security.
    """
    id: str = Field(alias="_id")  #: Admin user ID (MongoDB ObjectId as string)
    hashed_password: str  #: Bcrypt hashed password
    
    class Config:
        """Pydantic configuration."""
        populate_by_name = True  #: Allow both _id and id field names
        json_encoders = {
            ObjectId: str,  #: Convert ObjectId to string in JSON
        }


class AdminUserLogin(BaseModel):
    """Schema for admin login.
    
    Used for login form validation.
    """
    email: EmailStr  #: Admin email address
    password: str  #: Plain text password

