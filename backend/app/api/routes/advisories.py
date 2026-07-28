from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.advisory import Advisory
from app.schemas.advisory import AdvisoryResponse

router = APIRouter()


@router.get("/advisories", response_model=list[AdvisoryResponse])
def list_advisories(
    severity: str | None = None,
    organization: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Advisory)

    if severity:
        query = query.filter(Advisory.severity == severity)
    if organization:
        query = query.filter(Advisory.organization == organization)

    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size).all()


# Tek bir advisory'nin detayı
@router.get("/advisories/{advisory_id}", response_model=AdvisoryResponse)
def get_advisory(advisory_id: int, db: Session = Depends(get_db)):
    advisory = db.query(Advisory).filter(Advisory.id == advisory_id).first()
    if advisory is None:
        raise HTTPException(status_code=404, detail="Advisory not found")
    return advisory


# Bir advisory'yi sil
@router.delete("/advisories/{advisory_id}")
def delete_advisory(advisory_id: int, db: Session = Depends(get_db)):
    advisory = db.query(Advisory).filter(Advisory.id == advisory_id).first()
    if advisory is None:
        raise HTTPException(status_code=404, detail="Advisory not found")
    db.delete(advisory)
    db.commit()
    return {"message": "Advisory deleted successfully"}