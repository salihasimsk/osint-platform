from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.crawl_job import CrawlJobCreate, CrawlJobResponse
from app.services import crawl_job_service

router = APIRouter()


@router.post("/crawls", response_model=CrawlJobResponse)
def start_crawl(crawl: CrawlJobCreate, db: Session = Depends(get_db)):
    return crawl_job_service.start_crawl(db, crawl)


@router.get("/crawls", response_model=list[CrawlJobResponse])
def list_crawls(db: Session = Depends(get_db)):
    return crawl_job_service.list_crawls(db)


@router.get("/crawls/{job_id}", response_model=CrawlJobResponse)
def get_crawl(job_id: str, db: Session = Depends(get_db)):
    return crawl_job_service.get_crawl(db, job_id)


@router.post("/crawls/{job_id}/stop", response_model=CrawlJobResponse)
def stop_crawl(job_id: str, db: Session = Depends(get_db)):
    return crawl_job_service.stop_crawl(db, job_id)