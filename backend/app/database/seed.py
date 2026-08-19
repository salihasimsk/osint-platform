from app.database.database import SessionLocal
from app.models.source import Source


DEFAULT_SOURCES = [
    {
        "name": "Ubuntu Security Notices",
        "base_url": "https://ubuntu.com/security/notices",
        "enabled_status": True,
        "request_delay": 2,
    },
    {
        "name": "CERT/CC Vulnerability Notes",
        "base_url": "https://www.kb.cert.org/vuls/bypublished/desc/",
        "enabled_status": True,
        "request_delay": 2,
    },
    {
        "name": "CISA Known Exploited Vulnerabilities",
        "base_url": "https://raw.githubusercontent.com/cisagov/kev-data/develop/known_exploited_vulnerabilities.json",
        "enabled_status": True,
        "request_delay": 2,
    },
    {
        "name": "NVD CVE Database",
        "base_url": "https://services.nvd.nist.gov/rest/json/cves/2.0",
        "enabled_status": True,
        "request_delay": 6,
    },
    {
        "name": "Red Hat Security Data",
        "base_url": "https://access.redhat.com/hydra/rest/securitydata/cve.json",
        "enabled_status": True,
        "request_delay": 2,
    },
]


def seed_sources():
    db = SessionLocal()

    try:
        for source_data in DEFAULT_SOURCES:
            existing_source = (
                db.query(Source)
                .filter(Source.base_url == source_data["base_url"])
                .first()
            )

            if existing_source is None:
                db.add(Source(**source_data))

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()