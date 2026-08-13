from sqlalchemy.orm import Session
from app.models.advisory import Advisory

from datetime import datetime


def parse_date(date_str):
    """Convert a date string into a datetime object. Returns None if it fails."""
    if not date_str:
        return None
    # If it's already a datetime, return as is
    if isinstance(date_str, datetime):
        return date_str
    # Try common date formats
    formats = [
        "%Y-%m-%d",        # 2026-08-11 (CERT)
        "%d %B %Y",        # 11 August 2026 (Ubuntu)
        "%Y-%m-%dT%H:%M:%S",  # ISO with time
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None  # couldn't parse, store as null


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
    
def get_advisory_by_url(db: Session, url: str):
    """Find an advisory by its URL (used to avoid duplicates)."""
    return db.query(Advisory).filter(Advisory.url == url).first()


def create_advisory(db: Session, advisory_data: dict):
    new_advisory = Advisory(
        title=advisory_data.get("title"),
        url=advisory_data.get("url"),
        organization=advisory_data.get("organization"),
        publication_date=parse_date(advisory_data.get("publication_date")),  # ← çevir
        source_domain=advisory_data.get("source_domain"),
        cve=advisory_data.get("cve"),
        product=advisory_data.get("product"),
        severity=advisory_data.get("severity"),
        summary=advisory_data.get("summary"),
        crawl_job_id=advisory_data.get("crawl_job_id"),
    )
    ...
    db.add(new_advisory)
    db.commit()
    db.refresh(new_advisory)
    return new_advisory


def update_advisory_from_crawl(
    db: Session,
    advisory,
    advisory_data: dict,
):
    advisory.publication_date = parse_date(advisory_data.get("publication_date"))
    advisory.cve = advisory_data.get("cve")
    advisory.summary = advisory_data.get("summary")

    if advisory.crawl_job_id is None:
        advisory.crawl_job_id = advisory_data.get("crawl_job_id")

    db.commit()
    db.refresh(advisory)
    return advisory