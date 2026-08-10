import httpx, json, time, logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = "https://books.toscrape.com/index.html"

max_pages = 3

def fetch_page(url):
    headers = {
        "User-Agent": "osint-crawler/1.0"
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


def parse_books(html, current_url):
    soup = BeautifulSoup(html, "html.parser")

    books = soup.find_all("article", class_="product_pod")
    data = []

    for book in books:
        title = book.find("h3").find("a")["title"]
        price = book.find("p", class_="price_color").text
        stock = book.find("p", class_="instock").text.strip()
        rating = book.find("p", class_="star-rating")["class"][1]

        book_url = urljoin(
            current_url,
            book.find("h3").find("a")["href"]
        )

        book_data = {
            "title": title,
            "price": price,
            "stock": stock,
            "rating": rating,
            "book_url": book_url
        }

        data.append(book_data)

    return data


def get_next_page(html, current_url):
    soup = BeautifulSoup(html, "html.parser")

    next_button = soup.find("li", class_="next")

    if next_button:
        next_url = next_button.find("a")["href"]
        return urljoin(current_url, next_url)

    return None


def crawler(start_url, max_pages):
    url = start_url
    page = 1
    all_books = []
    visited_urls = set()

    while url and page <= max_pages:

        if url in visited_urls:
            break

        visited_urls.add(url)

        html = fetch_page(url)

        if html:
            books = parse_books(html, url)
            all_books.extend(books)

            url = get_next_page(html, url)

            page += 1

        else:
            break

    return all_books


all_books = crawler(url, max_pages)

with open("output7.json", "w", encoding="utf-8") as file:
    json.dump(all_books, file, ensure_ascii=False, indent=4)