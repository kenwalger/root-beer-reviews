"""Flavor note models.

This module defines Pydantic models for flavor notes, which are
descriptive tags used in reviews to characterize root beer flavors.
"""
from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from app.models.metadata import Metadata


class FlavorNoteBase(BaseModel):
    """Base flavor note schema.
    
    Represents a flavor characteristic that can be identified in
    a root beer (e.g., "Vanilla", "Sassafras", "Cinnamon").
    """
    name: str = Field(..., min_length=1, max_length=50)
    category: Optional[str] = Field(None, max_length=50)  # e.g., "Traditional", "Sweet & Creamy", "Spice & Herbal"


class FlavorNoteCreate(FlavorNoteBase):
    """Schema for creating a flavor note.
    
    Inherits all fields from FlavorNoteBase.
    """
    pass


class FlavorNote(FlavorNoteBase, Metadata):
    """Flavor note model with metadata.
    
    Complete flavor note model including base attributes and
    audit trail metadata.
    """
    id: str = Field(alias="_id")  #: Flavor note ID (MongoDB ObjectId as string)
    
    class Config:
        """Pydantic configuration."""
        populate_by_name = True  #: Allow both _id and id field names
        json_encoders = {
            ObjectId: str,  #: Convert ObjectId to string in JSON
        }

