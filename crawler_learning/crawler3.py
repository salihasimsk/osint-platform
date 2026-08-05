import requests,json
from bs4 import BeautifulSoup

url = "https://quotes.toscrape.com/"

response = requests.get(url) # istek gönderildi

print(response.status_code) # istek gönderildi (200 basarili)
soup = BeautifulSoup(response.text,"html.parser") # html parse edilir

quotes = soup.find_all("div",class_="quote") # quotes classına sahip quote divleri
data = []

for quote in quotes:
    text = quote.find("span",class_="text").text 
    author = quote.find("small",class_="author").text
    tags = [tag.text for tag in quote.find_all("a",class_="tag")]
    
    quote_data = {
    "text": text,
    "author":author,
    "tags":tags
   }

    data.append(quote_data)

with open("output3.json","w",encoding="utf-8") as file:
    json.dump(data,file,ensure_ascii=False,indent=4)
      
print(data)