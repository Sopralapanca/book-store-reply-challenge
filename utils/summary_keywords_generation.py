import requests
from transformers import pipeline
import spacy
import re


def get_info_from_google_books(title, author):
    print("Getting info from Google Books")
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title}+inauthor:{author}"
    info = {}

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "items" in data and len(data["items"]) > 0:
            book_data = data["items"][0]["volumeInfo"]
            description = book_data.get("description", None)
            categories = book_data.get("categories", None)

            info["description"] = description
            info["categories"] = categories

            return info

    except requests.exceptions.RequestException as e:
        print(f"Error fetching summary from Google Books: {e}")

    return None


# def get_summary_from_open_library(query):
#     url = f"http://openlibrary.org/search.json?q={query}"
#
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json()
#
#         if "docs" in data and len(data["docs"]) > 0:
#             book_data = data["docs"][0]
#             return book_data.get('first_sentence', {}).get('value', None)
#
#
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching summary from Open Library: {e}")
#
#     return None


def get_info(title, author):
    title = title.replace(' ', '+')
    author = author.replace(' ', '+')

    # Fetch data from Google Books API
    google_books_summary = get_info_from_google_books(title, author)
    #print(google_books_summary)

    # Fetch data from Open Library API
    #open_library_summary = get_summary_from_open_library(query)
    #print(open_library_summary)

    return google_books_summary


def summarize_text(text: str) -> str:
    # preprocess the text
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    overlap = 50
    min_length = 50

    summarizer = pipeline("summarization", model="lxyuan/distilbart-finetuned-summarization")

    #summarize the text in chunks if it is too long
    inputs = summarizer.tokenizer(text, return_tensors="pt",
                                  truncation=False)  # if sequence length is too long it will return a waring, can be ignored
    input_ids = inputs['input_ids'][0]

    # total number of tokens
    total_tokens = input_ids.size(0)
    window_size = min(300, total_tokens)
    max_length = min(150, window_size // 2)

    # Set the stride based on window size and overlap
    stride = window_size - overlap

    summaries = []

    # Slide through the text using the window size and stride
    for i in range(0, total_tokens, stride):
        chunk_ids = input_ids[i:i + window_size]


        print(f"Processing chunk: {i}:{i + window_size} of {total_tokens} tokens")

        if chunk_ids.size(0) == 0:
            break

        chunk_text = summarizer.tokenizer.decode(chunk_ids, skip_special_tokens=True)

        # Generate a summary for the current chunk
        chunk_summary = summarizer(chunk_text, max_length=max_length, min_length=min_length, do_sample=False)
        summaries.append(chunk_summary[0]['summary_text'])

        # Break if the window is smaller than expected (last chunk)
        if chunk_ids.size(0) < window_size:
            break

    # Combine all summaries into a final summary
    combined_summary = " ".join(summaries)
    final_summary = summarizer(combined_summary, max_length=max_length, min_length=min_length, do_sample=False)

    return final_summary[0]['summary_text']


def extract_keywords(text: str) -> str:
    print("Extracting keywords")
    text = re.sub(r'[\s\r\n\t]+', ' ', text).strip()

    # remove stopwords
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    # Remove stopwords
    filtered_words = [token.text for token in doc if not token.is_stop]

    # Join the words back into a string
    doc = ' '.join(filtered_words)
    doc = nlp(doc)

    # extract entities
    s = set()
    for ent in doc.ents:
        s.add(ent.text)

    keywords = list(s)

    #for each element of the list, if it ends with a whitespace or punctuation, remove it
    for i in range(len(keywords)):
        if keywords[i][-1] in [' ', ',', '.', ':', ';', '!', '?']:
            keywords[i] = keywords[i][:-1]

    keywords_str = ', '.join(keywords)
    return keywords_str


def get_summary_keywords(title, author):
    google_books_summary = get_info(title, author)

    if not google_books_summary:
        return None, None

    description = google_books_summary.get("description", None)
    categories = google_books_summary.get("categories", None)
    categories = ', '.join(categories) if categories else None
    combined_summary = f"Can you provide a description of the book? {title} - {author} - {categories} - {description}"
    summary = summarize_text(combined_summary)

    combined_keywords = f"{title}, {author}, {description}"
    keywords = extract_keywords(combined_keywords)

    if categories:
        keywords = keywords + ", "+categories

    return summary, keywords
