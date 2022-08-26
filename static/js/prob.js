const elm_body = document.querySelector('body');
const tag_h1 = document.createElement('h1');
tag_h1.classList.add('h1-sample');

elm_body.append(tag_h1.cloneNode());

const elm_h1 = document.querySelector('.h1-sample');
elm_h1.innerHTML = '{{ abc }}';
