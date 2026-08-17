import httpx
from app.crawler.parsers.cert_parser import CertParser

url = "https://www.kb.cert.org/vuls/bypublished/desc/"
headers = {"User-Agent": "Mozilla/5.0 (compatible; osint-crawler/1.0)"}

response = httpx.get(url, headers=headers, timeout=10, follow_redirects=True)
html = response.text

parser = CertParser()
results = parser.parse(html, url)

print(f"Number of notes found: {len(results)}\n")
for r in results[:5]:
    print(f"Title: {r['title']}")
    print(f"Date: {r['publication_date']}")
    print(f"URL: {r['url']}")
    print("-" * 50)
