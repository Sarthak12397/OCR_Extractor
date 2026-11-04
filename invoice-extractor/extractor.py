
import json
import logging
import re
import time

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 4

RETRYABLE_STATUS_CODES = {
    429, 500, 502, 503, 504
}


INVOICE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "invoice_number": {
            "type": "STRING",
            "nullable": True
        },
        "invoice_date": {
            "type": "STRING",
            "nullable": True
        },
        "supplier_name": {
            "type": "STRING",
            "nullable": True
        },
        "items": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "description": {
                        "type": "STRING",
                        "nullable": True
                    },
                    "quantity": {
                        "type": "STRING",
                        "nullable": True
                    },
                    "unit_price": {
                        "type": "NUMBER",
                        "nullable": True
                    },
                    "line_total": {
                        "type": "NUMBER",
                        "nullable": True
                    }
                },
                "required": [
                    "description",
                    "quantity",
                    "unit_price",
                    "line_total"
                ]
            }
        },
        "total_amount": {
            "type": "NUMBER",
            "nullable": True
        },
        "subtotal": {
            "type": "NUMBER",
            "nullable": True
        },
        "tax_amount": {
            "type": "NUMBER",
            "nullable": True
        },
        "currency": {
            "type": "STRING",
            "nullable": True
        }
    },
    "required": [
        "invoice_number",
        "invoice_date",
        "supplier_name",
        "items",
        "total_amount",
        "subtotal",
        "tax_amount",
        "currency"
    ]
}


def get_status_code(error):
    """Extract HTTP status code from a Gemini API exception."""

    status = (
        getattr(error, "code", None)
        or getattr(error, "status_code", None)
    )

    try:
        if status is not None:
            return int(status)
    except (TypeError, ValueError):
        pass

    # Fallback for exceptions where the status
    # code is only available in the error message.
    match = re.search(
        r"\b(429|500|502|503|504)\b",
        str(error)
    )

    if match:
        return int(match.group(1))

    return None


def extract_invoice(image):

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Check your .env file."
        )

    if not GEMINI_MODEL:
        raise RuntimeError(
            "GEMINI_MODEL is missing from configuration."
        )

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    prompt = """
    Extract invoice information from the provided image.

    Extract:
    1. Invoice number
    2. Invoice date
    3. Supplier name
    4. Items:
       - Description
       - Quantity
       - Unit price
       - Line total
    5. Subtotal
    6. Tax amount
    7. Total amount
    8. Currency

    Instructions:
    - Only extract information visible in the invoice.
    - Never invent missing information.
    - Use null for missing values.
    - Preserve the original invoice date format.
    - Return monetary values as numbers.
    - Distinguish subtotal, tax and grand total.
    - Do not calculate missing invoice values.
    - Preserve quantity units such as pcs, hrs and lot.
    """

    for attempt in range(1, MAX_ATTEMPTS + 1):

        try:

            logger.info(
                "Starting Gemini extraction. Attempt %s/%s",
                attempt,
                MAX_ATTEMPTS
            )

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[
                    prompt,
                    image
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=INVOICE_SCHEMA,
                    temperature=0
                )
            )

            if not response.text:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            try:
                extracted_data = json.loads(response.text)

            except json.JSONDecodeError as error:
                raise ValueError(
                    "Gemini returned invalid JSON."
                ) from error

            if not isinstance(extracted_data, dict):
                raise ValueError(
                    "Gemini response must be a JSON object."
                )

            logger.info(
                "Invoice extraction completed successfully."
            )

            return extracted_data

        except Exception as error:

            status_code = get_status_code(error)

            should_retry = (
                status_code in RETRYABLE_STATUS_CODES
                and attempt < MAX_ATTEMPTS
            )

            if should_retry:

                wait_seconds = 2 ** attempt

                logger.warning(
                    "Gemini API returned HTTP %s. "
                    "Retrying in %s seconds. Attempt %s/%s.",
                    status_code,
                    wait_seconds,
                    attempt,
                    MAX_ATTEMPTS
                )

                time.sleep(wait_seconds)

                continue

            logger.exception(
                "Invoice extraction failed after attempt %s.",
                attempt
            )

            raise RuntimeError(
                f"Invoice extraction failed: {error}"
            ) from error

    raise RuntimeError(
        "Invoice extraction failed after all retry attempts."
    )
