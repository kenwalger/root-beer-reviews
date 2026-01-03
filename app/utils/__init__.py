"""Utility functions for form parsing and data conversion.

This module provides utilities for parsing form data and converting
types appropriately, as well as re-exporting pagination utilities.
"""
from typing import Any, Dict, Optional
from datetime import datetime

# Import pagination utilities
from app.utils.pagination import (
    get_pagination_params,
    calculate_pagination_info,
    build_pagination_url,
)

__all__ = [
    "parse_form_data",
    "get_pagination_params",
    "calculate_pagination_info",
    "build_pagination_url",
]


def parse_form_data(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse form data and convert types appropriately.
    
    Converts string form values to appropriate Python types:
    - Numeric fields (int/float)
    - Boolean fields
    - Date fields (datetime)
    - List fields (for checkboxes)
    
    :param form_data: Raw form data dictionary
    :type form_data: Dict[str, Any]
    :returns: Parsed form data with converted types
    :rtype: Dict[str, Any]
    """
    parsed = {}
    
    for key, value in form_data.items():
        if value is None or value == "":
            continue
            
        # Handle numeric fields
        if key in ["sweetness", "carbonation_bite", "creaminess", "acidity", "aftertaste_length",
                   "overall_score", "uniqueness_score", "sugar_grams_per_serving", "caffeine_mg",
                   "alcohol_content", "estimated_co2_volumes"]:
            try:
                parsed[key] = float(value) if "." in str(value) else int(value)
            except (ValueError, TypeError):
                continue
        
        # Handle boolean fields
        elif key == "would_drink_again":
            parsed[key] = True
        
        # Handle date fields
        elif key == "review_date":
            try:
                parsed[key] = datetime.fromisoformat(value)
            except (ValueError, TypeError):
                continue
        
        # Handle list fields (for checkboxes)
        elif key == "flavor_notes":
            if isinstance(value, list):
                parsed[key] = value
            elif value:
                parsed[key] = [value]
        
        # Handle string fields
        else:
            parsed[key] = value
    
    return parsed

