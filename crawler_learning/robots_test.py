from urllib import response
from urllib.robotparser import RobotFileParser
import httpx


"""
url = "https://quotes.toscrape.com/robots.txt"

rp = RobotFileParser() #robpts okuyucu nesnesi oluşturulur
rp.set_url(url)
rp.read() #istek atıyor

print(rp.can_fetch("*", "https://quotes.toscrape.com/login")) #bot bu url yi ziyaret edebilir mi

print(
    rp.can_fetch(
        "*",
        "https://quotes.toscrape.com/admin"
    )
)

"""


def check_robots(url):
    robots_url = url + "/robots.txt"
    
    rp = RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    
    return rp.can_fetch(
        "OSINT-Crawler",
        url
    )

url = "https://quotes.toscrape.com/"

if check_robots(url):
    print("bot bu url yi ziyaret edebilir")
else:
    print("bot bu url yi ziyaret edemez")
    


def fetch_page(url):
    
    headers = {
        "user-agent" : "osint-crawler"
    }
    
    try:
        resğponse = httpx.get(
            url,
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        
        return response.text
    
    except httpx.TimeoutException:
        print("İstek zaman aşımına uğradı.")
        return None


    except httpx.HTTPStatusError as e:
        print(f"HTTP hatası: {e}")
        return None


    except httpx.RequestError as e:
        print(f"Bağlantı hatası: {e}")
        return None
    
    
    url = "https://quotes.toscrape.com/"

result = check_robots(url)

print(result)