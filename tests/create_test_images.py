#!/usr/bin/env python3
"""Create test PNG images for testing the upload functionality."""

from PIL import Image, ImageDraw, ImageFont
import os

# Create test-images directory
os.makedirs("tests/test-images", exist_ok=True)

# Create test images
colors = [
    ("red", (255, 0, 0)),
    ("green", (0, 255, 0)),
    ("blue", (0, 0, 255)),
    ("yellow", (255, 255, 0)),
    ("purple", (128, 0, 128))
]

for i, (color_name, color_rgb) in enumerate(colors, 1):
    # Create a new image
    img = Image.new('RGB', (800, 600), color=color_rgb)
    
    # Add text
    draw = ImageDraw.Draw(img)
    text = f"Test Image {i}\n{color_name.upper()}"
    
    # Try to use a font, fall back to default if not available
    try:
        font_size = 60
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        font = None
    
    # Get text bounding box
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
    else:
        bbox = draw.textbbox((0, 0), text)
    
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (800 - text_width) // 2
    y = (600 - text_height) // 2
    
    # Draw white text
    draw.text((x, y), text, fill="white", font=font)
    
    # Save the image
    filename = f"tests/test-images/test{i}.png"
    img.save(filename)
    print(f"Created {filename}")

print("\nTest images created successfully!")