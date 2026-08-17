from app.crawler.engine import CrawlerEngine
from app.crawler.parsers.cisa_kev_parser import CisaKevParser


SOURCE_URL = (
    "https://raw.githubusercontent.com/"
    "cisagov/kev-data/develop/"
    "known_exploited_vulnerabilities.json"
)


engine = CrawlerEngine(request_delay=2)
parser = CisaKevParser()

records = engine.crawl(
    SOURCE_URL,
    parser,
    max_pages=1,
)

print("Bulunan kayıt sayısı:", len(records))

if records:
    print("İlk kayıt:")
    print(records[0])
