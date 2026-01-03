"""Pagination utilities for list views."""
from typing import Dict, Any, Optional
from math import ceil


def get_pagination_params(request, default_per_page: int = 20) -> Dict[str, Any]:
    """
    Extract pagination parameters from request query params.
    
    Args:
        request: FastAPI Request object
        default_per_page: Default items per page
        
    Returns:
        Dictionary with page, per_page, skip, and limit values
    """
    try:
        page = int(request.query_params.get("page", 1))
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1
    
    # Allowed per-page values
    allowed_per_page = [10, 20, 50, 100]
    try:
        per_page = int(request.query_params.get("per_page", default_per_page))
        if per_page not in allowed_per_page:
            per_page = default_per_page
    except (ValueError, TypeError):
        per_page = default_per_page
    
    skip = (page - 1) * per_page
    limit = per_page
    
    return {
        "page": page,
        "per_page": per_page,
        "skip": skip,
        "limit": limit,
        "allowed_per_page": allowed_per_page,
    }


def calculate_pagination_info(total_items: int, page: int, per_page: int) -> Dict[str, Any]:
    """
    Calculate pagination information.
    
    Args:
        total_items: Total number of items
        page: Current page number
        per_page: Items per page
        
    Returns:
        Dictionary with pagination info (total_pages, has_prev, has_next, etc.)
    """
    total_pages = ceil(total_items / per_page) if total_items > 0 else 1
    if total_pages < 1:
        total_pages = 1
    
    # Ensure page is within valid range
    if page > total_pages:
        page = total_pages
    if page < 1:
        page = 1
    
    has_prev = page > 1
    has_next = page < total_pages
    
    # Calculate page range for display (show up to 5 page numbers)
    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)
    
    # Adjust if we're near the start or end
    if end_page - start_page < 4:
        if start_page == 1:
            end_page = min(total_pages, start_page + 4)
        elif end_page == total_pages:
            start_page = max(1, end_page - 4)
    
    page_range = list(range(start_page, end_page + 1))
    
    return {
        "total_items": total_items,
        "total_pages": total_pages,
        "page": page,
        "per_page": per_page,
        "has_prev": has_prev,
        "has_next": has_next,
        "prev_page": page - 1 if has_prev else None,
        "next_page": page + 1 if has_next else None,
        "page_range": page_range,
        "start_item": (page - 1) * per_page + 1 if total_items > 0 else 0,
        "end_item": min(page * per_page, total_items),
    }


def build_pagination_url(base_url: str, params: Dict[str, Any], page: Optional[int] = None, per_page: Optional[int] = None) -> str:
    """
    Build a URL with pagination parameters while preserving existing query params.
    
    Args:
        base_url: Base URL path
        params: Existing query parameters
        page: Page number (if None, uses existing page param)
        per_page: Items per page (if None, uses existing per_page param)
        
    Returns:
        URL string with query parameters
    """
    query_params = params.copy()
    
    if page is not None:
        query_params["page"] = page
    if per_page is not None:
        query_params["per_page"] = per_page
    
    # Build query string
    query_string = "&".join(f"{k}={v}" for k, v in query_params.items() if v is not None and v != "")
    
    if query_string:
        return f"{base_url}?{query_string}"
    return base_url

