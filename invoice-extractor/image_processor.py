from pathlib import Path
from PIL import Image, ImageOps


SUPPORTED_FORMATS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp"
}


def load_invoice_image(image_path):

    path = Path(image_path)

    if not path.is_file():

        raise FileNotFoundError(
            f"Invoice image not found: {path}"
        )

    if path.suffix.lower() not in SUPPORTED_FORMATS:

        raise ValueError(
            "Unsupported image format."
        )

    try:

        with Image.open(path) as image:

            image = ImageOps.exif_transpose(image)

            image = image.convert("RGB")

            image.load()

            return image

    except Exception as error:

        raise ValueError(
            f"Unable to process invoice image: {error}"
        ) from error