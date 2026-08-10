from app.crawler.robots import RobotsChecker


checker = RobotsChecker()

url = "https://quotes.toscrape.com/"

result = checker.can_fetch(url)

print(result)