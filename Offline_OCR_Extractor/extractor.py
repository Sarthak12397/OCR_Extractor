
import logging

from tesserocr import PyTessBaseAPI, PSM

from config import TESSDATA_PATH, OCR_LANGUAGE

logger = logging.getLogger(__name__)


def extract_invoice(image):
    try:
        with PyTessBaseAPI(
            path=str(TESSDATA_PATH),
            lang=OCR_LANGUAGE,
            psm=PSM.AUTO
        ) as api:

            api.SetImage(image)
            extracted_text = api.GetUTF8Text()

        if not extracted_text or not extracted_text.strip():
            raise ValueError("No readable text found in invoice image.")

        logger.info("Offline OCR extraction completed.")

        return extracted_text

    except Exception as error:
        logger.exception("Invoice OCR failed.")

        raise RuntimeError(
            f"Invoice OCR failed: {error}"
        ) from error
