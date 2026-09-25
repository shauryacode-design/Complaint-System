from typing import Any
from io import BytesIO

import fitz
import pytesseract

from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel
from pypdf import PdfReader
from PIL import Image

from app.services.ai.complaint_graph import (
    complaint_graph,
    edit_complaint_graph,
)


import os

if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


class ComplaintInput(BaseModel):
    text: str


class ComplaintEditInput(BaseModel):
    text: str
    complaint: dict[str, Any]


def extract_text_with_ocr(pdf_bytes: bytes) -> str:
    """
    Extract text from a PDF.

    First tries normal PDF text extraction.
    If no text is found, renders the PDF pages as images
    and uses Tesseract OCR.
    """

    # 1. Try normal text extraction
    reader = PdfReader(BytesIO(pdf_bytes))

    extracted_text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            extracted_text += page_text + "\n"

    if extracted_text.strip():
        return extracted_text.strip()

    # 2. No selectable text -> OCR
    ocr_text = ""

    pdf_document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf",
    )

    try:
        for page in pdf_document:

            # Render page at higher resolution for better OCR
            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(2, 2)
            )

            image_bytes = pixmap.tobytes("png")

            image = Image.open(
                BytesIO(image_bytes)
            )

            page_text = pytesseract.image_to_string(
                image
            )

            if page_text:
                ocr_text += page_text + "\n"

    finally:
        pdf_document.close()

    return ocr_text.strip()


@router.post("/analyze-complaint")
def analyze_complaint(user_input: ComplaintInput):

    result = complaint_graph.invoke(
        {
            "user_input": user_input.text,
            "complaint": {},
            "risk_assessment": {},
            "completeness": {},
            "summary": "",
        }
    )

    return {
        "complaint": result["complaint"],
        "risk_assessment": result["risk_assessment"],
        "completeness": result["completeness"],
        "summary": result["summary"],
        "message": (
            "Complaint parsed successfully. I've extracted the complaint "
            "details and generated an initial risk assessment. You can "
            "review the populated complaint form or tell me if you need "
            "to correct any information."
        ),
    }


@router.post("/edit-complaint")
def edit_complaint(user_input: ComplaintEditInput):

    result = edit_complaint_graph.invoke(
        {
            "user_input": user_input.text,
            "complaint": user_input.complaint,
            "risk_assessment": {},
            "completeness": {},
            "summary": "",
        }
    )

    return {
        "complaint": result["complaint"],
        "risk_assessment": result["risk_assessment"],
        "completeness": result["completeness"],
        "summary": result["summary"],
        "message": (
            "I've updated the complaint with the changes you provided "
            "and recalculated the initial risk assessment."
        ),
    }


@router.post("/analyze-document")
async def analyze_document(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        return {
            "error": "Only PDF files are supported."
        }

    pdf_bytes = await file.read()

    try:
        extracted_text = extract_text_with_ocr(pdf_bytes)

    except pytesseract.TesseractNotFoundError:
        return {
            "error": (
                "Tesseract OCR could not be found. "
                "Please check the Tesseract installation."
            )
        }

    except Exception as exc:
        return {
            "error": f"Failed to process PDF: {str(exc)}"
        }

    if not extracted_text:
        return {
            "error": (
                "OCR could not extract any readable text from the PDF."
            )
        }

    result = complaint_graph.invoke(
        {
            "user_input": extracted_text,
            "complaint": {},
            "risk_assessment": {},
            "completeness": {},
            "summary": "",
        }
    )

    return {
        "complaint": result["complaint"],
        "risk_assessment": result["risk_assessment"],
        "completeness": result["completeness"],
        "summary": result["summary"],
        "message": (
            "I've extracted the complaint information from the PDF "
            "using text extraction/OCR and generated an initial "
            "risk assessment."
        ),
    }
