import time

from app.crawler.engine import CrawlerEngine


crawler = CrawlerEngine(request_delay_seconds=2)

start = time.time()

html1 = crawler.fetch_page("https://example.com")
print("İlk request tamamlandı.")

html2 = crawler.fetch_page("https://example.com")
print("İkinci request tamamlandı.")

end = time.time()

print(f"Toplam süre: {end - start:.2f} saniye")