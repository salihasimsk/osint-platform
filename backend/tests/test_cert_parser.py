from datetime import datetime

from app.crawler.parsers.cert_parser import CertParser


SAMPLE_HTML = """
<html>
    <body>
        <table>
            <tbody>
                <tr>
                    <td>2026-08-11</td>
                    <td>2026-08-11</td>
                    <td>2026-08-12</td>
                    <td>VU#431093</td>
                    <td></td>
                    <td>
                        <a href="/vuls/id/431093">
                            Example CERT vulnerability
                        </a>
                    </td>
                </tr>
            </tbody>
        </table>

        <a rel="next" href="/vuls/bypublished/desc/2">
            Next
        </a>
    </body>
</html>
"""


def test_parse():
    parser = CertParser()

    results = parser.parse(
        SAMPLE_HTML,
        "https://www.kb.cert.org/vuls/bypublished/desc/",
    )

    assert len(results) == 1

    notice = results[0]

    assert notice["title"] == (
        "VU#431093: Example CERT vulnerability"
    )
    assert notice["url"] == (
        "https://www.kb.cert.org/vuls/id/431093"
    )
    assert notice["publication_date"] == datetime(2026, 8, 11)
    assert notice["organization"] == "CERT/CC"
    assert notice["source_domain"] == "kb.cert.org"


def test_get_next_page():
    parser = CertParser()

    next_page = parser.get_next_page(
        SAMPLE_HTML,
        "https://www.kb.cert.org/vuls/bypublished/desc/",
    )

    assert next_page == (
        "https://www.kb.cert.org/vuls/bypublished/desc/2"
    )


def test_parse_detail():
    parser = CertParser()

    detail_html = """
    <html>
        <body>
            <a href="https://www.cve.org/CVERecord?id=CVE-2026-1234">
                CVE-2026-1234
            </a>
        </body>
    </html>
    """

    result = parser.parse_detail(detail_html)

    assert result["cve"] == "CVE-2026-1234"
