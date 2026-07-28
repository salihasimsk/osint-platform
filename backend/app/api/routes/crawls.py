from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.database import get_db
from app.models.crawl_job import CrawlJob
from app.schemas.crawl_job import CrawlJobCreate, CrawlJobResponse

router = APIRouter()


# Okunabilir job_id üret: crawl_20260728_001 gibi
def generate_job_id(db: Session) -> str:
    today = datetime.now().strftime("%Y%m%d")
    count_today = db.query(CrawlJob).filter(
        CrawlJob.job_id.like(f"crawl_{today}_%")
    ).count()
    sequence = count_today + 1
    return f"crawl_{today}_{sequence:03d}"


# Tarama başlat
@router.post("/crawls", response_model=CrawlJobResponse)
def start_crawl(crawl: CrawlJobCreate, db: Session = Depends(get_db)):
    new_job = CrawlJob(
        job_id=generate_job_id(db),
        status="queued",
        configuration=crawl.model_dump(mode="json"),
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job


# Tüm taramaları listele
@router.get("/crawls", response_model=list[CrawlJobResponse])
def list_crawls(db: Session = Depends(get_db)):
    return db.query(CrawlJob).all()



@router.get("/crawls/{job_id}", response_model=CrawlJobResponse)
def get_crawl(job_id: str, db: Session = Depends(get_db)):
    job = db.query(CrawlJob).filter(CrawlJob.job_id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    return job


@router.post("/crawls/{job_id}/stop", response_model=CrawlJobResponse)
def stop_crawl(job_id: str, db: Session = Depends(get_db)):
    job = db.query(CrawlJob).filter(CrawlJob.job_id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    job.status = "stopped"
    db.commit()
    db.refresh(job)
    return job