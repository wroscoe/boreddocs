// Chevron rotation handled in CSS via [open] selector — keeping a small JS hook
// in case future enhancements (search, deep-link expand) need it.
(function () {
  const sections = document.querySelectorAll(".agenda-outline details");
  if (!sections.length) return;

  // Expand the section that matches a deep-link (e.g. #section-3-A) on load.
  const hash = window.location.hash;
  if (hash && hash.length > 1) {
    const target = document.getElementById(hash.slice(1));
    if (target) {
      let el = target;
      while (el && el !== document.body) {
        if (el.tagName === "DETAILS") el.open = true;
        el = el.parentElement;
      }
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }
})();
