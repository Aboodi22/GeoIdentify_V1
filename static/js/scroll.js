/* Défilement doux (Lenis) + pied de page « rideau » : la page glisse et dévoile le pied de page fixé dessous. */
(function () {
    var footer = document.getElementById("site-footer");
    var page = document.querySelector(".page");
    if (!footer || !page) return;
    var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var inner = footer.querySelector(".footer-inner");

    function measure() {
        var h = footer.offsetHeight;
        page.style.marginBottom = h + "px";
        page.style.minHeight = window.innerHeight + "px";
    }
    function reveal() {
        if (!inner) return;
        var max = footer.offsetHeight;
        var left = page.getBoundingClientRect().bottom - (window.innerHeight - max); // px de pied de page encore cachés
        var p = Math.min(1, Math.max(0, left / max));
        inner.style.transform = reduced ? "none" : "translateY(" + (-p * 14).toFixed(1) + "%)";
        inner.style.opacity = reduced ? "1" : (1 - p * 0.6).toFixed(2);
    }
    measure(); reveal();
    window.addEventListener("resize", function () { measure(); reveal(); });
    window.addEventListener("load", function () { measure(); reveal(); });
    window.addEventListener("scroll", reveal, { passive: true });

    if (!reduced && window.Lenis) {
        try {
            var lenis = new Lenis({ duration: 1.15, smoothWheel: true });
            lenis.on("scroll", reveal);
            (function raf(t) { lenis.raf(t); requestAnimationFrame(raf); })(0);
        } catch (e) { /* défilement natif si Lenis échoue */ }
    }
})();
