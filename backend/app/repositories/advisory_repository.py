from sqlalchemy.orm import Session
from app.models.advisory import Advisory


def get_advisories(db: Session, severity=None, organization=None, page=1, page_size=25):
    query = db.query(Advisory)

    if severity:
        query = query.filter(Advisory.severity == severity)
    if organization:
        query = query.filter(Advisory.organization == organization)

    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size).all()


def get_advisory_by_id(db: Session, advisory_id: int):
    return db.query(Advisory).filter(Advisory.id == advisory_id).first()


def delete_advisory(db: Session, advisory):
    db.delete(advisory)
    db.commit()