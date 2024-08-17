# app.py
from flask import Flask, request, jsonify, render_template
import sqlite3
from utils.summary_keywords_generation import get_summary_keywords

app = Flask(__name__)
db_path = "./database/books.db"


def connect_db():
    return sqlite3.connect(db_path)


def generate_summary_keywords(title, author):
    if not title or not author:
        return None

    summary, keywords = get_summary_keywords(title, author)
    return summary, keywords


@app.route('/api/generate_summary_keywords/<int:id>', methods=['POST'])
def generate_summary_keywords_for_book(id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT title, author FROM books WHERE id = ?", (id,))
    book = c.fetchone()

    if not book:
        conn.close()
        return jsonify({'error': 'Book not found'}), 404

    title, author = book
    summary, keywords = generate_summary_keywords(title, author)

    if not summary:
        conn.close()
        return jsonify({'error': 'Failed to generate summary'}), 500

    if not keywords:
        conn.close()
        return jsonify({'error': 'Failed to generate keywords'}), 500

    c.execute("UPDATE books SET summary = ? WHERE id = ?", (summary, id))
    conn.commit()


    c.execute("UPDATE books SET tags = ? WHERE id = ?", (keywords, id))
    conn.commit()

    conn.close()

    return jsonify({'summary': summary, 'keywords': keywords})


@app.route('/api/books', methods=['GET'])
def get_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page
    search_query = request.args.get('search', '')

    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')

    base_query = "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR year LIKE ?"
    sort_query = f"ORDER BY {sort_by} {sort_order.upper()} LIMIT ? OFFSET ?"
    full_query = f"{base_query} {sort_query}"

    conn = connect_db()
    c = conn.cursor()

    if search_query:
        search_query = f"%{search_query}%"
        c.execute(full_query, (search_query, search_query, search_query, per_page, offset))
    else:
        c.execute(full_query, ('%', '%', '%', per_page, offset))

    books = c.fetchall()

    c.execute("SELECT COUNT(*) FROM books WHERE title LIKE ? OR author LIKE ? OR year LIKE ?",
              (search_query, search_query, search_query) if search_query else ('%', '%', '%'))
    total_books = c.fetchone()[0]

    conn.close()

    return jsonify({
        'books': books,
        'total_books': total_books,
        'page': page,
        'per_page': per_page
    })


@app.route('/api/books/<int:id>', methods=['GET'])
def get_book(id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE id = ?", (id,))
    book = c.fetchone()
    conn.close()

    if book:
        return jsonify({
            'id': book[0],
            'title': book[1],
            'author': book[2],
            'year': book[3],
            'price': book[4],
            'tags': book[5],
            'summary': book[6]

        })
    else:
        return jsonify({'error': 'Book not found'}), 404


@app.route('/api/books', methods=['POST'])
def create_book():
    new_book = request.get_json()
    title = new_book['title']
    author = new_book['author']
    year = new_book['year']
    price = new_book['price']


    conn = connect_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO books (title, author, year, price) VALUES (?, ?, ?, ?)",
                  (title, author, year, price))
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Book already exists'}), 400

    conn.commit()
    conn.close()
    return jsonify(new_book), 201


@app.route('/api/books/<int:id>', methods=['PUT'])
def update_book(id):
    updated_book = request.get_json()
    title = updated_book['title']
    author = updated_book['author']
    year = updated_book['year']
    price = updated_book['price']

    conn = connect_db()
    c = conn.cursor()
    c.execute("UPDATE books SET title = ?, author = ?, year = ?, price = ? WHERE id = ?",
              (title, author, year, price, id))
    conn.commit()
    conn.close()
    return jsonify(updated_book)


@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return '', 204


@app.route('/book_details')
def book_details():
    return render_template('book_details.html')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
