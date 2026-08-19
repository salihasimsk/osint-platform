from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.source import SourceCreate, SourceResponse
from app.services import source_service
from app.crawler.robots import can_crawl

router = APIRouter()


@router.get("/sources", response_model=list[SourceResponse])
def list_sources(db: Session = Depends(get_db)):
    return source_service.list_sources(db)


@router.post("/sources", response_model=SourceResponse)
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    return source_service.create_source(db, source)


@router.put("/sources/{source_id}", response_model=SourceResponse)
def update_source(source_id: int, source: SourceCreate, db: Session = Depends(get_db)):
    return source_service.update_source(db, source_id, source)


@router.patch("/sources/{source_id}/status", response_model=SourceResponse)
def update_source_status(source_id: int, enabled: bool, db: Session = Depends(get_db)):
    return source_service.update_source_status(db, source_id, enabled)

@router.delete("/sources/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    return source_service.delete_source(db, source_id)

@router.get("/sources/{source_id}/robots")
def get_source_robots_status(
    source_id: int,
    db: Session = Depends(get_db),
):
    source = source_service.get_source(
        db,
        source_id,
    )

    allowed = can_crawl(source.base_url)

    return {
        "source_id": source.id,
        "allowed": allowed,
    }