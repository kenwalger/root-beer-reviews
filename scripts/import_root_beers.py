#!/usr/bin/env python3
"""Script to import root beers from JSON reference list.

This script reads from planning/root_beer_reference_list.json and allows
you to import root beers into your database. It will skip root beers that
already exist (by name).

Usage:
    uv run python scripts/import_root_beers.py
    uv run python scripts/import_root_beers.py --dry-run  # Preview without importing
    uv run python scripts/import_root_beers.py --file custom_list.json  # Use custom file
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, UTC
from typing import List, Dict, Any
import argparse

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import connect_to_mongo, close_mongo_connection, get_database
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def import_root_beers(
    json_file: Path,
    dry_run: bool = False,
    skip_existing: bool = True
) -> None:
    """Import root beers from JSON file.
    
    :param json_file: Path to JSON file with root beer data
    :type json_file: Path
    :param dry_run: If True, only print what would be imported without actually importing
    :type dry_run: bool
    :param skip_existing: If True, skip root beers that already exist (by name)
    :type skip_existing: bool
    :raises FileNotFoundError: If JSON file doesn't exist
    :raises json.JSONDecodeError: If JSON file is invalid
    """
    # Connect to database
    await connect_to_mongo()
    db = get_database()
    
    if db is None:
        print("ERROR: Could not connect to database")
        return
    
    # Load JSON file
    if not json_file.exists():
        print(f"ERROR: File not found: {json_file}")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    root_beers = data.get('root_beers', [])
    
    if not root_beers:
        print("No root beers found in JSON file")
        return
    
    print(f"Found {len(root_beers)} root beers in {json_file.name}")
    print(f"Mode: {'DRY RUN (no changes will be made)' if dry_run else 'IMPORT'}")
    print("-" * 60)
    
    now = datetime.now(UTC)
    imported = 0
    skipped = 0
    errors = 0
    
    for root_beer in root_beers:
        name = root_beer.get('name', '').strip()
        if not name:
            print(f"⚠️  Skipping entry with no name: {root_beer}")
            errors += 1
            continue
        
        brand = root_beer.get('brand', '').strip() or name
        region = root_beer.get('region', '').strip() or None
        country = root_beer.get('country', 'USA').strip()
        notes = root_beer.get('notes', '').strip() or None
        
        # Check if root beer already exists
        if skip_existing:
            existing = await db.rootbeers.find_one({"name": name})
            if existing:
                print(f"⏭️  Skipping (already exists): {name}")
                skipped += 1
                continue
        
        root_beer_dict = {
            "name": name,
            "brand": brand,
            "region": region,
            "country": country,
            "notes": notes,
            "images": [],
            "created_at": now,
            "updated_at": now,
            "created_by": "import_script",
            "updated_by": "import_script",
        }
        
        # Remove None values (but keep images)
        root_beer_dict = {k: v for k, v in root_beer_dict.items() if v is not None or k == "images"}
        
        if dry_run:
            print(f"📝 Would import: {name} ({brand})")
            imported += 1
        else:
            try:
                await db.rootbeers.insert_one(root_beer_dict)
                print(f"✅ Imported: {name} ({brand})")
                imported += 1
            except Exception as e:
                print(f"❌ Error importing {name}: {e}")
                errors += 1
    
    print("-" * 60)
    print(f"Summary:")
    print(f"  Imported: {imported}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")
    
    if dry_run:
        print("\n💡 Run without --dry-run to actually import these root beers")
    
    # Close database connection
    await close_mongo_connection()


def main():
    """Main entry point for the import script."""
    parser = argparse.ArgumentParser(
        description="Import root beers from JSON reference list"
    )
    parser.add_argument(
        '--file',
        type=Path,
        default=Path(__file__).parent.parent / 'planning' / 'root_beer_reference_list.json',
        help='Path to JSON file with root beer data (default: planning/root_beer_reference_list.json)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be imported without actually importing'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Import even if root beer already exists (creates duplicates)'
    )
    
    args = parser.parse_args()
    
    asyncio.run(import_root_beers(
        json_file=args.file,
        dry_run=args.dry_run,
        skip_existing=not args.force
    ))


if __name__ == '__main__':
    main()

