import base64
from pathlib import Path


def encode_image_to_base64(file_bytes: bytes) -> str:
    """Encode image bytes to base64 string for Claude Vision API."""
    return base64.standard_b64encode(file_bytes).decode("utf-8")


def get_media_type(filename: str) -> str:
    """Return the MIME type for an image file."""
    ext = Path(filename).suffix.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }.get(ext, "image/jpeg")
