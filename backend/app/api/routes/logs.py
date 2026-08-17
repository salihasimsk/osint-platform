from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.crawl_log import CrawlLogResponse
from app.services import crawl_log_service

router = APIRouter()


@router.get("/logs", response_model=list[CrawlLogResponse])
def list_logs(
    crawl_job_id: int | None = None,
    log_level: str | None = None,
    source: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return crawl_log_service.list_logs(
        db, crawl_job_id=crawl_job_id, log_level=log_level, source=source, page=page, page_size=page_size
    )
