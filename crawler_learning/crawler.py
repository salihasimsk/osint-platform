import requests, json
from bs4 import BeautifulSoup

url = "https://www.bbc.com/news/articles/c9349yx2ydvo"
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("h1").text
    
    data = {
    "source": "BBC News",
    "title" : title

    }
    
    with open ("output.json","w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=4)
        
    
    print("json oluşturuldu")

else:
    print("hata")