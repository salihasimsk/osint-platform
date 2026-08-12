from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import source_repository



def list_sources(db: Session):
    return source_repository.get_all_sources(db)


def get_source(db: Session, source_id: int):
    source = source_repository.get_source_by_id(db, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


def create_source(db: Session, source_data):
    return source_repository.create_source(db, source_data)


def update_source(db: Session, source_id: int, source_data):
    source = source_repository.get_source_by_id(db, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return source_repository.update_source(db, source, source_data)


def update_source_status(db: Session, source_id: int, enabled: bool):
    source = source_repository.get_source_by_id(db, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return source_repository.update_source_status(db, source, enabled)

def delete_source(db: Session, source_id: int):
    source = source_repository.get_source_by_id(db, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    source_repository.delete_source(db, source)
    return {"message": "Source deleted successfully"}