/* NUEVO LIP — motion global del shell
   Glow follower · botones magnéticos · reveal en scroll · nav activo.
   Respeta prefers-reduced-motion. No reemplaza el cursor. */
(function () {
  "use strict";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Glow follower sutil */
  var glow = document.querySelector(".glow");
  if (glow && !reduce) {
    window.addEventListener("pointermove", function (e) {
      glow.style.setProperty("--mx", e.clientX + "px");
      glow.style.setProperty("--my", e.clientY + "px");
    }, { passive: true });
  }

  /* Botones magnéticos [data-mag] */
  if (!reduce) {
    document.querySelectorAll("[data-mag]").forEach(function (btn) {
      var range = 34;
      btn.addEventListener("pointermove", function (e) {
        var r = btn.getBoundingClientRect();
        var x = (e.clientX - r.left - r.width / 2) / range;
        var y = (e.clientY - r.top - r.height / 2) / range;
        btn.style.transform = "translate(" + (x * 7) + "px," + (y * 7) + "px)";
      });
      btn.addEventListener("pointerleave", function () { btn.style.transform = ""; });
    });
  }

  /* Nav activo por path */
  document.querySelectorAll(".navbar-premium .nav-link").forEach(function (link) {
    var href = link.getAttribute("href");
    if (href && href.length > 1 && window.location.pathname.indexOf(href) === 0) {
      link.classList.add("active");
    }
  });

  /* Reveal suave [data-reveal] (IntersectionObserver, vanilla) */
  var revealEls = document.querySelectorAll("[data-reveal]");
  if (revealEls.length && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("visible"); io.unobserve(en.target); }
      });
    }, { threshold: 0.12 });
    revealEls.forEach(function (el) { el.classList.add("reveal-hide"); io.observe(el); });
  }
})();
