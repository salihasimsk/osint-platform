from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.repositories import advisory_repository


def list_advisories(
    db: Session,
    severity=None,
    organization=None,
    keyword=None,
    source_domain=None,
    date_from: date | None = None,
    date_to: date | None = None,
    sort_by="publication_date",
    sort_order="desc",
    page=1,
    page_size=25,
):
    if (
        date_from
        and date_to
        and date_from > date_to
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "date_from cannot be later "
                "than date_to"
            ),
        )

    return advisory_repository.get_advisories(
        db,
        severity=severity,
        organization=organization,
        keyword=keyword,
        source_domain=source_domain,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
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

def export_advisories(
    db: Session,
    severity=None,
    organization=None,
    keyword=None,
    source_domain=None,
    date_from: date | None = None,
    date_to: date | None = None,
    sort_by="publication_date",
    sort_order="desc",
):
    if (
        date_from
        and date_to
        and date_from > date_to
    ):
        raise HTTPException(
            status_code=400,
            detail="date_from cannot be later than date_to",
        )

    return advisory_repository.get_advisories_for_export(
        db,
        severity=severity,
        organization=organization,
        keyword=keyword,
        source_domain=source_domain,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
    )