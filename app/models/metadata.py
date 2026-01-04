"""Metadata model for audit trails.

This module defines the Metadata base model that provides audit trail
functionality for all documents in the system.
"""
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from datetime import datetime, UTC
from typing import Optional
from bson import ObjectId


class Metadata(BaseModel):
    """Metadata for audit trails on all documents.
    
    This mixin class provides automatic tracking of creation/update
    timestamps and user information for all database documents.
    """
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))  #: Document creation timestamp
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))  #: Document last update timestamp
    created_by: Optional[str] = None  #: User ID or admin email who created the document
    updated_by: Optional[str] = None  #: User ID or admin email who last updated the document
    
    model_config = ConfigDict(
        populate_by_name=True,  #: Allow both _id and id field names
    )
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, value: datetime) -> str:
        """Serialize datetime to ISO format string.
        
        :param value: Datetime value to serialize
        :type value: datetime
        :returns: ISO format string
        :rtype: str
        """
        return value.isoformat()

