from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pypdf import PdfReader
from io import BytesIO

from ..database import SessionLocal
from ..models import Deviation
from ..schemas import (
    DeviationCreate,
    DeviationResponse,
    DeviationAnalyzeRequest,
    DeviationAIResult
)

from ..ai.graph import deviation_graph


router = APIRouter(
    prefix="/api/deviations",
    tags=["Deviations"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# -----------------------------------------
# SAVE DEVIATION
# -----------------------------------------

@router.post("/", response_model=DeviationResponse)
def create_deviation(
    deviation: DeviationCreate,
    db: Session = Depends(get_db)
):
    new_deviation = Deviation(**deviation.model_dump())

    db.add(new_deviation)
    db.commit()
    db.refresh(new_deviation)

    return new_deviation


# -----------------------------------------
# ANALYZE PASTED TEXT
# -----------------------------------------

@router.post("/analyze", response_model=DeviationAIResult)
def analyze_deviation(
    request: DeviationAnalyzeRequest
):
    result = deviation_graph.invoke({
        "input_text": request.input_text
    })

    return result


# -----------------------------------------
# ANALYZE PDF
# -----------------------------------------

@router.post("/analyze-pdf", response_model=DeviationAIResult)
async def analyze_pdf(
    file: UploadFile = File(...)
):
    # Make sure the uploaded file is a PDF
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file."
        )

    # Read the uploaded PDF
    pdf_bytes = await file.read()

    try:
        reader = PdfReader(BytesIO(pdf_bytes))

        extracted_text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                extracted_text += page_text + "\n"

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read PDF: {str(e)}"
        )

    # Make sure the PDF actually contained text
    if not extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from the PDF."
        )

    # Send extracted text through our existing AI workflow
    result = deviation_graph.invoke({
        "input_text": extracted_text
    })

    return result