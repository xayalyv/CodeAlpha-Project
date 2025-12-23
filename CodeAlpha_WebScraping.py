import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from urllib.parse import urljoin
import os

base_url = "https://books.toscrape.com/catalogue/page-{}.html"
base_site = "https://books.toscrape.com/"

all_books = []

for page in range(1, 51):  # 50 pages
    if page == 1:
        url = base_site
    else:
        url = base_url.format(page)

    response = requests.get(url)
    response.encoding = 'utf-8'  
    soup = BeautifulSoup(response.text, "html.parser")

    books = soup.find_all("article", class_="product_pod")

    for book in books:
        title = book.h3.a["title"]

        price_text = book.find("p", class_="price_color").text
        price = float(re.sub(r'[^\d.]', '', price_text)) 

        rating = book.find("p", class_="star-rating")["class"][1]

        availability_text = book.find("p", class_="instock availability").text.strip()

        product_relative_url = book.h3.a["href"]
        product_url = urljoin(base_site + "catalogue/", product_relative_url)

        product_response = requests.get(product_url)
        product_response.encoding = 'utf-8'
        product_soup = BeautifulSoup(product_response.text, "html.parser")

        breadcrumb = product_soup.find("ul", class_="breadcrumb")
        if breadcrumb:
            category = breadcrumb.find_all("li")[2].text.strip()
        else:
            category = "Unknown"

        stock_element = product_soup.find("p", class_="instock availability")
        if stock_element:
            stock_text = stock_element.text
            stock_numbers = re.findall(r"\d+", stock_text)
            stock_count = int(stock_numbers[0]) if stock_numbers else 0
        else:
            stock_count = 0

        all_books.append([
            title,
            price,
            rating,
            availability_text,
            stock_count,
            category])

df = pd.DataFrame(
    all_books,
    columns=[
        "Title",
        "Price (£)",
        "Rating",
        "Availability",
        "Stock Count",
        "Category"]
)

print(df.head())
print(f"Total books scraped: {len(df)}")

desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "books_dataset_6_columns.csv")
df.to_csv(desktop_path, index=False)
print(f"CSV saved at: {desktop_path}")