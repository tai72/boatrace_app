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

// レスポンシブ、クラスの切り替え

// ページ開いた時
$(document).ready(function() {
    var x = $(window).width();
    var breakPoint = 768;
    if (x <= breakPoint) {
        $('.card-container').addClass('disp-none');
    } else {
        $('.card-container-responsive').addClass('disp-none');
        $('#second-first-view').addClass('disp-none');
    }
});

// リサイズしてリロードしたとき
$(window).on('resize orientationchange', function() {
    var x = $(window).width();
    var breakPoint = 768;
    if (x <= breakPoint) {
        $('.card-container').addClass('disp-none');
        $('.card-container-responsive').removeClass('disp-none');
        $('#second-first-view').removeClass('disp-none');
    } else {
        $('.card-container').removeClass('disp-none');
        $('.card-container-responsive').addClass('disp-none');
        $('#second-first-view').addClass('disp-none');
    }
});

/////////////
// ヘッダー  //
/////////////

// ハンバーガーメニュー

$('.nav-toggle').on('click', function() {
    $('.nav-toggle, .nav-humburger').toggleClass('show');    // showというクラスを付与する.
    $('.wrapper-appear-detailIcon').toggleClass('disp-none');
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

///////////////////
// ローディング部分  //
///////////////////

window.onload = function() {
    document.getElementById('loading-display').classList.add('disp-none');
}

/////////////
// about   //
/////////////

// 順に表示

const appearAboutContent = anime.timeline({
    targets: '.card', 
    easing: 'easeInOutSine', 
    delay: anime.stagger(200), 
    autoplay: false
})
.add({
    opacity: [0, 1], 
    delay: anime.stagger(100), 
    duration: 500, 
});

let appearAboutContentSignal = false;
$(document).scroll(function() {
    var scroll = $(window).scrollTop();
    var elmPos = $('.card-container').offset().top;
    var windowHeight = $(window).height();

    if (scroll+windowHeight >= elmPos+200 && appearAboutContentSignal == false) {
        appearAboutContent.play();
        appearAboutContentSignal = true;
    }
});

// クリックしたら詳細表示

$('.appear-detailIcon').on('click', function() {
    var index = $('.appear-detailIcon').index($(this));

    $('.card-container-responsive .card .face.face2').eq(index).toggleClass('appear-about-detail');
    $('.wrapper-appear-detailIcon').eq(index).toggleClass('rotate-90deg');
});

////////////////////
// whatIsBoatrace //
///////////////////

const appearWhatIsBoatraceContent = anime.timeline({
    targets: '.boatrace-content', 
    easing: 'easeInOutSine', 
    delay: anime.stagger(200), 
    autoplay: false
})
.add({
    opacity: [0, 1], 
    delay: anime.stagger(100), 
    duration: 500, 
});

let appearWhatIsBoatraceContentSignal = false;
$(document).scroll(function() {
    var scroll = $(window).scrollTop();
    var elmPos = $('.wrapper-boatrace-content').offset().top;
    var windowHeight = $(window).height();

    if (scroll+windowHeight >= elmPos+200 && appearWhatIsBoatraceContentSignal == false) {
        appearWhatIsBoatraceContent.play();
        appearWhatIsBoatraceContentSignal = true;
    }
});
