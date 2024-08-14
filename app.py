# app.py
from flask import Flask, request, jsonify, render_template
import sqlite3
from utils.summary_generation import get_summary

app = Flask(__name__)
db_path = "./database/books.db"


def connect_db():
    return sqlite3.connect(db_path)


def generate_summary(title, author):
    if not title or not author:
        return None

    summary = get_summary(title, author)
    return summary


@app.route('/api/generate_summary/<int:id>', methods=['POST'])
def generate_summary_for_book(id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT title, author FROM books WHERE id = ?", (id,))
    book = c.fetchone()

    if not book:
        conn.close()
        return jsonify({'error': 'Book not found'}), 404

    title, author = book
    summary = generate_summary(title, author)

    if not summary:
        conn.close()
        return jsonify({'error': 'Failed to generate summary'}), 500

    c.execute("UPDATE books SET summary = ? WHERE id = ?", (summary, id))
    conn.commit()
    conn.close()

    return jsonify({'summary': summary})


@app.route('/api/books', methods=['GET'])
def get_books():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    search_query = request.args.get('search', '')

    conn = connect_db()
    c = conn.cursor()

    if search_query:
        search_query = f"%{search_query}%"
        c.execute("""SELECT * FROM books 
                     WHERE title LIKE ? OR author LIKE ? OR year LIKE ? 
                     LIMIT ? OFFSET ?""", (search_query, search_query, search_query, per_page, offset))
    else:
        c.execute("SELECT * FROM books LIMIT ? OFFSET ?", (per_page, offset))

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

    print("price", price)

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
