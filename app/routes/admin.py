"""Admin routes for managing root beers, reviews, and metadata."""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from app.database import get_database
from app.models.rootbeer import RootBeerCreate, RootBeerUpdate
from app.models.review import ReviewCreate, ReviewUpdate
from app.models.flavor_note import FlavorNoteCreate
from app.routes.auth import require_admin
from app.templates_helpers import templates
from app.utils.images import upload_image, delete_image
from bson import ObjectId
from datetime import datetime
from typing import List, Optional


router = APIRouter()


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin: dict = Depends(require_admin)):
    """Admin dashboard."""
    db = get_database()
    
    # Get counts
    rootbeer_count = await db.rootbeers.count_documents({})
    review_count = await db.reviews.count_documents({})
    flavor_note_count = await db.flavor_notes.count_documents({})
    
    # Get recent reviews
    recent_reviews = await db.reviews.find().sort("created_at", -1).limit(5).to_list(5)
    for review in recent_reviews:
        review["_id"] = str(review["_id"])
        if review.get("root_beer_id"):
            rootbeer = await db.rootbeers.find_one({"_id": ObjectId(review["root_beer_id"])})
            if rootbeer:
                review["rootbeer_name"] = rootbeer.get("name", "Unknown")
    
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "admin": admin,
            "rootbeer_count": rootbeer_count,
            "review_count": review_count,
            "flavor_note_count": flavor_note_count,
            "recent_reviews": recent_reviews,
        }
    )


# Root Beer Management
@router.get("/admin/rootbeers", response_class=HTMLResponse)
async def list_rootbeers(request: Request, admin: dict = Depends(require_admin)):
    """List all root beers."""
    db = get_database()
    rootbeers = await db.rootbeers.find().sort("name", 1).to_list(1000)
    for rb in rootbeers:
        rb["_id"] = str(rb["_id"])
        # Count reviews
        rb["review_count"] = await db.reviews.count_documents({"root_beer_id": str(rb["_id"])})
    
    return templates.TemplateResponse(
        "admin/rootbeers/list.html",
        {"request": request, "admin": admin, "rootbeers": rootbeers}
    )


@router.get("/admin/rootbeers/new", response_class=HTMLResponse)
async def new_rootbeer_form(request: Request, admin: dict = Depends(require_admin)):
    """Show form to create a new root beer."""
    db = get_database()
    colors = await db.colors.find().sort("name", 1).to_list(100)
    for color in colors:
        color["_id"] = str(color["_id"])
    
    return templates.TemplateResponse(
        "admin/rootbeers/new.html",
        {"request": request, "admin": admin, "colors": colors}
    )


@router.post("/admin/rootbeers")
async def create_rootbeer(
    request: Request,
    admin: dict = Depends(require_admin),
    name: str = Form(...),
    brand: str = Form(...),
    region: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    ingredients: Optional[str] = Form(None),
    sweetener_type: Optional[str] = Form(None),
    sugar_grams_per_serving: Optional[float] = Form(None),
    caffeine_mg: Optional[float] = Form(None),
    alcohol_content: Optional[float] = Form(None),
    color: Optional[str] = Form(None),
    carbonation_level: Optional[str] = Form(None),
    estimated_co2_volumes: Optional[float] = Form(None),
    notes: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
):
    """Create a new root beer."""
    db = get_database()
    now = datetime.utcnow()
    
    rootbeer_dict = {
        "name": name,
        "brand": brand,
        "region": region,
        "country": country,
        "ingredients": ingredients,
        "sweetener_type": sweetener_type,
        "sugar_grams_per_serving": float(sugar_grams_per_serving) if sugar_grams_per_serving else None,
        "caffeine_mg": float(caffeine_mg) if caffeine_mg else None,
        "alcohol_content": float(alcohol_content) if alcohol_content else None,
        "color": color,
        "carbonation_level": carbonation_level,
        "estimated_co2_volumes": float(estimated_co2_volumes) if estimated_co2_volumes else None,
        "notes": notes,
        "images": [],  # Always initialize images as empty list
        "created_at": now,
        "updated_at": now,
        "created_by": admin["email"],
        "updated_by": admin["email"],
    }
    
    # Remove None values (but keep images even if empty)
    rootbeer_dict = {k: v for k, v in rootbeer_dict.items() if v is not None or k == "images"}
    
    result = await db.rootbeers.insert_one(rootbeer_dict)
    rootbeer_id = str(result.inserted_id)
    
    # Handle image uploads if provided
    if files:
        images = []
        primary_image = None
        for file in files:
            if file.filename:  # Only process files that were actually uploaded
                try:
                    image_url = await upload_image(file, rootbeer_id)
                    images.append(image_url)
                    if not primary_image:
                        primary_image = image_url
                except HTTPException:
                    # If upload fails, continue with other files
                    pass
        
        if images:
            await db.rootbeers.update_one(
                {"_id": result.inserted_id},
                {
                    "$set": {
                        "images": images,
                        "primary_image": primary_image,
                        "updated_at": now,
                        "updated_by": admin["email"],
                    }
                }
            )
    
    return RedirectResponse(url=f"/admin/rootbeers/{rootbeer_id}", status_code=303)


