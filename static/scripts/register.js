'use strict'
import { alertError, alertSuccess } from './lib/alerts.js'
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
        console.log(res);
        if(res.success) {
            alertSuccess('Cuenta creada :D');
            location.href = '/';
        } else {
            alertError(res.message);
        }
    })
    .catch(res => {
        alertError('Error al crear la cuenta');
        console.log(res);
    })
})
