from decimal import Decimal, InvalidOperation


def convert_decimal(value, field_name):

    if value is None:
        return None

    try:
        return Decimal(str(value))

    except (InvalidOperation, ValueError):
        raise ValueError(
            f"Invalid monetary value: {field_name}"
        )


def validate_invoice(invoice):

    errors = []
    warnings = []

    required_fields = [
        "invoice_number",
        "invoice_date",
        "supplier_name",
        "items",
        "total_amount"
    ]

    # Check required fields
    for field in required_fields:

        if invoice.get(field) in (None, "", []):

            errors.append(
                f"Missing required field: {field}"
            )

    items = invoice.get("items") or []

    calculated_subtotal = Decimal("0.00")

    all_line_totals_present = bool(items)

    # Validate individual items
    for index, item in enumerate(items, start=1):

        if not item.get("description"):

            errors.append(
                f"Item {index}: Missing description"
            )

        if not item.get("quantity"):

            errors.append(
                f"Item {index}: Missing quantity"
            )

        unit_price = convert_decimal(
            item.get("unit_price"),
            f"Item {index} unit price"
        )

        line_total = convert_decimal(
            item.get("line_total"),
            f"Item {index} line total"
        )

        if unit_price is None:

            warnings.append(
                f"Item {index}: Unit price missing"
            )

        if line_total is None:

            all_line_totals_present = False

        else:

            calculated_subtotal += line_total

    subtotal = convert_decimal(
        invoice.get("subtotal"),
        "subtotal"
    )

    tax_amount = convert_decimal(
        invoice.get("tax_amount"),
        "tax amount"
    )

    total_amount = convert_decimal(
        invoice.get("total_amount"),
        "total amount"
    )

    # Compare item totals with invoice subtotal
    if all_line_totals_present and subtotal is not None:

        if calculated_subtotal != subtotal:

            errors.append(
                f"Item totals ({calculated_subtotal}) "
                f"do not match subtotal ({subtotal})."
            )

    else:

        warnings.append(
            "Cannot verify subtotal because information is missing."
        )

    # Verify grand total
    if (
        subtotal is not None
        and tax_amount is not None
        and total_amount is not None
    ):

        expected_total = subtotal + tax_amount

        if expected_total != total_amount:

            errors.append(
                f"Expected total {expected_total}, "
                f"but invoice shows {total_amount}."
            )

    else:

        warnings.append(
            "Cannot verify grand total because information is missing."
        )

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "calculated_item_sum": str(
            calculated_subtotal.quantize(Decimal("0.01"))
        )
    }