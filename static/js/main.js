// format的な関数

function fmt(template, values) {
    return !values
    ? template
    : new Function(...Object.keys(values), `return \`${template}\`;`)(...Object.values(values).map(value => value ?? ''));
}

/////////////
// 共通設定 //
/////////////

// vh, vwの設定

let vh = window.innerHeight * 0.01;
let vw = window.innerWidth * 0.01;
document.documentElement.style.setProperty('--vh', `${vh}px`);
document.documentElement.style.setProperty('--vw', `${vw}px`);

// 共通変数

const breakPoint = 768;

/////////////
// ヘッダー  //
/////////////

// ハンバーガーメニュー

$('.nav-toggle').on('click', function() {
    $('.nav-toggle, .nav-humburger').toggleClass('show');    // showというクラスを付与する.
});

$(document).ready(function() {
    var x = $(window).width();
    if (x <= breakPoint) {
        $('.ul-header').addClass('disp-none');
    } else {
        $('.nav-toggle').addClass('disp-none');
    }
});

$(window).on('resize orientationchange', function() {
    var x = $(window).width();
    if (x <= breakPoint) {
        $('.ul-header').addClass('disp-none');
    } else {
        $('.nav-toggle').addClass('disp-none');
    }
});

const appearHumburgerAnimation = anime.timeline({
    targets: '.nav-menu-li', 
    easing: 'easeInOutSine', 
    delay: anime.stagger(200)
})
.add({
    opacity: [0, 1], 
    translateY: -10, 
    delay: anime.stagger(100), 
    duration: 500, 
});
$('.nav-toggle').on('click', function() {
    appearHumburgerAnimation.play();
    console.log('test');
});
