"""Public routes for viewing root beers and reviews.

This module provides public-facing routes that don't require authentication.
All routes are accessible to anyone and display root beer and review data.
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from app.database import get_database
from app.routes.auth import get_admin_optional
from app.templates_helpers import templates
from app.utils.pagination import get_pagination_params, calculate_pagination_info, build_pagination_url
from bson import ObjectId
from typing import Optional
import logging

logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request) -> HTMLResponse:
    """Homepage listing all reviewed root beers.
    
    Displays a paginated list of root beers that have reviews, with
    filtering and sorting options. Only root beers with at least one
    review are shown.
    
    :param request: FastAPI request object
    :type request: Request
    :returns: HTML response with homepage
    :rtype: HTMLResponse
    """
    db = get_database()
    
    # Get pagination parameters
    pagination = get_pagination_params(request, default_per_page=20)
    
    # Get filter/sort parameters
    brand_filter = request.query_params.get("brand")
    region_filter = request.query_params.get("region")
    sort_by = request.query_params.get("sort", "name")  # name, brand, score
    sort_order = request.query_params.get("order", "asc")  # asc, desc
    
    # Get all root beers once for filter dropdowns (independent filters - show all options)
    all_rootbeers_for_filters = await db.rootbeers.find().to_list(1000)
    brands = sorted(set(rb.get("brand", "") for rb in all_rootbeers_for_filters if rb.get("brand")))
    regions = sorted(set(
        rb.get("region", "") or rb.get("country", "")
        for rb in all_rootbeers_for_filters
        if rb.get("region") or rb.get("country")
    ))
    
    # Build query for filtered results
    query = {}
    if brand_filter:
        query["brand"] = {"$regex": brand_filter, "$options": "i"}
    if region_filter:
        query["$or"] = [
            {"region": {"$regex": region_filter, "$options": "i"}},
            {"country": {"$regex": region_filter, "$options": "i"}},
        ]
    
    # Get filtered root beers matching query (for counting and processing)
    all_rootbeers = await db.rootbeers.find(query).to_list(1000)
    
    # Get review data for each root beer
    for rb in all_rootbeers:
        rootbeer_id_obj = rb["_id"]  # Keep original ObjectId
        rootbeer_id_str = str(rootbeer_id_obj)
        rb["_id"] = rootbeer_id_str
        # Query for reviews - root_beer_id is stored as string in reviews
        # Use $or to handle both string and ObjectId formats (some reviews might have been created with ObjectId)
        reviews = await db.reviews.find({
            "$or": [
                {"root_beer_id": rootbeer_id_str},
                {"root_beer_id": rootbeer_id_obj}
            ]
        }).to_list(100)
        
        if reviews:
            # Calculate average scores
            total_score = sum(r.get("overall_score", 0) for r in reviews)
            rb["average_score"] = round(total_score / len(reviews), 1)
            rb["review_count"] = len(reviews)
            rb["latest_review_date"] = max(r.get("review_date", r.get("created_at")) for r in reviews)
        else:
            rb["average_score"] = None
            rb["review_count"] = 0
            rb["latest_review_date"] = None
    
    # Filter out root beers without reviews
    rootbeers_with_reviews = [rb for rb in all_rootbeers if rb["review_count"] > 0]
    
    # Sort
    reverse_order = sort_order == "desc"
    if sort_by == "name":
        rootbeers_with_reviews.sort(key=lambda x: x.get("name", "").lower(), reverse=reverse_order)
    elif sort_by == "brand":
        rootbeers_with_reviews.sort(key=lambda x: x.get("brand", "").lower(), reverse=reverse_order)
    elif sort_by == "score":
        rootbeers_with_reviews.sort(key=lambda x: x.get("average_score") or 0, reverse=reverse_order)
    
    # Calculate pagination
    total_items = len(rootbeers_with_reviews)
    pagination_info = calculate_pagination_info(total_items, pagination["page"], pagination["per_page"])
    
    # Apply pagination (slice the sorted list)
    start_idx = pagination["skip"]
    end_idx = start_idx + pagination["limit"]
    rootbeers = rootbeers_with_reviews[start_idx:end_idx]
    
    # Build query params for pagination URLs
    query_params = {
        "brand": brand_filter or "",
        "region": region_filter or "",
        "sort": sort_by,
        "order": sort_order,
        "per_page": pagination["per_page"],
    }
    
    # Check if user is logged in as admin
    admin = get_admin_optional(request)
    
    return templates.TemplateResponse(
        request,
        "public/home.html",
        {
            "rootbeers": rootbeers,
            "brands": brands,
            "regions": regions,
            "current_brand": brand_filter,
            "current_region": region_filter,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "admin": admin,
            "pagination": pagination_info,
            "query_params": query_params,
            "build_pagination_url": build_pagination_url,
        }
    )


@router.get("/rootbeers/{rootbeer_id}", response_class=HTMLResponse)
async def view_rootbeer_public(rootbeer_id: str, request: Request):
    """Public view of a root beer with all reviews."""
    db = get_database()
    rootbeer = await db.rootbeers.find_one({"_id": ObjectId(rootbeer_id)})
    if not rootbeer:
        raise HTTPException(status_code=404, detail="Root beer not found")
    
    rootbeer["_id"] = str(rootbeer["_id"])
    
    # Ensure images field exists and is a list (default to empty list if not present or None)
    if "images" not in rootbeer or rootbeer.get("images") is None:
        rootbeer["images"] = []
    elif not isinstance(rootbeer.get("images"), list):
        rootbeer["images"] = []
    
    # Ensure primary_image is set if images exist but primary_image is not set
    if rootbeer.get("images") and len(rootbeer["images"]) > 0 and not rootbeer.get("primary_image"):
        rootbeer["primary_image"] = rootbeer["images"][0]
    
    # Get all reviews
    reviews = await db.reviews.find({"root_beer_id": rootbeer_id}).sort("review_date", -1).to_list(100)
    
    # Enrich reviews with flavor notes
    for review in reviews:
        review["_id"] = str(review["_id"])
        flavor_note_ids = review.get("flavor_notes", [])
        flavor_notes = []
        for fn_id in flavor_note_ids:
            fn = await db.flavor_notes.find_one({"_id": ObjectId(fn_id)})
            if fn:
                fn["_id"] = str(fn["_id"])
                flavor_notes.append(fn)
        review["flavor_notes_objects"] = flavor_notes
    
    # Calculate average scores
    if reviews:
        avg_scores = {
            "sweetness": sum(r.get("sweetness", 0) for r in reviews) / len(reviews),
            "carbonation_bite": sum(r.get("carbonation_bite", 0) for r in reviews) / len(reviews),
            "creaminess": sum(r.get("creaminess", 0) for r in reviews) / len(reviews),
            "acidity": sum(r.get("acidity", 0) for r in reviews) / len(reviews),
            "aftertaste_length": sum(r.get("aftertaste_length", 0) for r in reviews) / len(reviews),
            "overall_score": sum(r.get("overall_score", 0) for r in reviews) / len(reviews),
        }
    else:
        avg_scores = None
    
    # Check if user is logged in as admin
    admin = get_admin_optional(request)
    
    return templates.TemplateResponse(
        request,
        "public/rootbeer.html",
        {
            "rootbeer": rootbeer,
            "reviews": reviews,
            "avg_scores": avg_scores,
            "admin": admin,
        }
    )


@router.get("/reviews/{review_id}", response_class=HTMLResponse)
async def view_review_public(review_id: str, request: Request) -> HTMLResponse:
    """Public view of a single review.
    
    :param review_id: Review ID
    :type review_id: str
    :param request: FastAPI request object
    :type request: Request
    :returns: HTML response with review details
    :rtype: HTMLResponse
    :raises HTTPException: If review not found
    """
    db = get_database()
    review = await db.reviews.find_one({"_id": ObjectId(review_id)})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    review["_id"] = str(review["_id"])
    
    # Get root beer
    rootbeer = None
    if review.get("root_beer_id"):
        rootbeer = await db.rootbeers.find_one({"_id": ObjectId(review["root_beer_id"])})
        if rootbeer:
            rootbeer["_id"] = str(rootbeer["_id"])
    
    # Get flavor notes
    flavor_note_ids = review.get("flavor_notes", [])
    flavor_notes = []
    for fn_id in flavor_note_ids:
        fn = await db.flavor_notes.find_one({"_id": ObjectId(fn_id)})
        if fn:
            fn["_id"] = str(fn["_id"])
            flavor_notes.append(fn)
    
    # Check if user is logged in as admin
    admin = get_admin_optional(request)
    
    return templates.TemplateResponse(
        request,
        "public/review.html",
        {
            "review": review,
            "rootbeer": rootbeer,
            "flavor_notes": flavor_notes,
            "admin": admin,
        }
    )

