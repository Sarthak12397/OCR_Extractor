
from pathlib import Path

from PIL import Image, ImageOps

from config import SUPPORTED_FORMATS


def load_image(image_path):
    image_path = Path(image_path)

    if not image_path.is_absolute():
        image_path = Path(__file__).resolve().parent / image_path

    if not image_path.exists():
        raise FileNotFoundError(
            f"Invoice image not found: {image_path}"
        )

    if image_path.suffix.lower() not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported image format: {image_path.suffix}"
        )

    try:
        with Image.open(image_path) as source:
            image = ImageOps.exif_transpose(source)
            image.load()

            if image.width < 100 or image.height < 100:
                raise ValueError("Image resolution is too small.")

            return image.convert("RGB")

    except Exception as error:
        raise ValueError(
            f"Unable to process invoice image: {error}"
        ) from error
