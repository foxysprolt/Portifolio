// Assim que a página carregar 100%
window.addEventListener('load', () => {
    setTimeout(() => {
        document.body.classList.remove('loading');
    }, 500); // 0.5 segundos parado no centro e depois sobe
});

// Código do scroll (não mexa, esse está bom)
window.onscroll = function() {
    const header = document.querySelector(".header-melin");
    if (window.scrollY > 20) {
        header.classList.add("rolagem");
    } else {
        header.classList.remove("rolagem");
    }
};