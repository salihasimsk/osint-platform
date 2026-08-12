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
    
def get_advisory_by_url(db: Session, url: str):
    """Find an advisory by its URL (used to avoid duplicates)."""
    return db.query(Advisory).filter(Advisory.url == url).first()


def create_advisory(db: Session, advisory_data: dict):
    """Create a new advisory from a dictionary of parsed data."""
    new_advisory = Advisory(
    title=advisory_data.get("title"),
    url=advisory_data.get("url"),
    organization=advisory_data.get("organization"),
    publication_date=advisory_data.get("publication_date"),
    source_domain=advisory_data.get("source_domain"),
    cve=advisory_data.get("cve"),
    product=advisory_data.get("product"),
    severity=advisory_data.get("severity"),
    summary=advisory_data.get("summary"),
    crawl_job_id=advisory_data.get("crawl_job_id"),
)
    db.add(new_advisory)
    db.commit()
    db.refresh(new_advisory)
    return new_advisory


def update_advisory_from_crawl(
    db: Session,
    advisory,
    advisory_data: dict,
):
    advisory.publication_date = advisory_data.get("publication_date")
    advisory.cve = advisory_data.get("cve")
    advisory.summary = advisory_data.get("summary")

    if advisory.crawl_job_id is None:
        advisory.crawl_job_id = advisory_data.get("crawl_job_id")

    db.commit()
    db.refresh(advisory)
    return advisory