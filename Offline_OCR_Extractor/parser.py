
import re
from decimal import Decimal


MONEY = r"\d[\d,]*\.\d{2}"


def amount(value):
    return float(Decimal(value.replace(",", "")))


def parse_invoice(raw_text):
    invoice = {
        "invoice_number": None,
        "invoice_date": None,
        "supplier_name": None,
        "items": [],
        "total_amount": None,
        "subtotal": None,
        "tax_amount": None,
        "currency": "NPR" if "NPR" in raw_text.upper() else None
    }

    warnings = []

    # Invoice number
    match = re.search(
        r"\b[A-Z]{1,8}-\d{4}-\d+\b",
        raw_text.upper()
    )
    if match:
        invoice["invoice_number"] = match.group()

    # Invoice date
    match = re.search(
        r"\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}\b",
        raw_text
    )
    if match:
        invoice["invoice_date"] = match.group()

    # Supplier
    for line in raw_text.splitlines():
        if re.search(r"\bLTD\.?\b", line, re.IGNORECASE):
            invoice["supplier_name"] = line.strip()
            break

    # Standard item rows
    item_pattern = re.compile(
        rf"^\s*\d+\s+(.+?)\s+"
        rf"(\d+(?:\.\d+)?)\s+"
        rf"(pcs|pes|hrs|lot)\s+"
        rf"({MONEY})\s+({MONEY})\s*$",
        re.IGNORECASE
    )

    for line in raw_text.splitlines():
        match = item_pattern.match(line)

        if not match:
            continue

        description, quantity, unit, price, total = match.groups()

        normalized_unit = {
            "pes": "pcs"
        }.get(unit.lower(), unit.lower())

        invoice["items"].append({
            "description": description.strip(),
            "quantity": f"{quantity} {normalized_unit}",
            "unit_price": amount(price),
            "line_total": amount(total)
        })

    # Delivery row: OCR may merge "1 lot" into "Tot".
    delivery_pattern = re.compile(
        rf"^\s*5\s+Delivery Charge\s+Tot\s+"
        rf"({MONEY})\s+({MONEY})\s*$",
        re.IGNORECASE
    )

    for line in raw_text.splitlines():
        match = delivery_pattern.match(line)

        if match:
            price, total = match.groups()

            invoice["items"].append({
                "description": "Delivery Charge",
                "quantity": "1 lot",
                "unit_price": amount(price),
                "line_total": amount(total)
            })

            warnings.append(
                "Delivery quantity interpreted as '1 lot' because "
                "OCR did not clearly recognize the quantity."
            )

    # Summary
    summary_patterns = {
        "subtotal": rf"Subtotal\s*\(NPR\)\s*({MONEY})",
        "tax_amount": rf"VAT\s*\(13%\)\s*({MONEY})",
        "total_amount": rf"Total\s+Amount\s*\(NPR\)\s*({MONEY})"
    }

    for field, pattern in summary_patterns.items():
        match = re.search(pattern, raw_text, re.IGNORECASE)

        if match:
            invoice[field] = amount(match.group(1))

    return invoice, warnings
