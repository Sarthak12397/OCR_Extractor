
from decimal import Decimal, InvalidOperation


def validate_invoice(invoice, parser_warnings=None):
    errors = []
    warnings = list(parser_warnings or [])

    required_fields = [
        "invoice_number",
        "invoice_date",
        "supplier_name",
        "items",
        "subtotal",
        "tax_amount",
        "total_amount",
        "currency"
    ]

    for field in required_fields:
        if invoice.get(field) in (None, "", []):
            errors.append(f"Missing required field: {field}")

    calculated_sum = Decimal("0")

    for index, item in enumerate(invoice.get("items", []), start=1):
        try:
            quantity_text = str(item["quantity"])
            quantity_match = quantity_text.split()[0]

            quantity = Decimal(quantity_match)
            unit_price = Decimal(str(item["unit_price"]))
            line_total = Decimal(str(item["line_total"]))

            expected_total = (quantity * unit_price).quantize(
                Decimal("0.01")
            )

            if expected_total != line_total.quantize(Decimal("0.01")):
                errors.append(
                    f"Item {index}: quantity multiplied by unit price "
                    "does not match line total."
                )

            calculated_sum += line_total

        except (KeyError, InvalidOperation, ValueError, TypeError):
            errors.append(f"Item {index}: invalid item values.")

    calculated_sum = calculated_sum.quantize(Decimal("0.01"))

    if invoice.get("subtotal") is not None:
        subtotal = Decimal(str(invoice["subtotal"]))

        if calculated_sum != subtotal:
            errors.append(
                "Calculated item sum does not match invoice subtotal."
            )

    if all(
        invoice.get(field) is not None
        for field in ("subtotal", "tax_amount", "total_amount")
    ):
        subtotal = Decimal(str(invoice["subtotal"]))
        tax = Decimal(str(invoice["tax_amount"]))
        total = Decimal(str(invoice["total_amount"]))

        if subtotal + tax != total:
            errors.append(
                "Subtotal plus tax does not match total amount."
            )

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "calculated_item_sum": f"{calculated_sum:.2f}"
    }
