import httpx

url = "https://quotes.toscrape.com/"

headers = {
    "User-Agent": "OSINT-Crawler/1.0"
}

try:

    response = httpx.get(
        url,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    print("başarılı")

except httpx.TimeoutException:
    print("İstek zaman aşımına uğradı.")

except httpx.HTTPStatusError as e:
    print(f"başarısız: {e}")

except httpx.RequestError as e:
    print(f"bağlantı hatası: {e}")
    
print(response.request.headers)

