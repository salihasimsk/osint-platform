from datetime import date, datetime, time

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.advisory import Advisory


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


def get_advisories(
    db: Session,
    severity=None,
    organization=None,
    keyword=None,
    source_domain=None,
    date_from: date | None = None,
    date_to: date | None = None,
    sort_by="publication_date",
    sort_order="desc",
    page=1,
    page_size=25,
):
    query = db.query(Advisory)

    if severity:
        query = query.filter(
            func.lower(Advisory.severity)
            == severity.lower()
        )

    if organization:
        query = query.filter(
            func.lower(Advisory.organization)
            == organization.lower()
        )

    if source_domain:
        query = query.filter(
            func.lower(Advisory.source_domain)
            == source_domain.lower()
        )

    if keyword:
        search_pattern = f"%{keyword.strip()}%"

        query = query.filter(
            or_(
                Advisory.title.ilike(search_pattern),
                Advisory.summary.ilike(search_pattern),
                Advisory.cve.ilike(search_pattern),
                Advisory.product.ilike(search_pattern),
            )
        )

    if date_from:
        start_datetime = datetime.combine(
            date_from,
            time.min,
        )
        query = query.filter(
            Advisory.publication_date
            >= start_datetime
        )

    if date_to:
        end_datetime = datetime.combine(
            date_to,
            time.max,
        )
        query = query.filter(
            Advisory.publication_date
            <= end_datetime
        )

    sort_columns = {
        "publication_date": Advisory.publication_date,
        "collection_date": Advisory.collection_date,
        "title": Advisory.title,
        "organization": Advisory.organization,
        "severity": Advisory.severity,
    }

    sort_column = sort_columns.get(
        sort_by,
        Advisory.publication_date,
    )

    if sort_order == "asc":
        query = query.order_by(
            sort_column.asc(),
            Advisory.id.asc(),
        )
    else:
        query = query.order_by(
            sort_column.desc(),
            Advisory.id.desc(),
        )

    offset = (page - 1) * page_size

    return query.offset(offset).limit(
        page_size
    ).all()

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

    db.add(new_advisory)
    db.commit()
    db.refresh(new_advisory)
    return new_advisory


def update_advisory_from_crawl(
    db: Session,
    advisory,
    advisory_data: dict,
):
    publication_date = parse_date(
        advisory_data.get("publication_date")
    )

    if publication_date is not None:
        advisory.publication_date = publication_date

    update_fields = (
        "title",
        "organization",
        "source_domain",
        "cve",
        "product",
        "severity",
        "summary",
    )

    for field_name in update_fields:
        new_value = advisory_data.get(field_name)

        if new_value is not None:
            setattr(
                advisory,
                field_name,
                new_value,
            )

    if advisory.crawl_job_id is None:
        advisory.crawl_job_id = advisory_data.get(
            "crawl_job_id"
        )

    db.commit()
    db.refresh(advisory)

    return advisory
