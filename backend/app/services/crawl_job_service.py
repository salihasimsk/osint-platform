from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.repositories import crawl_log_repository
from app.repositories import crawl_job_repository
from app.repositories import advisory_repository
from app.crawler.engine import CrawlerEngine
from app.crawler.parsers.ubuntu_parser import UbuntuParser
from app.crawler.parsers.cert_parser import CertParser
from app.crawler.parsers.cisa_kev_parser import CisaKevParser
from app.crawler.parsers.nvd_parser import NvdParser
from app.crawler.parsers.red_hat_parser import RedHatParser
from app.repositories import source_repository



def start_crawl(
    db: Session,
    crawl_data,
):
    sources = []

    for source_id in crawl_data.source_ids:
        source = source_repository.get_source_by_id(
            db,
            source_id,
        )

        if source is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Source not found: {source_id}"
                ),
            )

        if not source.enabled_status:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Source is disabled: {source_id}"
                ),
            )

        sources.append(source)

    job_id = crawl_job_repository.generate_job_id(
        db
    )

    configuration = crawl_data.model_dump(
        mode="json"
    )

    primary_source_id = sources[0].id

    return crawl_job_repository.create_crawl(
        db,
        job_id,
        primary_source_id,
        configuration,
    )

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
    elif "services.nvd.nist.gov" in source.base_url:
        return NvdParser()
    elif "access.redhat.com" in source.base_url:
        return RedHatParser()
    else:
        raise ValueError(f"No parser available for source: {source.base_url}")

def get_crawl_url_for_source(source):
    base_url = source.base_url
    parsed_url = urlparse(base_url)
    query_params = parse_qs(parsed_url.query)

    if "services.nvd.nist.gov" in base_url:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        query_params["resultsPerPage"] = ["10"]
        query_params["pubStartDate"] = [
            start_date.isoformat(timespec="milliseconds")
        ]
        query_params["pubEndDate"] = [
            end_date.isoformat(timespec="milliseconds")
        ]

    elif "access.redhat.com" in base_url:
        query_params["created_days_ago"] = ["30"]
        query_params["per_page"] = ["10"]
        query_params["page"] = ["1"]
        query_params["isCompressed"] = ["false"]

    else:
        return base_url

    new_query = urlencode(
        query_params,
        doseq=True,
    )

    return urlunparse(
        parsed_url._replace(query=new_query)
    )

def run_crawl(db, source, crawl_job_id, max_pages=3):
    parser = get_parser_for_source(source)
    crawl_url = get_crawl_url_for_source(source)

    engine = CrawlerEngine(
        request_delay=source.request_delay
    )

    collected = engine.crawl(
        crawl_url,
        parser,
        max_pages=max_pages,
    )

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

def execute_crawl_job(
    job_id: str,
    source_ids: list[int],
    max_pages: int = 3,
):
    from app.database.database import SessionLocal

    db = SessionLocal()

    try:
        job = (
            crawl_job_repository
            .get_crawl_by_job_id(db, job_id)
        )

        if job is None:
            return

        crawl_job_repository.start_crawl_job(
            db,
            job,
        )

        total_pages = 0
        total_records = 0
        total_errors = 0
        source_count = len(source_ids)

        for source_number, source_id in enumerate(
            source_ids,
            start=1,
        ):
            db.refresh(job)

            # Stop was requested through the API.
            if job.status == "stopped":
                return

            source = (
                source_repository
                .get_source_by_id(db, source_id)
            )

            if (
                source is None
                or not source.enabled_status
            ):
                total_errors += 1

                crawl_log_repository.create_log(
                    db,
                    message=(
                        "Source could not be processed: "
                        f"{source_id}"
                    ),
                    log_level="error",
                    source=f"source:{source_id}",
                    crawl_job_id=job.id,
                )

            else:
                source_name = source.name

                source_repository.update_last_crawl_date(
                    db,
                    source,
                )

                crawl_log_repository.create_log(
                    db,
                    message=(
                        f"Crawl started for "
                        f"{source_name}"
                    ),
                    log_level="info",
                    source=source_name,
                    crawl_job_id=job.id,
                )

                try:
                    result = run_crawl(
                        db=db,
                        source=source,
                        crawl_job_id=job.id,
                        max_pages=max_pages,
                    )

                    total_pages += result[
                        "pages_visited"
                    ]
                    total_records += result[
                        "collected"
                    ]

                    crawl_log_repository.create_log(
                        db,
                        message=(
                            "Crawl completed. "
                            f"Pages: {result['pages_visited']}, "
                            f"Saved: {result['saved']}, "
                            f"Skipped: {result['skipped']}"
                        ),
                        log_level="info",
                        source=source_name,
                        crawl_job_id=job.id,
                    )

                except Exception:
                    db.rollback()

                    job = (
                        crawl_job_repository
                        .get_crawl_by_job_id(
                            db,
                            job_id,
                        )
                    )

                    total_errors += 1

                    crawl_log_repository.create_log(
                        db,
                        message=(
                            "Crawl failed for "
                            f"{source_name}"
                        ),
                        log_level="error",
                        source=source_name,
                        crawl_job_id=job.id,
                    )

            job = (
                crawl_job_repository
                .get_crawl_by_job_id(db, job_id)
            )

            if job is None or job.status == "stopped":
                return

            progress = int(
                source_number
                / source_count
                * 100
            )

            crawl_job_repository.update_crawl_progress(
                db=db,
                job=job,
                progress=progress,
                pages_visited=total_pages,
                records_extracted=total_records,
                error_count=total_errors,
            )

        job = (
            crawl_job_repository
            .get_crawl_by_job_id(db, job_id)
        )

        if job is None or job.status == "stopped":
            return

        crawl_job_repository.complete_crawl(
            db=db,
            job=job,
            pages_visited=total_pages,
            records_extracted=total_records,
            error_count=total_errors,
        )

    except Exception:
        db.rollback()

        job = (
            crawl_job_repository
            .get_crawl_by_job_id(db, job_id)
        )

        if job is not None:
            crawl_job_repository.fail_crawl(
                db,
                job,
            )

            crawl_log_repository.create_log(
                db,
                message="Crawl job failed",
                log_level="error",
                source="crawler",
                crawl_job_id=job.id,
            )

    finally:
        db.close()
