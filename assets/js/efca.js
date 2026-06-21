/* =============================================================================
   efca.js — JS vanilla minimal pour efoilcotedazur.fr
   Aucune dépendance. Chargé en `defer` (non bloquant).
   Rôles : 1) carrousel d'avis  2) animations de révélation  3) année footer
           4) hook tracking des CTA (data-efca-cta).
   La FAQ utilise <details> natif → aucun JS requis.
   ============================================================================= */
(function () {
  "use strict";

  /* --- 1. Carrousel d'avis : défile la piste scroll-snap ------------------- */
  var track = document.getElementById("efca-reviews-track");
  if (track) {
    var step = function () {
      var first = track.querySelector(".efca-review");
      // largeur d'une carte + gap (fallback 320px)
      return first ? first.getBoundingClientRect().width + 20 : 320;
    };
    document.querySelectorAll("[data-efca-reviews]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var dir = btn.getAttribute("data-efca-reviews") === "next" ? 1 : -1;
        track.scrollBy({ left: dir * step(), behavior: "smooth" });
      });
    });
  }

  /* --- 2. Révélation au scroll (respecte prefers-reduced-motion) ----------- */
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var reveals = document.querySelectorAll(".efca-reveal");
  if (reduce || !("IntersectionObserver" in window)) {
    reveals.forEach(function (el) { el.classList.add("is-visible"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -10% 0px", threshold: 0.1 });
    reveals.forEach(function (el) { io.observe(el); });
  }

  /* --- 3. Année courante dans le footer ------------------------------------ */
  var year = document.getElementById("efca-year");
  if (year) { year.textContent = String(new Date().getFullYear()); }

  /* --- 4. Hook tracking des CTA (à brancher sur GA4/Matomo plus tard) ------- */
  document.querySelectorAll("[data-efca-cta]").forEach(function (cta) {
    cta.addEventListener("click", function () {
      var id = cta.getAttribute("data-efca-cta");
      // window.dataLayer && window.dataLayer.push({ event: "cta_reserver", cta_id: id });
      if (window.console) { console.debug("[EFCA] CTA cliqué:", id); }
    });
  });

  /* Les 2 versions couleur sont des fichiers distincts (index.html / index-bleu.html),
     reliés par un bandeau de liens. Pas de toggle JS. */
})();
