// タブに対してイベントを付与
const tabs = document.getElementsByClassName('tab');
for (let i=0;i<tabs.length;i++) {
    tabs[i].addEventListener('click', tabSwitch, false);
}

function tabSwitch() {
    // タブのclass値を変更
    document.getElementsByClassName('is-active')[0].classList.remove('is-active');
    this.classList.add('is-active');
    // コンテンツのclass値を変更
    document.getElementsByClassName('is-show')[0].classList.remove('is-show');
    const arrayTabs = Array.prototype.slice.call(tabs);
    // クリックしタブのインデックスを取得
    const index = arrayTabs.indexOf(this);
    document.getElementsByClassName('panel')[index].classList.add('is-show');
}
