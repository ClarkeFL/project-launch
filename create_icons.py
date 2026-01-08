#!/usr/bin/env python3
"""
Generate application icons for Project Launcher.
Creates .ico (Windows) and .icns (macOS) files.
"""

from PIL import Image
from pathlib import Path
import os

# Path to the source icon image
SOURCE_ICON = Path(__file__).parent / "source_icon.png"


def create_icon_image(size=256):
    """Load and resize the Project Launcher icon image."""
    if not SOURCE_ICON.exists():
        raise FileNotFoundError(
            f"Source icon not found at {SOURCE_ICON}\n"
            "Please place your icon image as 'source_icon.png' in the project root."
        )
    
    # Load the source image
    image = Image.open(SOURCE_ICON)
    
    # Convert to RGBA if needed
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Resize with high-quality resampling
    if image.size != (size, size):
        image = image.resize((size, size), Image.Resampling.LANCZOS)
    
    return image


def create_ico(output_path):
    """Create Windows .ico file with multiple sizes."""
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        img = create_icon_image(size)
        images.append(img)
    
    # Save as ICO
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )
    print(f"[OK] Created {output_path}")


def create_icns(output_path):
    """Create macOS .icns file."""
    # For .icns we need specific sizes
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    # Create a temporary directory for iconset
    iconset_dir = Path(output_path).with_suffix('.iconset')
    iconset_dir.mkdir(exist_ok=True)
    
    for size in sizes:
        img = create_icon_image(size)
        
        # Standard resolution
        img.save(iconset_dir / f"icon_{size}x{size}.png")
        
        # Retina (@2x) - only for sizes up to 512
        if size <= 512:
            img_2x = create_icon_image(size * 2)
            img_2x.save(iconset_dir / f"icon_{size}x{size}@2x.png")
    
    print(f"[OK] Created iconset at {iconset_dir}")
    
    # On macOS, convert to .icns using iconutil
    if os.system("which iconutil > /dev/null 2>&1") == 0:
        os.system(f"iconutil -c icns {iconset_dir}")
        print(f"[OK] Created {output_path}")
        # Clean up iconset
        import shutil
        shutil.rmtree(iconset_dir)
    else:
        print(f"[INFO] iconutil not available (not on macOS)")
        print(f"[INFO] Iconset saved at {iconset_dir}")
        print(f"[INFO] Run 'iconutil -c icns {iconset_dir}' on macOS to create .icns")


def create_png(output_path, size=256):
    """Create a PNG icon (for Linux and general use)."""
    img = create_icon_image(size)
    img.save(output_path, format='PNG')
    print(f"[OK] Created {output_path}")


def main():
    print("Generating Project Launcher icons...\n")
    
    script_dir = Path(__file__).parent
    assets_dir = script_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Create all icon formats
    create_ico(assets_dir / "icon.ico")
    create_png(assets_dir / "icon.png", 256)
    create_png(assets_dir / "icon_512.png", 512)
    
    # Try to create .icns (only works fully on macOS)
    create_icns(assets_dir / "icon.icns")
    
    print(f"\nIcons saved to: {assets_dir}")


if __name__ == "__main__":
    main()
