from sqlalchemy.orm import Session
from datetime import datetime
from app.models.crawl_job import CrawlJob


def generate_job_id(db: Session) -> str:
    today = datetime.now().strftime("%Y%m%d")
    count_today = db.query(CrawlJob).filter(
        CrawlJob.job_id.like(f"crawl_{today}_%")
    ).count()
    sequence = count_today + 1
    return f"crawl_{today}_{sequence:03d}"


def get_all_crawls(db: Session):
    return db.query(CrawlJob).all()


def get_crawl_by_job_id(db: Session, job_id: str):
    return db.query(CrawlJob).filter(CrawlJob.job_id == job_id).first()


def create_crawl(db: Session, job_id: str, configuration):
    new_job = CrawlJob(
        job_id=job_id,
        status="queued",
        configuration=configuration,
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job


def update_crawl_status(db: Session, job, status: str):
    job.status = status
    db.commit()
    db.refresh(job)
    return job