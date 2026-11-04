# Invoice Extraction System

An invoice extraction application that converts invoice images into structured JSON. This repository contains two independent implementations: an AI-powered approach using Google Gemini and an offline OCR approach using Tesseract.

## Project Overview

The project explores two approaches to extracting structured information from invoices:

| Implementation | Technology | Processing |
|---|---|---|
| Gemini Invoice Extractor | Python, Google Gemini API | Cloud-based AI extraction |
| Offline OCR Extractor | Python, Tesseract OCR | Local OCR and rule-based parsing |

Both implementations aim to extract invoice information, produce structured JSON, and validate financial calculations.

## Implementations

### 1. Gemini Invoice Extractor

Uses Google's Gemini API to interpret invoice content and extract structured information.

**Key capabilities**
- Extract invoice number, date, and supplier information.
- Identify invoice line items, quantities, and unit prices.
- Extract subtotal, tax, and total amount.
- Produce structured JSON output.
- Validate extracted financial values.
- Handle extraction errors and missing information.

**Processing flow**

1. Load the invoice image.
2. Submit the image for AI-based extraction.
3. Receive structured invoice data.
4. Validate extracted information.
5. Generate JSON output.

### 2. Offline OCR Extractor

Uses Tesseract OCR to process invoice images locally without sending invoice data to an external AI service.

**Key capabilities**
- Local image processing.
- Text extraction using Tesseract OCR.
- Rule-based parsing of invoice information.
- Financial calculation validation.
- Structured JSON output.
- Error handling for unreadable or unsupported images.

**Processing flow**

1. Load and preprocess the invoice image.
2. Extract text using Tesseract OCR.
3. Parse the extracted text into invoice fields.
4. Validate quantities, line totals, subtotal, tax, and final amount.
5. Generate JSON output.

**Important:** OCR does not understand invoice meaning in the same way an AI model does. OCR errors and ambiguous fields may require additional parsing rules or manual review.

## Extracted Invoice Information

The application is designed to extract:

- Invoice number
- Invoice date
- Supplier name
- Item descriptions
- Item quantities
- Unit prices
- Line totals
- Subtotal
- Tax amount
- Total amount
- Currency

## Example JSON Output

```json
{
  "invoice": {
    "invoice_number": "RT-2024-1052",
    "invoice_date": "14 October 2024",
    "supplier_name": "RIVERTECH SUPPLIES LTD.",
    "items": [
      {
        "description": "HDPE Pipe 110mm (6m length)",
        "quantity": "50 pcs",
        "unit_price": 1250.0,
        "line_total": 62500.0
      }
    ],
    "total_amount": 113565.0,
    "subtotal": 100500.0,
    "tax_amount": 13065.0,
    "currency": "NPR"
  },
  "validation": {
    "is_valid": true,
    "errors": [],
    "warnings": [],
    "calculated_item_sum": "100500.00"
  }
}
```

The example illustrates the intended output structure. Actual results depend on the invoice image and extraction accuracy.

## Financial Validation

The validation process checks:

- Whether required invoice fields are present.
- Whether extracted line totals match quantity multiplied by unit price, where the quantity can be interpreted.
- Whether the sum of line items matches the subtotal.
- Whether subtotal plus tax matches the invoice total.
- Whether extraction warnings or validation errors need attention.

Financial validation helps identify inconsistencies but does not guarantee that every extracted field is correct.

## Repository Structure

```text
OCR_Extractor/
│
├── invoice-extractor/
│   ├── input/
│   ├── output/
│   ├── config.py
│   ├── extractor.py
│   ├── image_processor.py
│   ├── main.py
│   └── ...
│
├── Offline_OCR_Extractor/
│   ├── input/
│   ├── output/
│   ├── config.py
│   ├── extractor.py
│   ├── image_processor.py
│   ├── parser.py
│   ├── validator.py
│   └── main.py
│
├── README.md
└── requirements.txt
```

## Requirements

- Python 3
- Dependencies listed in the relevant `requirements.txt`
- Google Gemini API access for the Gemini implementation
- Tesseract OCR and English trained data for the offline implementation

## Running the Applications

Each implementation is maintained independently.

### Gemini implementation

```powershell
cd invoice-extractor
pip install -r requirements.txt
```

Configure the Gemini API key using the method supported by the application, then run:

```powershell
python main.py input/invoice_sample.png
```

### Offline implementation

```powershell
cd Offline_OCR_Extractor
pip install -r requirements.txt
```

Configure the Tesseract trained-data directory in `config.py`, then run:

```powershell
python main.py input/invoice_sample.png
```

The offline implementation does not require a Gemini API key.

## Limitations

- OCR accuracy depends on image quality, layout, and text clarity.
- OCR may confuse similar characters, numbers, and abbreviations.
- Rule-based parsing can be sensitive to invoice layout variations.
- AI extraction depends on API availability and model responses.
- Extracted information should be reviewed before being used in financial or accounting workflows.

## Purpose

This project demonstrates two approaches to invoice data extraction and explores the engineering challenges involved in converting unstructured invoice documents into structured, validated data.
