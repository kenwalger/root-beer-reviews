"""Root beer models.

This module defines Pydantic models for root beer entities, including
base schemas, creation/update schemas, and the full model with metadata.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from bson import ObjectId
from app.models.metadata import Metadata


class RootBeerBase(BaseModel):
    """Base root beer schema.
    
    Contains all objective attributes of a root beer that can be
    measured or observed without tasting.
    """
    name: str = Field(..., min_length=1, max_length=200)
    brand: str = Field(..., min_length=1, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    ingredients: Optional[str] = None
    sweetener_type: Optional[str] = Field(None, max_length=50)  # e.g., "cane sugar", "HFCS", "honey"
    sugar_grams_per_serving: Optional[float] = Field(None, ge=0)
    caffeine_mg: Optional[float] = Field(None, ge=0)
    alcohol_content: Optional[float] = Field(None, ge=0, le=100)  # % ABV
    color: Optional[str] = Field(None, max_length=50)  # Selected from dropdown
    carbonation_level: Optional[str] = Field(None, max_length=20)  # "low", "medium", "high"
    estimated_co2_volumes: Optional[float] = Field(None, ge=0, le=10)  # Optional CO2 volumes
    notes: Optional[str] = None
    images: Optional[List[str]] = Field(None, description="List of S3 image URLs")
    primary_image: Optional[str] = Field(None, description="URL of primary/featured image")


class RootBeerCreate(RootBeerBase):
    """Schema for creating a root beer.
    
    Inherits all fields from RootBeerBase. All fields are required
    except those marked as Optional.
    """
    pass


class RootBeerUpdate(BaseModel):
    """Schema for updating a root beer.
    
    All fields are optional, allowing partial updates.
    Only provided fields will be updated.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    brand: Optional[str] = Field(None, min_length=1, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    ingredients: Optional[str] = None
    sweetener_type: Optional[str] = Field(None, max_length=50)
    sugar_grams_per_serving: Optional[float] = Field(None, ge=0)
    caffeine_mg: Optional[float] = Field(None, ge=0)
    alcohol_content: Optional[float] = Field(None, ge=0, le=100)
    color: Optional[str] = Field(None, max_length=50)
    carbonation_level: Optional[str] = Field(None, max_length=20)
    estimated_co2_volumes: Optional[float] = Field(None, ge=0, le=10)
    notes: Optional[str] = None


class RootBeer(RootBeerBase, Metadata):
    """Root beer model with metadata.
    
    Complete root beer model including all base attributes and
    audit trail metadata (created_at, updated_at, etc.).
    """
    id: str = Field(alias="_id")  #: Root beer ID (MongoDB ObjectId as string)
    
    model_config = ConfigDict(
        populate_by_name=True,  #: Allow both _id and id field names
    )

