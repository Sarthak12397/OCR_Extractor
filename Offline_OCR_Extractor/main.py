
import argparse
import json
import logging
import sys

from config import INPUT_DIR, OUTPUT_DIR
from image_processor import load_image
from extractor import extract_invoice
from parser import parse_invoice
from validator import validate_invoice


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Offline Invoice Extractor"
    )

    parser.add_argument(
        "image",
        nargs="?",
        default=str(INPUT_DIR / "invoice_sample.png")
    )

    args = parser.parse_args()

    try:
        image = load_image(args.image)

        raw_text = extract_invoice(image)

        invoice, parser_warnings = parse_invoice(raw_text)

        validation = validate_invoice(
            invoice,
            parser_warnings
        )

        result = {
            "invoice": invoice,
            "validation": validation
        }

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        output_path = OUTPUT_DIR / "extracted_invoice.json"

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(
                result,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(json.dumps(result, indent=4, ensure_ascii=False))

        print(f"\nJSON saved to: {output_path}")

        if not validation["is_valid"]:
            print("\nValidation failed.")
            return 2

        print("\nValidation passed.")
        return 0

    except Exception as error:
        logger.exception("Invoice processing failed.")
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
