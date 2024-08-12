# db_operations.py
import sqlite3
import requests
import random
import time
from datetime import datetime
import os

db_path = "./database/books.db"

def create_db():
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER NOT NULL,
            price REAL NOT NULL,
            tags TEXT, 
            summary TEXT,
            CONSTRAINT unique_book UNIQUE (title, author, year, price)
        )
    ''')


def fetch_random_books():
    random_queries = ['python', 'history', 'science', 'fantasy', 'art',
                      'biography', 'mystery', 'technology', 'business',
                      'travel', 'music', 'food', 'health', 'sports', 'religion',
                      'self-help', 'comics', 'romance', 'horror',
                      'thriller',
                      'poetry', 'drama', 'satire', 'action', 'adventure',
                      'science-fiction', 'children', 'young-adult', 'classic',
                      'literature', 'philosophy', 'psychology', 'politics']

    book_list = set()

    for i in range(200):
        query = random.choice(random_queries)
        print(f"Fetching books for query: {query}")
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=35"
        response = requests.get(url)

        if response.status_code == 200:
            books = response.json().get('items', [])
            random.shuffle(books)

            for j in range(min(len(books), 10)):
                book = books[j]

                volume_info = book.get('volumeInfo', {})
                sale_info = book.get('saleInfo', {})

                title = volume_info.get('title', 'N/A')
                authors = ', '.join(volume_info.get('authors', ['N/A']))
                published_date = volume_info.get('publishedDate', 'N/A')

                for format in ('%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d', '%Y'):
                    try:
                        published_date = datetime.strptime(published_date, format)
                        break
                    except ValueError:
                        continue

                if isinstance(published_date, datetime):
                    published_date = published_date.year
                else:
                    continue

                list_price = sale_info.get('listPrice', {})
                price = list_price.get('amount', 'N/A')

                if price == 'N/A':
                    continue

                currency = list_price.get('currencyCode', 'N/A')

                book_list.add((title, authors, published_date, price))

                print(f"Title: {title}")
                print(f"Author(s): {authors}")
                print(f"Published Date: {published_date}")
                print(f"Price: {price} {currency}")
                print("-" * 40)

        else:
            print("Failed to fetch data")

        time.sleep(1)

    return list(book_list)


def populate_db():
    books = fetch_random_books()

    c.executemany('''
        INSERT INTO books (title, author, year, price)
        VALUES (?, ?, ?, ?)
    ''', books)


if __name__ == "__main__":
    if not os.path.exists("./database/"):
        os.makedirs("./database/")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    op = "populate"  # "populate" or "create"

    if op == "create":
        create_db()

    if op == "populate":
        populate_db()

    conn.commit()
    conn.close()
