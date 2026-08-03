from sqlalchemy.orm import Session

from app.repositories import crawl_log_repository


def list_logs(db: Session, crawl_job_id=None, log_level=None, source=None, page=1, page_size=50):
    return crawl_log_repository.get_logs(
        db, crawl_job_id=crawl_job_id, log_level=log_level, source=source, page=page, page_size=page_size
    )