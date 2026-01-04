"""Review models.

This module defines Pydantic models for root beer reviews, including
sensory ratings, subjective scores, and metadata.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, UTC
from bson import ObjectId
from app.models.metadata import Metadata


class ReviewBase(BaseModel):
    """Base review schema.
    
    Contains all sensory ratings (1-5 scale), descriptive attributes,
    and subjective opinion scores for a root beer review.
    """
    root_beer_id: str
    # Structured sensory ratings (1-5 scale)
    sweetness: int = Field(..., ge=1, le=5)
    carbonation_bite: int = Field(..., ge=1, le=5)
    creaminess: int = Field(..., ge=1, le=5)
    acidity: int = Field(..., ge=1, le=5)
    aftertaste_length: int = Field(..., ge=1, le=5)
    # Descriptive attributes
    flavor_notes: List[str] = Field(default_factory=list)  # List of flavor note IDs
    tasting_notes: Optional[str] = None
    # Subjective opinion
    overall_score: int = Field(..., ge=1, le=10)
    would_drink_again: bool = True
    uniqueness_score: Optional[int] = Field(None, ge=1, le=10)
    # Metadata
    review_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    serving_context: Optional[str] = Field(None, max_length=50)  # Selected from dropdown


class ReviewCreate(ReviewBase):
    """Schema for creating a review.
    
    Inherits all fields from ReviewBase. All required fields must
    be provided when creating a new review.
    """
    pass


class ReviewUpdate(BaseModel):
    """Schema for updating a review.
    
    All fields are optional, allowing partial updates.
    Only provided fields will be updated.
    """
    root_beer_id: Optional[str] = None
    sweetness: Optional[int] = Field(None, ge=1, le=5)
    carbonation_bite: Optional[int] = Field(None, ge=1, le=5)
    creaminess: Optional[int] = Field(None, ge=1, le=5)
    acidity: Optional[int] = Field(None, ge=1, le=5)
    aftertaste_length: Optional[int] = Field(None, ge=1, le=5)
    flavor_notes: Optional[List[str]] = None
    tasting_notes: Optional[str] = None
    overall_score: Optional[int] = Field(None, ge=1, le=10)
    would_drink_again: Optional[bool] = None
    uniqueness_score: Optional[int] = Field(None, ge=1, le=10)
    review_date: Optional[datetime] = None
    serving_context: Optional[str] = Field(None, max_length=50)


class Review(ReviewBase, Metadata):
    """Review model with metadata.
    
    Complete review model including all base attributes and
    audit trail metadata (created_at, updated_at, etc.).
    """
    id: str = Field(alias="_id")  #: Review ID (MongoDB ObjectId as string)
    
    model_config = ConfigDict(
        populate_by_name=True,  #: Allow both _id and id field names
    )

