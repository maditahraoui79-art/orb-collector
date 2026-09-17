from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract

# Default region from the 960x1536 screenshot used during testing.
# Format: left, top, right, bottom.
DEFAULT_REGION = (175, 45, 280, 105)


def crop_orb_region(image: Image.Image, region=DEFAULT_REGION) -> Image.Image:
    """Crop the part of the screenshot containing the Orb counter."""
    return image.crop(region)


def prepare_for_ocr(image: Image.Image) -> Image.Image:
    """Prepare a small counter image for Tesseract using Pillow only."""
    image = image.convert("L")
    image = ImageOps.autocontrast(image)
    image = image.resize((image.width * 4, image.height * 4))
    image = image.filter(ImageFilter.SHARPEN)
    image = ImageEnhance.Contrast(image).enhance(2.0)
    return image


def read_orbs(image: Image.Image) -> int | None:
    """Return the first integer detected in the Orb counter, or None."""
    prepared = prepare_for_ocr(image)
    text = pytesseract.image_to_string(
        prepared,
        config="--psm 7 -c tessedit_char_whitelist=0123456789",
    )
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None


def read_from_file(path: str | Path, region=DEFAULT_REGION) -> int | None:
    """Read the Orb counter from a screenshot file."""
    image = Image.open(path)
    return read_orbs(crop_orb_region(image, region))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Read an Orb counter from a screenshot")
    parser.add_argument("image", help="Path to screenshot")
    args = parser.parse_args()

    result = read_from_file(args.image)
    print(f"Orbs: {result if result is not None else 'not detected'}")
