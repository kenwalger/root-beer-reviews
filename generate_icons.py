#!/usr/bin/env python3
"""
Simple script to generate placeholder PWA icons.
Creates basic colored square icons with a root beer emoji.

Usage:
    uv pip install Pillow
    uv run python generate_icons.py
    
Or if Pillow is installed in your system Python:
    python3 generate_icons.py
"""

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow is required. Install it with: uv pip install Pillow")
    print("Then run with: uv run python generate_icons.py")
    exit(1)

import os

# Icon sizes needed
SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# Colors from the app theme
BACKGROUND_COLOR = (92, 64, 51)  # #5C4033 (sassafras)
TEXT_COLOR = (255, 248, 220)  # #FFF8DC (vanilla)

def create_icon(size):
    """Create a simple icon with root beer emoji."""
    # Create image with background color
    img = Image.new('RGB', (size, size), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default if not available
    font_size = int(size * 0.6)
    font = ImageFont.load_default()  # Default fallback
    
    # Try to use a system font that supports emoji
    emoji_font_paths = [
        "/System/Library/Fonts/Apple Color Emoji.ttc",  # macOS
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",  # Linux
    ]
    
    for font_path in emoji_font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except (OSError, IOError):
            # Font file doesn't exist or can't be loaded, try next
            continue
    
    # Draw root beer emoji or text
    text = "🍺"
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill=TEXT_COLOR, font=font)
    
    return img

def main():
    """Generate all required icon sizes."""
    icons_dir = "app/static/icons"
    os.makedirs(icons_dir, exist_ok=True)
    
    print("Generating PWA icons...")
    for size in SIZES:
        icon = create_icon(size)
        filename = f"{icons_dir}/icon-{size}x{size}.png"
        icon.save(filename, "PNG")
        print(f"Created: {filename}")
    
    print(f"\n✅ Generated {len(SIZES)} icons in {icons_dir}/")
    print("Icons are ready for PWA installation!")

if __name__ == "__main__":
    main()

