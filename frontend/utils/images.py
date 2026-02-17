from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


def generate_webp_versions(image_field, sizes=(400, 800, 1200), quality=85):
    """Generate WEBP binary blobs for given PIL-image-like `image_field`.

    Returns dict mapping size -> ContentFile
    """
    try:
        img = Image.open(image_field)
    except Exception:
        return {}

    img = img.convert("RGB")
    files = {}

    for size in sizes:
        img_copy = img.copy()
        # Maintain a 2:1-ish aspect by constraining width and letting thumbnail maintain aspect
        img_copy.thumbnail((size, int(size * 0.75)))
        buffer = BytesIO()
        img_copy.save(buffer, format="WEBP", quality=quality)
        files[size] = ContentFile(buffer.getvalue())

    return files
