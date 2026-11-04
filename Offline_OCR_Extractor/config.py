
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

TESSDATA_PATH = Path(r"D:\OCR_task\tessdata")

OCR_LANGUAGE = "eng"

SUPPORTED_FORMATS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tiff"
}
