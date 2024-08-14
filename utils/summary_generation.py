import requests
from transformers import pipeline

def get_summary_from_google_books(query):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "items" in data and len(data["items"]) > 0:
            book_data = data["items"][0]["volumeInfo"]
            return book_data.get("description", None)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching summary from Google Books: {e}")

    return None


def get_summary_from_open_library(query):
    url = f"http://openlibrary.org/search.json?q={query}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "docs" in data and len(data["docs"]) > 0:
            book_data = data["docs"][0]
            return book_data.get('first_sentence', {}).get('value', None)


    except requests.exceptions.RequestException as e:
        print(f"Error fetching summary from Open Library: {e}")

    return None


def get_summaries(title, author):
    query = f"{title} {author}".replace(' ', '+')

    # Fetch data from Google Books API
    google_books_summary = get_summary_from_google_books(query)
    #print(google_books_summary)

    # Fetch data from Open Library API
    open_library_summary = get_summary_from_open_library(query)
    #print(open_library_summary)

    return (google_books_summary, open_library_summary)


def get_summary(title, author):
    google_books_summary, open_library_summary = get_summaries(title, author)

    if not google_books_summary and not open_library_summary:
        return None

    combined_summary = f"Google Books Summary: {google_books_summary}\nOpen Library Summary: {open_library_summary}"
    summarizer = pipeline("summarization", model="t5-small")
    summary = summarizer(combined_summary, max_length=300, min_length=30, do_sample=False)

    print(combined_summary)
    print(summary[0]['summary_text'])
    return summary[0]['summary_text']