from fastapi import APIRouter, Depends,BackgroundTasks
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.crawl_job import CrawlJobCreate, CrawlJobResponse
from app.services import crawl_job_service
from app.schemas.crawl_log import CrawlLogResponse
from app.services import crawl_log_service


router = APIRouter()


@router.post(
    "/crawls",
    response_model=CrawlJobResponse,
)
def start_crawl(
    crawl: CrawlJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = crawl_job_service.start_crawl(
        db,
        crawl,
    )

    background_tasks.add_task(
        crawl_job_service.execute_crawl_job,
        job.job_id,
        crawl.source_ids,
        crawl.maximum_pages,
        crawl.date_from,
        crawl.keywords,
    )

    return job


@router.get("/crawls", response_model=list[CrawlJobResponse])
def list_crawls(db: Session = Depends(get_db)):
    return crawl_job_service.list_crawls(db)


@router.get("/crawls/{job_id}", response_model=CrawlJobResponse)
def get_crawl(job_id: str, db: Session = Depends(get_db)):
    return crawl_job_service.get_crawl(db, job_id)

@router.get(
    "/crawls/{job_id}/logs",
    response_model=list[CrawlLogResponse],
)

def get_crawl_logs(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = crawl_job_service.get_crawl(
        db,
        job_id,
    )

    return crawl_log_service.list_logs(
        db,
        crawl_job_id=job.id,
        page=1,
        page_size=20,
    )

@router.post("/crawls/{job_id}/stop", response_model=CrawlJobResponse)
def stop_crawl(job_id: str, db: Session = Depends(get_db)):
    return crawl_job_service.stop_crawl(db, job_id)
