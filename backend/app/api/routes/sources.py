from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.source import Source
from app.schemas.source import SourceCreate, SourceResponse

router = APIRouter()

@router.post("/sources", response_model=SourceResponse)
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    new_source = Source(
        name=source.name,
        base_url=source.base_url,
        enabled_status=source.enabled_status,
        request_delay=source.request_delay
    )
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return new_source

@router.get("/sources", response_model=list[SourceResponse])
def get_sources(db: Session = Depends(get_db)):
    return db.query(Source).all()


@router.put("/sources/{source_id}", response_model=SourceResponse)
def update_source(source_id: int, source: SourceCreate, db: Session = Depends(get_db)):
    existing = db.query(Source).filter(Source.id == source_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Source not found")
    
    existing.name = source.name
    base_url = source.base_url
    existing.enabled_status = source.enabled_status
    existing.request_delay = source.request_delay
    
    db.commit()
    db.refresh(existing)
    return existing 


@router.patch("/sources/{source_id}/enable", response_model=SourceResponse)
def update_source_status(source_id: int,enabled:bool, db: Session = Depends(get_db)):
    existing = db.query(Source).filter(Source.id == source_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Source not found")
    
    existing.enabled = enabled
    db.commit()
    db.refresh(existing)
    return existing