@router.get("/admin/rootbeers/{rootbeer_id}", response_class=HTMLResponse)
async def view_rootbeer(
    rootbeer_id: str,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """View a root beer."""
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
    
    # Get reviews
    reviews = await db.reviews.find({"root_beer_id": rootbeer_id}).to_list(100)
    for review in reviews:
        review["_id"] = str(review["_id"])
    
    colors = await db.colors.find().sort("name", 1).to_list(100)
    for color in colors:
        color["_id"] = str(color["_id"])
    
    return templates.TemplateResponse(
        "admin/rootbeers/view.html",
        {
            "request": request,
            "admin": admin,
            "rootbeer": rootbeer,
            "reviews": reviews,
            "colors": colors,
        }
    )


@router.post("/admin/rootbeers/{rootbeer_id}")
async def update_rootbeer(
    rootbeer_id: str,
    rootbeer: RootBeerUpdate,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Update a root beer."""
    db = get_database()
    update_data = rootbeer.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    update_data["updated_by"] = admin["email"]
    
    result = await db.rootbeers.update_one(
        {"_id": ObjectId(rootbeer_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Root beer not found")
    
    return RedirectResponse(url=f"/admin/rootbeers/{rootbeer_id}", status_code=303)


@router.post("/admin/rootbeers/{rootbeer_id}/delete")
async def delete_rootbeer(
    rootbeer_id: str,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Delete a root beer."""
    db = get_database()
    
    # Check if there are reviews
    review_count = await db.reviews.count_documents({"root_beer_id": rootbeer_id})
    if review_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete root beer with {review_count} review(s). Delete reviews first."
        )
    
    result = await db.rootbeers.delete_one({"_id": ObjectId(rootbeer_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Root beer not found")
    
    return RedirectResponse(url="/admin/rootbeers", status_code=303)


@router.post("/admin/rootbeers/{rootbeer_id}/images")
async def upload_rootbeer_image(
    rootbeer_id: str,
    file: UploadFile = File(...),
    admin: dict = Depends(require_admin)
):
    """Upload an image for a root beer."""
    db = get_database()
    
    # Verify root beer exists
    rootbeer = await db.rootbeers.find_one({"_id": ObjectId(rootbeer_id)})
    if not rootbeer:
        raise HTTPException(status_code=404, detail="Root beer not found")
    
    # Upload image
    image_url = await upload_image(file, rootbeer_id)
    
    # Update root beer with new image
    images = rootbeer.get("images") or []
    if not isinstance(images, list):
        images = []
    images.append(image_url)
    
    # Set as primary if it's the first image
    primary_image = rootbeer.get("primary_image") or image_url
    
    await db.rootbeers.update_one(
        {"_id": ObjectId(rootbeer_id)},
        {
            "$set": {
                "images": images,
                "primary_image": primary_image,
                "updated_at": datetime.utcnow(),
                "updated_by": admin["email"],
            }
        }
    )
    
    return RedirectResponse(url=f"/admin/rootbeers/{rootbeer_id}", status_code=303)


@router.post("/admin/rootbeers/{rootbeer_id}/images/delete")
async def delete_rootbeer_image(
    rootbeer_id: str,
    image_url: str = Form(...),
    admin: dict = Depends(require_admin)
):
    """Delete an image from a root beer."""
    db = get_database()
    
    rootbeer = await db.rootbeers.find_one({"_id": ObjectId(rootbeer_id)})
    if not rootbeer:
        raise HTTPException(status_code=404, detail="Root beer not found")
    
    images = rootbeer.get("images", [])
    if image_url not in images:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Delete from S3 (continue even if deletion fails to avoid orphaned DB references)
    s3_deleted = await delete_image(image_url)
    if not s3_deleted:
        # Log warning but continue with DB update
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to delete image from S3, but continuing with database update: {image_url}")
    
    # Remove from database
    images.remove(image_url)
    primary_image = rootbeer.get("primary_image")
    if primary_image == image_url:
        primary_image = images[0] if images else None
    
    await db.rootbeers.update_one(
        {"_id": ObjectId(rootbeer_id)},
        {
            "$set": {
                "images": images,
                "primary_image": primary_image,
                "updated_at": datetime.utcnow(),
                "updated_by": admin["email"],
            }
        }
    )
    
    return RedirectResponse(url=f"/admin/rootbeers/{rootbeer_id}", status_code=303)


@router.post("/admin/rootbeers/{rootbeer_id}/images/set-primary")
async def set_primary_image(
    rootbeer_id: str,
    image_url: str = Form(...),
    admin: dict = Depends(require_admin)
):
    """Set the primary/featured image for a root beer."""
    db = get_database()
    
    rootbeer = await db.rootbeers.find_one({"_id": ObjectId(rootbeer_id)})
    if not rootbeer:
        raise HTTPException(status_code=404, detail="Root beer not found")
    
    images = rootbeer.get("images", [])
    if image_url not in images:
        raise HTTPException(status_code=404, detail="Image not found")
    
    await db.rootbeers.update_one(
        {"_id": ObjectId(rootbeer_id)},
        {
            "$set": {
                "primary_image": image_url,
                "updated_at": datetime.utcnow(),
                "updated_by": admin["email"],
            }
        }
    )
    
    return RedirectResponse(url=f"/admin/rootbeers/{rootbeer_id}", status_code=303)


# Review Management
@router.get("/admin/reviews", response_class=HTMLResponse)
async def list_reviews(request: Request, admin: dict = Depends(require_admin)):
    """List all reviews."""
    db = get_database()
    reviews = await db.reviews.find().sort("review_date", -1).to_list(1000)
    
    # Get root beer names
    for review in reviews:
        review["_id"] = str(review["_id"])
        if review.get("root_beer_id"):
            rootbeer = await db.rootbeers.find_one({"_id": ObjectId(review["root_beer_id"])})
            if rootbeer:
                review["rootbeer_name"] = rootbeer.get("name", "Unknown")
    
    return templates.TemplateResponse(
        "admin/reviews/list.html",
        {"request": request, "admin": admin, "reviews": reviews}
    )


@router.get("/admin/reviews/new", response_class=HTMLResponse)
async def new_review_form(request: Request, admin: dict = Depends(require_admin)):
    """Show form to create a new review."""
    db = get_database()
    rootbeers = await db.rootbeers.find().sort("name", 1).to_list(1000)
    for rb in rootbeers:
        rb["_id"] = str(rb["_id"])
    
    flavor_notes = await db.flavor_notes.find().sort("name", 1).to_list(1000)
    for fn in flavor_notes:
        fn["_id"] = str(fn["_id"])
    
    serving_contexts = await db.serving_contexts.find().sort("name", 1).to_list(100)
    for sc in serving_contexts:
        sc["_id"] = str(sc["_id"])
    
    return templates.TemplateResponse(
        "admin/reviews/new.html",
        {
            "request": request,
            "admin": admin,
            "rootbeers": rootbeers,
            "flavor_notes": flavor_notes,
            "serving_contexts": serving_contexts,
        }
    )


@router.post("/admin/reviews")
async def create_review(
    request: Request,
    admin: dict = Depends(require_admin),
    root_beer_id: str = Form(...),
    review_date: str = Form(...),
    serving_context: Optional[str] = Form(None),
    sweetness: int = Form(...),
    carbonation_bite: int = Form(...),
    creaminess: int = Form(...),
    acidity: int = Form(...),
    aftertaste_length: int = Form(...),
    overall_score: int = Form(...),
    uniqueness_score: Optional[int] = Form(None),
    would_drink_again: bool = Form(False),
    tasting_notes: Optional[str] = Form(None),
    flavor_notes: List[str] = Form(default_factory=list),
):
    """Create a new review."""
    db = get_database()
    
    # Verify root beer exists
    rootbeer = await db.rootbeers.find_one({"_id": ObjectId(root_beer_id)})
    if not rootbeer:
        raise HTTPException(status_code=404, detail="Root beer not found")
    
    # Parse review date
    try:
        review_date_obj = datetime.fromisoformat(review_date)
    except (ValueError, TypeError):
        review_date_obj = datetime.utcnow()
    
    now = datetime.utcnow()
    review_dict = {
        "root_beer_id": root_beer_id,
        "review_date": review_date_obj,
        "serving_context": serving_context,
        "sweetness": int(sweetness),
        "carbonation_bite": int(carbonation_bite),
        "creaminess": int(creaminess),
        "acidity": int(acidity),
        "aftertaste_length": int(aftertaste_length),
        "overall_score": int(overall_score),
        "uniqueness_score": int(uniqueness_score) if uniqueness_score else None,
        "would_drink_again": bool(would_drink_again),
        "tasting_notes": tasting_notes,
        "flavor_notes": flavor_notes if isinstance(flavor_notes, list) else [flavor_notes] if flavor_notes else [],
        "created_at": now,
        "updated_at": now,
        "created_by": admin["email"],
        "updated_by": admin["email"],
    }
    
    # Remove None values
    review_dict = {k: v for k, v in review_dict.items() if v is not None or k in ["flavor_notes", "serving_context"]}
    
    result = await db.reviews.insert_one(review_dict)
    return RedirectResponse(url=f"/admin/reviews/{result.inserted_id}", status_code=303)


@router.get("/admin/reviews/{review_id}", response_class=HTMLResponse)
async def view_review(
    review_id: str,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """View a review."""
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
    
    rootbeers = await db.rootbeers.find().sort("name", 1).to_list(1000)
    for rb in rootbeers:
        rb["_id"] = str(rb["_id"])
    
    all_flavor_notes = await db.flavor_notes.find().sort("name", 1).to_list(1000)
    for fn in all_flavor_notes:
        fn["_id"] = str(fn["_id"])
    
    serving_contexts = await db.serving_contexts.find().sort("name", 1).to_list(100)
    for sc in serving_contexts:
        sc["_id"] = str(sc["_id"])
    
    return templates.TemplateResponse(
        "admin/reviews/view.html",
        {
            "request": request,
            "admin": admin,
            "review": review,
            "rootbeer": rootbeer,
            "flavor_notes": flavor_notes,
            "rootbeers": rootbeers,
            "all_flavor_notes": all_flavor_notes,
            "serving_contexts": serving_contexts,
        }
    )


@router.post("/admin/reviews/{review_id}")
async def update_review(
    review_id: str,
    request: Request,
    admin: dict = Depends(require_admin),
    root_beer_id: Optional[str] = Form(None),
    review_date: Optional[str] = Form(None),
    serving_context: Optional[str] = Form(None),
    sweetness: Optional[int] = Form(None),
    carbonation_bite: Optional[int] = Form(None),
    creaminess: Optional[int] = Form(None),
    acidity: Optional[int] = Form(None),
    aftertaste_length: Optional[int] = Form(None),
    overall_score: Optional[int] = Form(None),
    uniqueness_score: Optional[int] = Form(None),
    would_drink_again: Optional[bool] = Form(None),
    tasting_notes: Optional[str] = Form(None),
    flavor_notes: List[str] = Form(default_factory=list),
):
    """Update a review."""
    db = get_database()
    update_data = {}
    
    if root_beer_id is not None:
        update_data["root_beer_id"] = root_beer_id
    if review_date:
        try:
            update_data["review_date"] = datetime.fromisoformat(review_date)
        except (ValueError, TypeError):
            pass
    if serving_context is not None:
        update_data["serving_context"] = serving_context
    if sweetness is not None:
        update_data["sweetness"] = int(sweetness)
    if carbonation_bite is not None:
        update_data["carbonation_bite"] = int(carbonation_bite)
    if creaminess is not None:
        update_data["creaminess"] = int(creaminess)
    if acidity is not None:
        update_data["acidity"] = int(acidity)
    if aftertaste_length is not None:
        update_data["aftertaste_length"] = int(aftertaste_length)
    if overall_score is not None:
        update_data["overall_score"] = int(overall_score)
    if uniqueness_score is not None:
        update_data["uniqueness_score"] = int(uniqueness_score)
    if would_drink_again is not None:
        update_data["would_drink_again"] = bool(would_drink_again)
    if tasting_notes is not None:
        update_data["tasting_notes"] = tasting_notes
    if flavor_notes:
        update_data["flavor_notes"] = flavor_notes if isinstance(flavor_notes, list) else [flavor_notes]
    
    update_data["updated_at"] = datetime.utcnow()
    update_data["updated_by"] = admin["email"]
    
    result = await db.reviews.update_one(
        {"_id": ObjectId(review_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return RedirectResponse(url=f"/admin/reviews/{review_id}", status_code=303)


@router.post("/admin/reviews/{review_id}/delete")
async def delete_review(
    review_id: str,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Delete a review."""
    db = get_database()
    result = await db.reviews.delete_one({"_id": ObjectId(review_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return RedirectResponse(url="/admin/reviews", status_code=303)


# Flavor Note Management
@router.get("/admin/flavor-notes", response_class=HTMLResponse)
async def list_flavor_notes(request: Request, admin: dict = Depends(require_admin)):
    """List all flavor notes."""
    db = get_database()
    flavor_notes = await db.flavor_notes.find().sort("name", 1).to_list(1000)
    for fn in flavor_notes:
        fn["_id"] = str(fn["_id"])
    
    return templates.TemplateResponse(
        "admin/flavor-notes/list.html",
        {"request": request, "admin": admin, "flavor_notes": flavor_notes}
    )


@router.post("/admin/flavor-notes")
async def create_flavor_note(
    request: Request,
    admin: dict = Depends(require_admin),
    name: str = Form(...),
    category: Optional[str] = Form(None),
):
    """Create a new flavor note."""
    db = get_database()
    now = datetime.utcnow()
    
    fn_dict = {
        "name": name,
        "category": category,
        "created_at": now,
        "updated_at": now,
        "created_by": admin["email"],
        "updated_by": admin["email"],
    }
    
    # Remove None values
    fn_dict = {k: v for k, v in fn_dict.items() if v is not None}
    
    await db.flavor_notes.insert_one(fn_dict)
    return RedirectResponse(url="/admin/flavor-notes", status_code=303)


@router.post("/admin/flavor-notes/{flavor_note_id}/delete")
async def delete_flavor_note(
    flavor_note_id: str,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Delete a flavor note."""
    db = get_database()
    result = await db.flavor_notes.delete_one({"_id": ObjectId(flavor_note_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Flavor note not found")
    
    return RedirectResponse(url="/admin/flavor-notes", status_code=303)


# Metadata Management (Colors, Serving Contexts)
@router.get("/admin/metadata", response_class=HTMLResponse)
async def metadata_management(request: Request, admin: dict = Depends(require_admin)):
    """Manage metadata (colors, serving contexts)."""
    db = get_database()
    colors = await db.colors.find().sort("name", 1).to_list(100)
    for color in colors:
        color["_id"] = str(color["_id"])
    
    serving_contexts = await db.serving_contexts.find().sort("name", 1).to_list(100)
    for sc in serving_contexts:
        sc["_id"] = str(sc["_id"])
    
    return templates.TemplateResponse(
        "admin/metadata.html",
        {
            "request": request,
            "admin": admin,
            "colors": colors,
            "serving_contexts": serving_contexts,
        }
    )


@router.post("/admin/metadata/colors")
async def create_color(
    name: str,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Create a new color option."""
    db = get_database()
    now = datetime.utcnow()
    
    color_dict = {
        "name": name,
        "created_at": now,
        "updated_at": now,
        "created_by": admin["email"],
        "updated_by": admin["email"],
    }
    
    await db.colors.insert_one(color_dict)
    return RedirectResponse(url="/admin/metadata", status_code=303)


@router.post("/admin/metadata/colors/{color_id}/delete")
async def delete_color(
    color_id: str,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Delete a color option."""
    db = get_database()
    result = await db.colors.delete_one({"_id": ObjectId(color_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Color not found")
    
    return RedirectResponse(url="/admin/metadata", status_code=303)


@router.post("/admin/metadata/serving-contexts")
async def create_serving_context(
    name: str,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Create a new serving context option."""
    db = get_database()
    now = datetime.utcnow()
    
    sc_dict = {
        "name": name,
        "created_at": now,
        "updated_at": now,
        "created_by": admin["email"],
        "updated_by": admin["email"],
    }
    
    await db.serving_contexts.insert_one(sc_dict)
    return RedirectResponse(url="/admin/metadata", status_code=303)


@router.post("/admin/metadata/serving-contexts/{sc_id}/delete")
async def delete_serving_context(
    sc_id: str,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Delete a serving context option."""
    db = get_database()
    result = await db.serving_contexts.delete_one({"_id": ObjectId(sc_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Serving context not found")
    
    return RedirectResponse(url="/admin/metadata", status_code=303)


# Admin Account Management
@router.get("/admin/account", response_class=HTMLResponse)
async def admin_account(request: Request, admin: dict = Depends(require_admin)):
    """Admin account settings page."""
    db = get_database()
    user = await db.admin_users.find_one({"email": admin["email"]})
    if user:
        user["_id"] = str(user["_id"])
    
    return templates.TemplateResponse(
        "admin/account.html",
        {
            "request": request,
            "admin": admin,
            "user": user,
        }
    )


@router.post("/admin/account/change-password")
async def change_password(
    request: Request,
    admin: dict = Depends(require_admin),
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
):
    """Change admin password."""
    from app.auth import verify_password, get_password_hash, get_admin_user_by_email
    
    # Verify current password
    user = await get_admin_user_by_email(admin["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_password(current_password, user.hashed_password):
        db = get_database()
        user_doc = await db.admin_users.find_one({"email": admin["email"]})
        if user_doc:
            user_doc["_id"] = str(user_doc["_id"])
        return templates.TemplateResponse(
            "admin/account.html",
            {
                "request": request,
                "admin": admin,
                "user": user_doc,
                "error": "Current password is incorrect",
            },
            status_code=400
        )
    
    # Validate new password
    if new_password != confirm_password:
        db = get_database()
        user_doc = await db.admin_users.find_one({"email": admin["email"]})
        if user_doc:
            user_doc["_id"] = str(user_doc["_id"])
        return templates.TemplateResponse(
            "admin/account.html",
            {
                "request": request,
                "admin": admin,
                "user": user_doc,
                "error": "New passwords do not match",
            },
            status_code=400
        )
    
    if len(new_password) < 8:
        db = get_database()
        user_doc = await db.admin_users.find_one({"email": admin["email"]})
        if user_doc:
            user_doc["_id"] = str(user_doc["_id"])
        return templates.TemplateResponse(
            "admin/account.html",
            {
                "request": request,
                "admin": admin,
                "user": user_doc,
                "error": "Password must be at least 8 characters long",
            },
            status_code=400
        )
    
    # Update password
    db = get_database()
    hashed_password = get_password_hash(new_password)
    await db.admin_users.update_one(
        {"email": admin["email"]},
        {
            "$set": {
                "hashed_password": hashed_password,
                "updated_at": datetime.utcnow(),
                "updated_by": admin["email"],
            }
        }
    )
    
    return RedirectResponse(url="/admin/account?success=Password updated successfully", status_code=303)

