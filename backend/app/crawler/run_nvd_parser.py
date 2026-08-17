from app.crawler.engine import CrawlerEngine
from app.crawler.parsers.nvd_parser import NvdParser


url = (
    "https://services.nvd.nist.gov/"
    "rest/json/cves/2.0?resultsPerPage=10"
)

parser = NvdParser()
engine = CrawlerEngine(request_delay=2)

results = engine.crawl(
    url,
    parser,
    max_pages=1,
)

print(f"Bulunan kayıt sayısı: {len(results)}")

if results:
    print("İlk kayıt:")
    print(results[0])
