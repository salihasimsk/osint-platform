from sqlalchemy.orm import Session
from app.models.source import Source


def get_all_sources(db: Session):
    return db.query(Source).all()


def get_source_by_id(db: Session, source_id: int):
    return db.query(Source).filter(Source.id == source_id).first()


def create_source(db: Session, source_data):
    new_source = Source(
        name=source_data.name,
        base_url=source_data.base_url,
        enabled_status=source_data.enabled_status,
        request_delay=source_data.request_delay,
    )
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return new_source


def update_source(db: Session, source, source_data):
    source.name = source_data.name
    source.base_url = source_data.base_url
    source.enabled_status = source_data.enabled_status
    source.request_delay = source_data.request_delay
    db.commit()
    db.refresh(source)
    return source


def update_source_status(db: Session, source, enabled: bool):
    source.enabled_status = enabled
    db.commit()
    db.refresh(source)
    return source

def delete_source(db: Session, source):
    db.delete(source)
    db.commit()