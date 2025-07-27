import os
from typing import Tuple
from src.logger import Logger

try:
    import pymupdf
except ImportError:
    pymupdf = None
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
try:
    from pdf2image import convert_from_path
    import pytesseract
except ImportError:
    convert_from_path = None
    pytesseract = None

logger = Logger()

def extract_text_from_pdf(file_path: str) -> Tuple[str, str]:
    """
    Returns (text, method): method is 'native' or 'ocr'
    """
    # Try native extraction first
    text = ""
    method = "native"
    if pymupdf:
        try:
            doc = pymupdf.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            logger.log(f"pymupdf extraction failed: {e}", level="error")
    if not text and PyPDF2:
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            logger.log(f"PyPDF2 extraction failed: {e}", level="error")
    # If still no text, try OCR
    if not text and convert_from_path and pytesseract:
        method = "ocr"
        try:
            images = convert_from_path(file_path)
            for img in images:
                text += pytesseract.image_to_string(img, lang='deu+eng')
        except Exception as e:
            logger.log(f"OCR extraction failed: {e}", level="error")
    if not text:
        logger.log(f"No text could be extracted from {file_path}", level="error")
    return text, method
