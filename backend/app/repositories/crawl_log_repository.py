from sqlalchemy.orm import Session
from app.models.crawl_log import CrawlLog


def get_logs(db: Session, crawl_job_id=None, log_level=None, source=None, page=1, page_size=50):
    query = db.query(CrawlLog)

    if crawl_job_id:
        query = query.filter(CrawlLog.crawl_job_id == crawl_job_id)
    if log_level:
        query = query.filter(CrawlLog.log_level == log_level)
    if source:
        query = query.filter(CrawlLog.source == source)

    offset = (page - 1) * page_size
    return query.order_by(CrawlLog.timestamp.desc()).offset(offset).limit(page_size).all()

def create_log(db: Session, message: str, log_level: str = "info", source: str = None, crawl_job_id: int = None):
    new_log = CrawlLog(
        message=message,
        log_level=log_level,
        source=source,
        crawl_job_id=crawl_job_id,
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log