from sqlalchemy.orm import Session
from datetime import datetime,timezone
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


def create_crawl(db, job_id, source_id, configuration):
    new_job = CrawlJob(
        job_id=job_id,
        source_id=source_id,
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

def start_crawl_job(db: Session, job):
    job.status = "running"
    job.started_date = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    return job

def update_crawl_progress(
    db: Session,
    job,
    progress: int,
    pages_visited: int,
    records_extracted: int,
    error_count: int,
):
    job.progress = max(
        0,
        min(progress, 99),
    )
    job.pages_visited = pages_visited
    job.records_extracted = records_extracted
    job.error_count = error_count

    db.commit()
    db.refresh(job)

    return job

def complete_crawl(
    db: Session,
    job,
    pages_visited: int,
    records_extracted: int,
    error_count: int = 0,
):
    job.status = "completed"
    job.progress = 100
    job.pages_visited = pages_visited
    job.records_extracted = records_extracted
    job.error_count = error_count
    job.completed_date = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(job)

    return job

def fail_crawl(db: Session, job):
    job.status = "failed"
    job.error_count += 1
    job.completed_date = datetime.now(timezone.utc)

    db.commit()
    db.refresh(job)
    return job
