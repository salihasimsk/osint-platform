from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.crawl_log import CrawlLog
from app.schemas.crawl_log import CrawlLogResponse

router = APIRouter()


# Logları listele (filtreleme + sayfalama)
@router.get("/logs", response_model=list[CrawlLogResponse])
def list_logs(
    crawl_job_id: str | None = None,
    log_level: str | None = None,
    source: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(CrawlLog)

    if crawl_job_id:
        query = query.filter(CrawlLog.crawl_job_id == crawl_job_id)
    if log_level:
        query = query.filter(CrawlLog.log_level == log_level)
    if source:
        query = query.filter(CrawlLog.source == source)

    offset = (page - 1) * page_size
    return query.order_by(CrawlLog.timestamp.desc()).offset(offset).limit(page_size).all()