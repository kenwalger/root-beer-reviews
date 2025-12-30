"""Flavor note models."""
from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from app.models.metadata import Metadata


class FlavorNoteBase(BaseModel):
    """Base flavor note schema."""
    name: str = Field(..., min_length=1, max_length=50)
    category: Optional[str] = Field(None, max_length=50)  # e.g., "Traditional", "Sweet & Creamy", "Spice & Herbal"


class FlavorNoteCreate(FlavorNoteBase):
    """Schema for creating a flavor note."""
    pass


class FlavorNote(FlavorNoteBase, Metadata):
    """Flavor note model with metadata."""
    id: str = Field(alias="_id")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
        }

