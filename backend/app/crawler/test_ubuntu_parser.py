from app.crawler.parsers.ubuntu_parser import UbuntuParser


SAMPLE_HTML = """
<html>
    <body>
        <div id="notices-list">
            <section class="p-section--shallow">
                <div class="row">
                    <div class="col-6">
                        <h3>
                            <a href="/security/notices/USN-1234-1">
                                USN-1234-1: Example vulnerability
                            </a>
                        </h3>

                        <p class="u-text--muted">
                            12 August 2026
                        </p>

                        <p class="u-no-margin--bottom">
                            An example security issue was fixed.
                        </p>

                        <a href="/security/CVE-2026-1234">
                            CVE-2026-1234
                        </a>
                    </div>
                </div>
            </section>
        </div>

        <a
            class="p-pagination__link--next"
            href="/security/notices?page=2"
        >
            Next
        </a>
    </body>
</html>
"""


def test_parse():
    parser = UbuntuParser()

    results = parser.parse(
        SAMPLE_HTML,
        "https://ubuntu.com/security/notices",
    )

    assert len(results) == 1

    notice = results[0]

    assert notice["title"] == "USN-1234-1: Example vulnerability"
    assert notice["url"] == (
        "https://ubuntu.com/security/notices/USN-1234-1"
    )
    assert notice["publication_date"] == "12 August 2026"
    assert notice["summary"] == (
        "An example security issue was fixed."
    )
    assert notice["cve"] == "CVE-2026-1234"
    assert notice["organization"] == "Ubuntu"
    assert notice["source_domain"] == "ubuntu.com"


def test_get_next_page():
    parser = UbuntuParser()

    next_page = parser.get_next_page(
        SAMPLE_HTML,
        "https://ubuntu.com/security/notices",
    )

    assert next_page == (
        "https://ubuntu.com/security/notices?page=2"
    )