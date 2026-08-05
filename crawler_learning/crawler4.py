import httpx,json
from bs4 import BeautifulSoup

url = "https://quotes.toscrape.com/" #taranan 
base_url = "https://quotes.toscrape.com" #next için 

data = []

max_page = 3
page_count = 0

while url and page_count < max_page:
    print(f"taraniyor : {url}")
    
    response= httpx.get(url)
    soup = BeautifulSoup(response.text,"html.parser")
    
    quotes = soup.find_all("div",class_="quote")
    
    for quote in quotes:
        text = quote.find("span",class_="text").text
        author = quote.find("small",class_="author").text
        tags= [tag.text for tag in quote.find_all("a",class_="tag")]
        
        quote_data = {
            "text" : text,
            "author": author,
            "tags" : tags
        } 
        
        data.append(quote_data)
        
    page_count += 1 
    
    next_button = soup.find("li",class_="next")
    
    if next_button:
        next_href= soup.find("a")["href"] # a etiketini bulur -- a öelliğinin href attribute u alınır
        url = base_url + next_href
    else : 
        url = None
        
print(f"\n taranan sayfa sayisi : {page_count}, alinti sayisi : len{data}")

with open("output4","w",encoding="utf-8") as file:
    json.dump(data,file,ensure_ascii=False,indent=4)
    
print(data)