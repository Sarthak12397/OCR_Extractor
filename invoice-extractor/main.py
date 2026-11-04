import argparse
import json
import logging

from extractor import extract_invoice
from image_processor import load_invoice_image
from validator import validate_invoice
from config import OUTPUT_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="AI-Powered Invoice Data Extraction"
    )

    parser.add_argument(
        "image",
        help="Path to invoice image"
    )

    args = parser.parse_args()

    try:
        # Load invoice image
        image = load_invoice_image(args.image)

        # Extract invoice information using AI
        invoice_data = extract_invoice(image)

        # Validate extracted information
        validation = validate_invoice(invoice_data)

        # Combine extraction and validation results
        result = {
            "invoice": invoice_data,
            "validation": validation
        }

        # Create output directory if missing
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Save JSON output
        output_path = OUTPUT_DIR / "extracted_invoice.json"

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(
                result,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(json.dumps(result, indent=4, ensure_ascii=False))

        print(f"\nJSON saved to: {output_path}")

        if not validation["is_valid"]:
            logger.warning("Invoice requires manual review.")
            raise SystemExit(2)

    except (FileNotFoundError, ValueError, RuntimeError) as error:
        logger.error("Application error: %s", error)
        raise SystemExit(1)


if __name__ == "__main__":
    main()