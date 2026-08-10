import httpx,json,time,logging
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)

def check_robots(url):
    robots_url = url + "/robots.txt"
    
    rp = RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    
    return rp.can_fetch(
        "osint-crawler",
        url
    )


url= "https://quotes.toscrape.com/"
#url= "https://quotes.toscrape.com/xxx"

#print(check_robots(url))

def fetch_page(url):
    headers={
        "User-Agent" : "osint-crawler/1.0"
    }
    
    try:
        response = httpx.get(
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
    
    
def parse_quotes(html):
    soup = BeautifulSoup(html,"html.parser")
    quotes =soup.find_all("div",class_= "quote")
    
    data=[]
    
    for quote in quotes:
        text = quote.find("span",class_="text").text
        author = quote.find("small",class_="author").text
        tags=[tag.text for tag in quote.find_all("a",class_="tag")]
        
        quote_data = {
            "text" : text,
            "author" : author,
            "tags" : tags
        }
        
        data.append(quote_data)
    
    return data

def get_next_page(html):
    soup=BeautifulSoup(html,"html.parser")
    next_button=soup.find("li",class_="next")
    
    if next_button:
        next_url = next_button.find("a")["href"]   # /page/2/
        return "https://quotes.toscrape.com" + next_url
    return None

def get_links(html):
    soup = BeautifulSoup(html,"html.parser")
    links=soup.find_all("a")
    
    valid_links =set()
    
    
    for link in links:
        href = link.get("href")
        full_url = urljoin("https://quotes.toscrape.com/",href)
        
        
        if full_url.startswith("https://quotes.toscrape.com"):   #full_url şu adresle başlıyor mu -- domain filtresi
            valid_links.add(full_url)
    return valid_links
    
def save_json(data):

    with open("output6.json","w",encoding="utf-8") as file:
        json.dump(data,file,ensure_ascii=False,indent=4)
   
"""     
def crawl(url):
    if check_robots(url):
        print("bot urlyi ziyaret edebilir")
        html=fetch_page(url)
        
        if html:
            quotes = parse_quotes(html)
            save_json(quotes)
            print("crawler tamamlandı")
        else:
            print("bot urlyi ziyaret edemez")
"""

def crawl(url):
    
    max_urls=3
    url_count=0
    
    visited_urls = set()
    
    if check_robots(url):
        logging.info("bot urlyi ziyaret edebilir")
        
        all_quotes = []
        logging.info(f"Crawl başladı: {url}")
        
        while url and url_count <= max_urls:
            
            if url in visited_urls:
                logging.info(f"URL daha önce ziyaret edildi: {url}")
                break

            visited_urls.add(url)
            url_count += 1
            
            html = fetch_page(url)
            
            if html:
                quotes = parse_quotes(html)
                all_quotes.extend(quotes)

                logging.info(f"Sayfada {len(quotes)} veri bulundu")

                links = get_links(html)
                new_links = links - visited_urls

                if new_links:
                    url = next(iter(new_links))

                time.sleep(2)
                

            else:
                break
        
        if all_quotes:
            save_json(all_quotes)
            logging.info(f"Toplam veri: {len(all_quotes)}")
            logging.info("Crawler tamamlandı")
        else:
             logging.warning("Hiç veri bulunamadı.")    


crawl(url)

html = fetch_page(url)
links = get_links(html)
#print(links)


"""   
html = fetch_page(url)
print(get_next_page(html))
"""
    
    
 
"""   
if check_robots(url):

    print("Bot bu URL'yi ziyaret edebilir.")

    html = fetch_page(url)

    if html:

       quotes = parse_quotes(html)

    save_json(quotes)

    print("Veriler JSON dosyasına kaydedildi.")

else:
    print("Bot bu URL'yi ziyaret edemez.")

"""

"""
if check_robots(url):
    print("bot bu urlyi ziyaret edebilir")
    
    html = fetch_page(url)
    
    if html:
        print("sayfa başarıyla indirildi")
        print(html[:300])
        
else:
    ("bot bu urlyi ziyaret edemez")
"""

