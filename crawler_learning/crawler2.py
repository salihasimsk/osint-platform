import requests, json
from bs4 import BeautifulSoup

url = "https://www.bbc.com/news/articles/c9349yx2ydvo"
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text,"html.parser")
    title = soup.find("h1").text
    
    news = []
    links = soup.find_all("a")
    
    for link in links:
        href = link.get("href")
        head = link.find("h2")
        
        if href and head:
            new={
                "title" : head.text,
                "url" : "https://www.bbc.com" + href
            }
            
            news.append(new)
        
    data ={
        "source" : "BBC News",
        "news" : news
    }
    
    with open ("output2.json","w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)
        
    
    print("json oluşturuldu")

else:
    print("hata")