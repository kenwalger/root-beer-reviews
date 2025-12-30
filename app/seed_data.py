"""Seed default data from planning documents."""
from datetime import datetime
from app.database import get_database


async def seed_default_data():
    """Seed default flavor notes, colors, and serving contexts."""
    db = get_database()
    now = datetime.utcnow()
    
    # Default flavor notes from planning/initial_thoughts.md
    default_flavor_notes = [
        # Traditional
        {"name": "Sassafras", "category": "Traditional", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Sarsaparilla", "category": "Traditional", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Wintergreen", "category": "Traditional", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Licorice", "category": "Traditional", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Anise", "category": "Traditional", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Birch", "category": "Traditional", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        
        # Sweet & Creamy
        {"name": "Vanilla", "category": "Sweet & Creamy", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Caramel", "category": "Sweet & Creamy", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Molasses", "category": "Sweet & Creamy", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Honey", "category": "Sweet & Creamy", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Marshmallow", "category": "Sweet & Creamy", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        
        # Spice & Herbal
        {"name": "Clove", "category": "Spice & Herbal", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Cinnamon", "category": "Spice & Herbal", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Nutmeg", "category": "Spice & Herbal", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Allspice", "category": "Spice & Herbal", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Ginger", "category": "Spice & Herbal", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        
        # Other
        {"name": "Citrus peel", "category": "Other", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Medicinal", "category": "Other", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Earthy", "category": "Other", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Peppery", "category": "Other", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
    ]
    
    # Default colors (common root beer colors)
    default_colors = [
        {"name": "Amber", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Brown", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Dark Brown", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Black", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Mahogany", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
    ]
    
    # Default serving contexts
    default_serving_contexts = [
        {"name": "Bottle", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Can", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Tap", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Fountain", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"name": "Growler", "created_at": now, "updated_at": now, "created_by": "system", "updated_by": "system"},
    ]
    
    # Seed flavor notes (only if collection is empty)
    flavor_note_count = await db.flavor_notes.count_documents({})
    if flavor_note_count == 0:
        await db.flavor_notes.insert_many(default_flavor_notes)
        print(f"Seeded {len(default_flavor_notes)} flavor notes")
    
    # Seed colors (only if collection is empty)
    color_count = await db.colors.count_documents({})
    if color_count == 0:
        await db.colors.insert_many(default_colors)
        print(f"Seeded {len(default_colors)} colors")
    
    # Seed serving contexts (only if collection is empty)
    serving_context_count = await db.serving_contexts.count_documents({})
    if serving_context_count == 0:
        await db.serving_contexts.insert_many(default_serving_contexts)
        print(f"Seeded {len(default_serving_contexts)} serving contexts")

