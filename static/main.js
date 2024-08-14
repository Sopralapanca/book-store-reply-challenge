let currentPage = 1;

function loadBooks(page = 1, query = '') {

    const searchQuery = query ? `&search=${query}` : '';

    fetch(`/api/books?page=${page}${searchQuery}`)
        .then(response => response.json())
        .then(data => {
            const table = document.getElementById('books-table');
            table.innerHTML = '';
            data.books.forEach(book => {
                const row = `<tr onclick="viewBook(${book[0]})">
                                <td>${book[0]}</td>
                                <td>${book[1]}</td>
                                <td>${book[2]}</td>
                                <td>${book[3]}</td>
                                <td>${book[4]}</td>
                                <td>
                                    <button class="btn btn-warning" onclick="editBook(${book[0]})">Edit</button>
                                    <button class="btn btn-danger" onclick="deleteBook(${book[0]})">Delete</button>
                                </td>
                            </tr>`;
                table.insertAdjacentHTML('beforeend', row);
            });

            currentPage = data.page;

            // Disable buttons if there are no more pages
            document.querySelector("#pagination button:first-child").disabled = currentPage === 1;
            document.querySelector("#pagination button:last-child").disabled = currentPage * data.per_page >= data.total_books;
        });
}

function previousPage() {
    if (currentPage > 1) {
        loadBooks(currentPage - 1, document.getElementById('search-input').value);
    }
}

function nextPage() {
    loadBooks(currentPage + 1, document.getElementById('search-input').value);
}

function searchBooks() {
    const query = document.getElementById('search-input').value;
    loadBooks(1, query);  // Start search from the first page
}

function addBook() {
    const title = prompt("Enter book title:");
    if (title === null) return;
    const author = prompt("Enter book author:");
    if (author === null) return;

    let year;
    let price;
    let currentYear = new Date().getFullYear();

    while (true){
        year = prompt("Enter publication year (e.g., 2020):");
        if (year === null) return;

        if(!Number.isInteger(parseInt(year)) || parseInt(year) < 0 || parseInt(year) > currentYear || isNaN(parseInt(year)) || !Number.isInteger(parseFloat(year))){
            alert("Invalid year. Please enter a valid year.");
        }else {
            break;
        }
    }

    while (true){
        price = prompt("Enter book price (e.g., 10.00):");
        if (price === null) return;

        if(!isNaN(price) && parseFloat(price) === price && parseFloat(price) >= 0){
            alert("Invalid price. Please enter a valid price.");
        }else {
            price = parseFloat(price).toFixed(2);
            break;
        }
    }


    const book = { title, author, year, price };

    fetch('/api/books', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(book)
    }).then( response => response.json())
        .then( data => {
            if (data.error) {
                alert(data.error);
            } else {
                loadBooks(currentPage, document.getElementById('search-input').value);
            }
        });
}

function editBook(id) {
    const title = prompt("Enter new title:");
    const author = prompt("Enter new author:");
    const year = prompt("Enter new year:");
    const price = prompt("Enter new price:");

    const book = { title, author, year, price };

    fetch(`/api/books/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(book)
    }).then(() => loadBooks(currentPage, document.getElementById('search-input').value));
}

function deleteBook(id) {
    if (confirm("Are you sure you want to delete this book?")) {
        fetch(`/api/books/${id}`, {
            method: 'DELETE'
        }).then(() => loadBooks(currentPage, document.getElementById('search-input').value));
    }
}

function viewBook(id) {
        window.location.href = `/book_details?id=${id}`;
    }

window.onload = () => loadBooks(currentPage);

// Add event listener to search input - dynamic search
document.getElementById('search-input').addEventListener('input', () => {
        searchBooks();
    });