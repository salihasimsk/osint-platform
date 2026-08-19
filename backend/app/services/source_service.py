from urllib.parse import urlparse

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import source_repository
from app.crawler.url_validator import is_safe_url


SUPPORTED_SOURCE_HOSTS = {
    "ubuntu.com",
    "www.kb.cert.org",
    "kb.cert.org",
    "raw.githubusercontent.com",
    "services.nvd.nist.gov",
    "access.redhat.com",
}


def _normalize_url(url: str) -> str:
    return url.strip()


def _validate_source_url(url: str) -> None:
    if not is_safe_url(url):
        raise HTTPException(
            status_code=400,
            detail=(
                "Source URL must be a public "
                "HTTP or HTTPS address"
            ),
        )


def _validate_supported_source(url: str) -> None:
    parsed = urlparse(url)

    hostname = (
        parsed.hostname.lower()
        if parsed.hostname
        else ""
    )

    if hostname not in SUPPORTED_SOURCE_HOSTS:
        raise HTTPException(
            status_code=400,
            detail=(
                "This source is not supported by "
                "the current crawler parsers."
            ),
        )

    # GitHub raw content is accepted only for
    # the approved CISA KEV dataset.
    if hostname == "raw.githubusercontent.com":
        if "/cisagov/kev-data/" not in parsed.path.lower():
            raise HTTPException(
                status_code=400,
                detail=(
                    "Only the approved CISA KEV "
                    "GitHub source is supported."
                ),
            )


def _validate_request_delay(
    request_delay: int,
) -> None:
    if request_delay < 1:
        raise HTTPException(
            status_code=400,
            detail=(
                "Request delay must be at least "
                "1 second."
            ),
        )

    if request_delay > 60:
        raise HTTPException(
            status_code=400,
            detail=(
                "Request delay must not exceed "
                "60 seconds."
            ),
        )


def _check_duplicate_source(
    db: Session,
    url: str,
    ignored_source_id: int | None = None,
) -> None:
    existing_source = (
        source_repository.get_source_by_base_url(
            db,
            url,
        )
    )

    if existing_source is None:
        return

    if (
        ignored_source_id is not None
        and existing_source.id == ignored_source_id
    ):
        return

    raise HTTPException(
        status_code=409,
        detail=(
            "A source with this Base URL "
            "already exists."
        ),
    )


def list_sources(db: Session):
    return source_repository.get_all_sources(db)


def get_source(
    db: Session,
    source_id: int,
):
    source = source_repository.get_source_by_id(
        db,
        source_id,
    )

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="Source not found",
        )

    return source


def create_source(
    db: Session,
    source_data,
):
    source_data.base_url = _normalize_url(
        source_data.base_url
    )

    source_data.name = source_data.name.strip()

    if not source_data.name:
        raise HTTPException(
            status_code=400,
            detail="Source name is required.",
        )

    _validate_source_url(
        source_data.base_url
    )

    _validate_supported_source(
        source_data.base_url
    )

    _validate_request_delay(
        source_data.request_delay
    )

    _check_duplicate_source(
        db,
        source_data.base_url,
    )

    return source_repository.create_source(
        db,
        source_data,
    )


def update_source(
    db: Session,
    source_id: int,
    source_data,
):
    source = source_repository.get_source_by_id(
        db,
        source_id,
    )

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="Source not found",
        )

    source_data.base_url = _normalize_url(
        source_data.base_url
    )

    source_data.name = source_data.name.strip()

    if not source_data.name:
        raise HTTPException(
            status_code=400,
            detail="Source name is required.",
        )

    _validate_source_url(
        source_data.base_url
    )

    _validate_supported_source(
        source_data.base_url
    )

    _validate_request_delay(
        source_data.request_delay
    )

    _check_duplicate_source(
        db,
        source_data.base_url,
        ignored_source_id=source_id,
    )

    return source_repository.update_source(
        db,
        source,
        source_data,
    )


def update_source_status(
    db: Session,
    source_id: int,
    enabled: bool,
):
    source = source_repository.get_source_by_id(
        db,
        source_id,
    )

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="Source not found",
        )

    return (
        source_repository.update_source_status(
            db,
            source,
            enabled,
        )
    )


def delete_source(
    db: Session,
    source_id: int,
):
    source = source_repository.get_source_by_id(
        db,
        source_id,
    )

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="Source not found",
        )

    source_repository.delete_source(
        db,
        source,
    )

    return {
        "message": "Source deleted successfully"
    }