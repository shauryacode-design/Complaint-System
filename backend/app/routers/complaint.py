from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.complaint import Complaint
from app.schemas.complaint import ComplaintData, ComplaintResponse


router = APIRouter(
    prefix="/complaints",
    tags=["Complaints"],
)


@router.post("/", response_model=ComplaintResponse)
def create_complaint(
    complaint_data: ComplaintData,
    db: Session = Depends(get_db),
):
    complaint = Complaint(**complaint_data.model_dump())

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    return complaint


@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
):
    complaint = (
        db.query(Complaint)
        .filter(Complaint.id == complaint_id)
        .first()
    )

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found",
        )

    return complaint