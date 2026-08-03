from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import advisory_repository


def list_advisories(db: Session, severity=None, organization=None, page=1, page_size=25):
    return advisory_repository.get_advisories(
        db, severity=severity, organization=organization, page=page, page_size=page_size
    )


def get_advisory(db: Session, advisory_id: int):
    advisory = advisory_repository.get_advisory_by_id(db, advisory_id)
    if advisory is None:
        raise HTTPException(status_code=404, detail="Advisory not found")
    return advisory


def delete_advisory(db: Session, advisory_id: int):
    advisory = advisory_repository.get_advisory_by_id(db, advisory_id)
    if advisory is None:
        raise HTTPException(status_code=404, detail="Advisory not found")
    advisory_repository.delete_advisory(db, advisory)
    return {"message": "Advisory deleted successfully"}