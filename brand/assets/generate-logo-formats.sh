#!/bin/bash

# Logo Format Generation Script
# This script documents the required logo formats and provides commands
# to generate them using ImageMagick (convert) or similar tools

echo "image2model Logo Format Generation"
echo "=================================="
echo ""
echo "This script requires ImageMagick to be installed."
echo "Install with: brew install imagemagick (macOS) or apt-get install imagemagick (Linux)"
echo ""

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo "ERROR: ImageMagick is not installed. Please install it first."
    exit 1
fi

# Create output directory
mkdir -p various-formats

# Generate PNG formats at different sizes
echo "Generating PNG formats..."
convert logo-original.png -resize 16x16 various-formats/logo-16.png
convert logo-original.png -resize 32x32 various-formats/logo-32.png
convert logo-original.png -resize 48x48 various-formats/logo-48.png
convert logo-original.png -resize 64x64 various-formats/logo-64.png
convert logo-original.png -resize 128x128 various-formats/logo-128.png
convert logo-original.png -resize 192x192 various-formats/logo-192.png
convert logo-original.png -resize 256x256 various-formats/logo-256.png
convert logo-original.png -resize 512x512 various-formats/logo-512.png
convert logo-original.png -resize 1024x1024 various-formats/logo-1024.png

# Generate favicon
echo "Generating favicon..."
convert logo-original.png -resize 16x16 -colors 256 various-formats/favicon.ico

# Generate Apple Touch Icon
echo "Generating Apple Touch Icon..."
convert logo-original.png -resize 180x180 various-formats/apple-touch-icon.png

# Generate Android adaptive icon layers
echo "Generating Android adaptive icon..."
convert logo-original.png -resize 108x108 -gravity center -extent 108x108 various-formats/android-icon-foreground.png
convert -size 108x108 xc:'#3A424A' various-formats/android-icon-background.png

# Generate monochrome versions
echo "Generating monochrome versions..."
convert logo-original.png -colorspace Gray various-formats/logo-mono.png
convert logo-original.png -colorspace Gray -negate various-formats/logo-mono-inverted.png

# Generate social media formats
echo "Generating social media formats..."
convert logo-original.png -resize 400x400 -gravity center -extent 400x400 various-formats/logo-social-square.png
convert logo-original.png -resize 1200x630 -gravity center -extent 1200x630 -background '#ECF0F1' various-formats/logo-social-og.png
convert logo-original.png -resize 1500x500 -gravity center -extent 1500x500 -background '#3A424A' various-formats/logo-social-twitter-header.png

echo ""
echo "Logo generation complete!"
echo ""
echo "Generated formats:"
echo "- PNG: 16px to 1024px"
echo "- ICO: favicon.ico"
echo "- Apple Touch Icon: 180x180"
echo "- Android Adaptive Icon: 108x108"
echo "- Monochrome versions"
echo "- Social media formats"
echo ""
echo "For SVG format, please use a vector graphics editor to manually trace the logo."
echo "For Windows .ico with multiple sizes, use a specialized tool like icotool."