from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import crawl_job_repository


def start_crawl(db: Session, crawl_data):
    job_id = crawl_job_repository.generate_job_id(db)
    configuration = crawl_data.model_dump(mode="json")
    return crawl_job_repository.create_crawl(db, job_id, configuration)


def list_crawls(db: Session):
    return crawl_job_repository.get_all_crawls(db)


def get_crawl(db: Session, job_id: str):
    job = crawl_job_repository.get_crawl_by_job_id(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    return job


def stop_crawl(db: Session, job_id: str):
    job = crawl_job_repository.get_crawl_by_job_id(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    return crawl_job_repository.update_crawl_status(db, job, "stopped")