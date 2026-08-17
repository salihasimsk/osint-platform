from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.advisory import AdvisoryResponse
from app.services import advisory_service


router = APIRouter()

router = APIRouter()


@router.get(
    "/advisories",
    response_model=list[AdvisoryResponse],
)
def list_advisories(
    severity: str | None = Query(
        default=None,
        max_length=20,
    ),
    organization: str | None = Query(
        default=None,
        max_length=100,
    ),
    keyword: str | None = Query(
        default=None,
        min_length=1,
        max_length=200,
    ),
    source_domain: str | None = Query(
        default=None,
        max_length=255,
    ),
    date_from: date | None = None,
    date_to: date | None = None,
    sort_by: Literal[
        "publication_date",
        "collection_date",
        "title",
        "organization",
        "severity",
    ] = "publication_date",
    sort_order: Literal[
        "asc",
        "desc",
    ] = "desc",
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=25,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    return advisory_service.list_advisories(
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


@router.get("/advisories/{advisory_id}", response_model=AdvisoryResponse)
def get_advisory(advisory_id: int, db: Session = Depends(get_db)):
    return advisory_service.get_advisory(db, advisory_id)


@router.delete("/advisories/{advisory_id}")
def delete_advisory(advisory_id: int, db: Session = Depends(get_db)):
    return advisory_service.delete_advisory(db, advisory_id)
