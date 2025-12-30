"""Metadata model for audit trails."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from bson import ObjectId


class Metadata(BaseModel):
    """Metadata for audit trails on all documents."""
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # user_id or admin email
    updated_by: Optional[str] = None  # user_id or admin email
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str,
        }

