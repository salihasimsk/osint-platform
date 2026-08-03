from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.advisory import AdvisoryResponse
from app.services import advisory_service

router = APIRouter()


@router.get("/advisories", response_model=list[AdvisoryResponse])
def list_advisories(
    severity: str | None = None,
    organization: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return advisory_service.list_advisories(
        db, severity=severity, organization=organization, page=page, page_size=page_size
    )


@router.get("/advisories/{advisory_id}", response_model=AdvisoryResponse)
def get_advisory(advisory_id: int, db: Session = Depends(get_db)):
    return advisory_service.get_advisory(db, advisory_id)


@router.delete("/advisories/{advisory_id}")
def delete_advisory(advisory_id: int, db: Session = Depends(get_db)):
    return advisory_service.delete_advisory(db, advisory_id)