"""Metadata model for audit trails.

This module defines the Metadata base model that provides audit trail
functionality for all documents in the system.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from bson import ObjectId


class Metadata(BaseModel):
    """Metadata for audit trails on all documents.
    
    This mixin class provides automatic tracking of creation/update
    timestamps and user information for all database documents.
    """
    
    created_at: datetime = Field(default_factory=datetime.utcnow)  #: Document creation timestamp
    updated_at: datetime = Field(default_factory=datetime.utcnow)  #: Document last update timestamp
    created_by: Optional[str] = None  #: User ID or admin email who created the document
    updated_by: Optional[str] = None  #: User ID or admin email who last updated the document
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),  #: Convert datetime to ISO format
            ObjectId: str,  #: Convert ObjectId to string in JSON
        }

