'use strict'

const $form = document.querySelector('#register-form');

$form.addEventListener('submit', (e) => {
    e.preventDefault();
    const formData = new FormData($form);

    // lo elimine por que para esto habria que parsear el formData en el server
    // const username = formData.get('username');
    // const email = formData.get('email');
    // const lastname = formData.get('lastname');
    // const password = formData.get('password');

    // const user = {
    //     username,
    //     email,
    //     lastname,
    //     password
    // }

    // // objeto inmutable
    // Object.freeze(user);

    fetch('/register', {
        method: 'POST',
        body: formData,
    }).then(res => res.json())
    .then(res => {
        if(res.success) {
            location.href = '/';
        }
    })
    .catch(res => {
        if(res.success) {
            location.reload()
        }
    })
})
