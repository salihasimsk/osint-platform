from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories import crawl_log_repository
from app.repositories import crawl_job_repository
from app.repositories import advisory_repository
from app.crawler.engine import CrawlerEngine
from app.crawler.parsers.ubuntu_parser import UbuntuParser
from app.crawler.parsers.cert_parser import CertParser
from app.crawler.parsers.cisa_kev_parser import CisaKevParser


def start_crawl(db: Session, crawl_data):
    job_id = crawl_job_repository.generate_job_id(db)
    configuration = crawl_data.model_dump(mode="json")
    source_id = crawl_data.source_ids[0]
    return crawl_job_repository.create_crawl(db, job_id, source_id, configuration)

def list_crawls(db: Session):
    return crawl_job_repository.get_all_crawls(db)


def get_crawl(db: Session, job_id: str):
    job = crawl_job_repository.get_crawl_by_job_id(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    return job


def stop_crawl(db: Session, job_id: str):
    job = crawl_job_repository.get_crawl_by_job_id(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    return crawl_job_repository.update_crawl_status(db, job, "stopped")

def get_parser_for_source(source):
    """Choose the correct parser based on the source domain."""
    if "ubuntu.com" in source.base_url:
        return UbuntuParser()
    elif "kb.cert.org" in source.base_url:
        return CertParser()
    elif "raw.githubusercontent.com/cisagov/kev-data" in source.base_url:
        return CisaKevParser()
    else:
        raise ValueError(f"No parser available for source: {source.base_url}")

def run_crawl(db, source, crawl_job_id, max_pages=3):
    parser = get_parser_for_source(source)
    engine = CrawlerEngine(request_delay=source.request_delay)
    collected = engine.crawl(source.base_url, parser, max_pages=max_pages)

    saved_count = 0
    skipped_count = 0

    for advisory_data in collected:
        advisory_data["crawl_job_id"] = crawl_job_id

        # If the advisory has no CVE yet, try to fetch it from the detail page
        if not advisory_data.get("cve") and hasattr(parser, "parse_detail"):
            detail_html = engine.fetch_page(advisory_data["url"])
            if detail_html:
                detail_data = parser.parse_detail(detail_html)
                advisory_data["cve"] = detail_data.get("cve")

        existing = advisory_repository.get_advisory_by_url(db, advisory_data["url"])
        if existing:
            advisory_repository.update_advisory_from_crawl(db, existing, advisory_data)
            skipped_count += 1
            continue
        advisory_repository.create_advisory(db, advisory_data)
        saved_count += 1

    return {
        "pages_visited": engine.pages_visited,
        "collected": len(collected),
        "saved": saved_count,
        "skipped": skipped_count,
    }
    
def execute_crawl_job(job_id: str, source_id: int, max_pages: int = 3):
    from app.database.database import SessionLocal
    from app.repositories import source_repository

    db = SessionLocal()
    try:
        job = crawl_job_repository.get_crawl_by_job_id(db, job_id)
        source = source_repository.get_source_by_id(db, source_id)

        if job is None or source is None:
            return

        crawl_job_repository.start_crawl_job(db, job)
        # Update the source's last crawl date
        source_repository.update_last_crawl_date(db, source)
        crawl_log_repository.create_log(
            db,
            message=f"Crawl started for {source.name}",
            log_level="info",
            source=source.name,
            crawl_job_id=job.id,
        )

        try:
            result = run_crawl(db=db, source=source, crawl_job_id=job.id, max_pages=max_pages)
            crawl_job_repository.complete_crawl(
                db=db, job=job,
                pages_visited=result["pages_visited"],
                records_extracted=result["collected"],
            )
            crawl_log_repository.create_log(
                db,
                message=f"Crawl completed. Pages: {result['pages_visited']}, Saved: {result['saved']}, Skipped: {result['skipped']}",
                log_level="info",
                source=source.name,
                crawl_job_id=job.id,
            )
        except Exception as e:
            db.rollback()
            crawl_job_repository.fail_crawl(db, job)
            crawl_log_repository.create_log(
                db,
                message=f"Crawl failed: {str(e)}",
                log_level="error",
                source=source.name,
                crawl_job_id=job.id,
            )
    finally:
        db.close()