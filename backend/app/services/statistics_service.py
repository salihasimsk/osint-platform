from sqlalchemy.orm import Session
from app.repositories import statistics_repository


def get_summary(db: Session):
    return {
        "total_advisories": statistics_repository.count_all_advisories(db),
        "critical": statistics_repository.count_advisories_by_severity(db, "critical"),
        "high": statistics_repository.count_advisories_by_severity(db, "high"),
        "medium": statistics_repository.count_advisories_by_severity(db, "medium"),
        "low": statistics_repository.count_advisories_by_severity(db, "low"),
        "active_sources": statistics_repository.count_active_sources(db),
        "completed_crawls": statistics_repository.count_completed_crawls(db),
        "unknown_severity": (statistics_repository.count_advisories_with_unknown_severity(db)),
        "by_organization": (statistics_repository.count_advisories_by_organization(db)),
    }