// format的な関数

function fmt(template, values) {
    return !values
    ? template
    : new Function(...Object.keys(values), `return \`${template}\`;`)(...Object.values(values).map(value => value ?? ''));
}

///////////////////////
// アイコンのアニメーション //
//////////////////////

const bracketAnimation = anime.timeline({
    targets: '.bracketIcon', 
    easing: 'easeInOutSine', 
    delay: anime.stagger(1000), 
    // loop: true, 
    autoplay: false
}).add({
    duration: 400, 
    opacity: 1, 
    delay: anime.stagger(300)
}).add({
    targets: '.wrapper-hitIcon-img', 
    opacity: 1, 
    duration: 100
}).add({
    targets: '.wrapper-hitIcon-img', 
    scale: .8, 
    rotate: 20, 
    duration: 300
}).add({
    targets: '.wrapper-hitIcon-img', 
    scale: 1.2, 
    rotate: -20, 
    duration: 300
}).add({
    targets: '.wrapper-hitIcon-img', 
    scale: .8, 
    rotate: 20, 
    duration: 300
}).add({
    targets: '.wrapper-hitIcon-img', 
    scale: 1, 
    rotate: 0, 
    duration: 300
});

// スクロールしたらアニメーション開始

let appearIconSignal = false;

$(document).scroll(function() {
    var elmPos = $('.wrapper-orderOfArriveIcon').offset().top;
    var scroll = $(window).scrollTop();
    var windowHeight = $(window).height();

    if (scroll + windowHeight >= elmPos - 50 && appearIconSignal == false) {
        bracketAnimation.play();
        appearIconSignal = true;
    }
});
