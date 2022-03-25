const $form = document.querySelector('#findBook');

$form.addEventListener('submit', async(e) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget);
    const books = await getBook(formData)
    console.log(books)
})


async function getBook(formData) {
    const filterBy = formData.get('filterBy');
    const find = formData.get('find');
    const response = await fetch(`/api/v1/find_books?filterBy=${filterBy}&value=${find}`);

    return await response.json();
}
