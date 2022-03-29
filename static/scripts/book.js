import { alertError, alertSuccess } from './lib/alerts.js'
const $opinionForm = document.querySelector('#opinion-form');

$opinionForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget)
    const path = window.location.pathname
    console.log(formData.get('opinion'))
    console.log(formData.get('score'))
    const request = fetch(path, {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(res => {
        console.log(res)
        if(res.success) {
            alertSuccess('Opinion submitted successfully')
        } else {
            alertError(res.message)
        }
    })
    .catch(res => {
        console.log('f')
        console.log(res)
    })
})
