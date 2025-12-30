"""Root beer models."""
from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId
from app.models.metadata import Metadata


class RootBeerBase(BaseModel):
    """Base root beer schema."""
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


class RootBeerCreate(RootBeerBase):
    """Schema for creating a root beer."""
    pass


class RootBeerUpdate(BaseModel):
    """Schema for updating a root beer."""
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
    """Root beer model with metadata."""
    id: str = Field(alias="_id")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
        }

