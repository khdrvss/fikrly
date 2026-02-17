"""Image optimization utilities for better performance."""

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InUploadedMemoryFile, InMemoryUploadedFile
import sys


def optimize_image(image_field, max_width=1200, max_height=1200, quality=85):
    """
    Optimize uploaded images by:
    - Resizing to max dimensions while maintaining aspect ratio
    - Converting to RGB if necessary
    - Compressing with specified quality
    - Converting to JPEG for smaller file sizes

    Args:
        image_field: Django ImageField
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        quality: JPEG quality (1-100)

    Returns:
        InMemoryUploadedFile or None
    """
    if not image_field:
        return None

    try:
        # Open image
        img = Image.open(image_field)

        # Convert RGBA to RGB if necessary
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Calculate new dimensions maintaining aspect ratio
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        # Save to BytesIO
        output = BytesIO()
        img.save(output, format="JPEG", quality=quality, optimize=True)
        output.seek(0)

        # Create InMemoryUploadedFile
        return InMemoryUploadedFile(
            output,
            "ImageField",
            f"{image_field.name.split('.')[0]}.jpg",
            "image/jpeg",
            sys.getsizeof(output),
            None,
        )
    except Exception as e:
        # Log error and return original
        print(f"Image optimization failed: {e}")
        return None


def create_thumbnail(image_field, size=(300, 300)):
    """
    Create a thumbnail version of an image.

    Args:
        image_field: Django ImageField
        size: Tuple of (width, height)

    Returns:
        InMemoryUploadedFile or None
    """
    if not image_field:
        return None

    try:
        img = Image.open(image_field)

        # Convert to RGB if needed
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Create thumbnail
        img.thumbnail(size, Image.Resampling.LANCZOS)

        # Save
        output = BytesIO()
        img.save(output, format="JPEG", quality=85, optimize=True)
        output.seek(0)

        return InMemoryUploadedFile(
            output,
            "ImageField",
            f"thumb_{image_field.name.split('.')[0]}.jpg",
            "image/jpeg",
            sys.getsizeof(output),
            None,
        )
    except Exception as e:
        print(f"Thumbnail creation failed: {e}")
        return None
