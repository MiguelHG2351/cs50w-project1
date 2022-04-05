import { alertError, alertSuccess } from './lib/alerts.js'
const $opinionForm = document.querySelector('#opinion-form');

window.addEventListener('load', () => {
    const starContainer = document.querySelector('#star-container');
    const star = window.star
    const starImage = rankedStar(star);
    starContainer.append(...starImage);
})

function isDecimal(n) {
    return Number(n) === n && n % 1 !== 0;
}

// si es decimal, entonces, se redondea a la derecha y se agrega una estrella a la mitad

function rankedStar(star_count) {
    const startImage = []
    if(isDecimal(star_count)) {
        const newRank = Math.round(star_count);
        for(let i = 0; i < newRank; i++) {
            const image = document.createElement('img');
            if(i === newRank - 1) {
                image.setAttribute('src', '/static/images/Star_medium.svg');
            } else {
                image.setAttribute('src', '/static/images/Star.svg');
            }
            startImage.push(image);
        }
    } else {
        for(let i = 0; i < star_count; i++) {
            const image = document.createElement('img');
            image.setAttribute('src', '/static/images/Star.svg');
            startImage.push(image);
        }
    }
    return startImage;
}

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
            $opinionForm.reset()
        }
    })
    .catch(res => {
        console.log('f')
        console.log(res)
    })
})
