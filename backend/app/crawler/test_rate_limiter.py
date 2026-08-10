import time

from app.crawler.rate_limiter import RateLimiter


limiter = RateLimiter(2)

start = time.time()

limiter.wait()
print("İlk request")

limiter.wait()
print("İkinci request")

end = time.time()

print(f"Geçen süre: {end - start:.2f} saniye")