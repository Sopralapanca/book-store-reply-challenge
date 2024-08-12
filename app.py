# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)
db_path = "./database/books.db"


def connect_db():
    return sqlite3.connect(db_path)


@app.route('/api/books', methods=['GET'])
def get_books():
    page = request.args.get('page', 1, type=int)
    per_page = 20
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


@app.route('/api/books', methods=['POST'])
def create_book():
    new_book = request.get_json()
    title = new_book['title']
    author = new_book['author']
    year = new_book['year']
    price = new_book['price']

    conn = connect_db()
    c = conn.cursor()
    c.execute("INSERT INTO books (title, author, year, price) VALUES (?, ?, ?, ?)",
              (title, author, year, price))
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


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
