import { alertError, alertSuccess } from './lib/alerts.js'
const $form = document.querySelector('#findBook');
const $listBook = document.querySelector('#list-books');

$form.addEventListener('submit', async(e) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget);
    const books = await getBook(formData)
    if(!books.success) {
        console.log(books)
        return alertError(books.message)
    }
    console.log(books)
    const listArray = books.data.map(book => renderTemplate(book.title, book.isbn, book.author))
    $listBook.innerHTML = '';
    $listBook.append(...listArray)
})

function renderTemplate(title, isbn, author) {
    const fragment = new DocumentFragment();
    const template = `
    <li>
        <div class="book-image">
            <img src="https://dummyimage.com/120x120.png/dddddd/000000&text=${title}" alt="${title}">
        </div>
        <div class="books-description">
            <h2>${title}</h2>
            <strong>${author}</strong>
            <p>${isbn}</p>
            <a href="/books/${isbn}">Más información</a>
        </div>
    </li>
    `
    const parse = new DOMParser().parseFromString(template, 'text/html').querySelector('li');
    fragment.appendChild(parse);

    return fragment
}

async function getBook(formData) {
    const filterBy = formData.get('filterBy');
    const find = formData.get('find');
    const response = await fetch(`/api/v1/find_books?filterBy=${filterBy}&value=${find}`);

    return await response.json();
}
