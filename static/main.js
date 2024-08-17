let currentPage = 1;
let currentSortColumn = 'id';
let currentSortOrder = 'asc';

function loadBooks(page = 1, query = '') {

    const searchQuery = query ? `&search=${query}` : '';
    const url = `/api/books?page=${page}${searchQuery}&sort_by=${currentSortColumn}&sort_order=${currentSortOrder}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const table = document.getElementById('books-table');
            table.innerHTML = '';
            data.books.forEach(book => {
                const row = `<tr>
                                <td onclick="viewBook(${book[0]})">${book[0]}</td>
                                <td onclick="viewBook(${book[0]})">${book[1]}</td>
                                <td onclick="viewBook(${book[0]})">${book[2]}</td>
                                <td onclick="viewBook(${book[0]})">${book[3]}</td>
                                <td onclick="viewBook(${book[0]})">${book[4]}</td>
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


function sortTable(column) {
    // Toggle dell'ordine di ordinamento se la stessa colonna viene cliccata
    if (currentSortColumn === column) {
        currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
    } else {
        currentSortColumn = column;
        currentSortOrder = 'asc';  // Resetta a ascendente quando cambi colonna
    }

    updateSortIcons();
    loadBooks();  // Ricarica i libri con il nuovo ordinamento
}



function updateSortIcons() {
    const columns = ['id', 'title', 'author', 'year', 'price'];

    columns.forEach(col => {
        const iconElement = document.getElementById(`sort-icon-${col}`);
        if (col === currentSortColumn) {
            if (currentSortOrder === 'asc') {
                iconElement.innerHTML = '&#9650;';  // Freccia verso l'alto
            } else {
                iconElement.innerHTML = '&#9660;';  // Freccia verso il basso
            }
        } else {
            iconElement.innerHTML = '&#9651;';  // freccia bidirezionale
        }
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

function bookChecks(){
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

        if (!isNaN(price) && price.trim() !== "" && parseFloat(price) === price && parseFloat(price) >= 0) {
            price = parseFloat(price).toFixed(2);
            break;
        } else {
            alert("Invalid price. Please enter a valid price.");
        }
    }


    const book = { title, author, year, price };

    return book;
}


function addBook() {
    let book = bookChecks();

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

    let book = bookChecks();

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

//window.onload = () => loadBooks(currentPage);


document.addEventListener('DOMContentLoaded', () => {
    updateSortIcons();  // Imposta la freccia predefinita
    loadBooks(currentPage);  // Carica i libri
});

// Add event listener to search input - dynamic search
document.getElementById('search-input').addEventListener('input', () => {
        searchBooks();
    });