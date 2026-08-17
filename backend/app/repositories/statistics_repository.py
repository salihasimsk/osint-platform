from sqlalchemy.orm import Session
from app.models.advisory import Advisory
from app.models.source import Source
from app.models.crawl_job import CrawlJob
from sqlalchemy import func

def count_all_advisories(db: Session):
    return db.query(Advisory).count()


def count_advisories_by_severity(db: Session, severity: str):
    return db.query(Advisory).filter(Advisory.severity == severity).count()


def count_active_sources(db: Session):
    return db.query(Source).filter(Source.enabled_status == True).count()


def count_completed_crawls(db: Session):
    return db.query(CrawlJob).filter(CrawlJob.status == "completed").count()

def count_advisories_with_unknown_severity(db: Session):
    return db.query(Advisory).filter(
        Advisory.severity.is_(None)
    ).count()

def count_advisories_by_organization(db: Session):
    rows = (
        db.query(
            Advisory.organization,
            func.count(Advisory.id),
        )
        .group_by(Advisory.organization)
        .all()
    )

    return {
        organization: count
        for organization, count in rows
    }
