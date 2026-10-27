/* Schick Medical Aesthetics – kleine, abhängigkeitsfreie Interaktionen */
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.remove("no-js");

  // Mobile Navigation
  var toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // Untermenü "Leistungen"
  document.querySelectorAll(".has-sub").forEach(function (item) {
    var btn = item.querySelector("button.nav-link");
    if (!btn) return;
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = item.getAttribute("data-open") === "true";
      item.setAttribute("data-open", open ? "false" : "true");
      btn.setAttribute("aria-expanded", open ? "false" : "true");
    });
  });
  document.addEventListener("click", function (e) {
    document.querySelectorAll('.has-sub[data-open="true"]').forEach(function (item) {
      if (!item.contains(e.target) && window.innerWidth > 1100) {
        item.setAttribute("data-open", "false");
        item.querySelector("button.nav-link").setAttribute("aria-expanded", "false");
      }
    });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    document.body.classList.remove("nav-open");
    if (toggle) toggle.setAttribute("aria-expanded", "false");
    document.querySelectorAll(".has-sub").forEach(function (item) { item.setAttribute("data-open", "false"); });
  });

  // Sanftes Einblenden beim Scrollen
  var els = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    els.forEach(function (el) { io.observe(el); });
  } else {
    els.forEach(function (el) { el.classList.add("in"); });
  }

  // Terminanfrage: Behandlung aus URL vorauswählen und E-Mail erzeugen
  var form = document.getElementById("terminanfrage");
  if (form) {
    var params = new URLSearchParams(window.location.search);
    var pre = params.get("behandlung");
    var select = form.querySelector("#f-behandlung");
    if (pre && select) {
      Array.prototype.forEach.call(select.options, function (o) { if (o.value === pre) select.value = pre; });
    }
    var art = params.get("art");
    if (art) {
      var radio = form.querySelector('input[name="art"][value="' + art + '"]');
      if (radio) radio.checked = true;
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var get = function (id) { var el = form.querySelector(id); return el ? el.value.trim() : ""; };
      var artEl = form.querySelector('input[name="art"]:checked');
      var behandlung = select.options[select.selectedIndex].text;
      var lines = [
        "Guten Tag Frau Dr. Schick,",
        "",
        "ich möchte gern einen Termin anfragen.",
        "",
        "Art des Termins: " + (artEl ? artEl.getAttribute("data-label") : "-"),
        "Interesse an: " + behandlung,
        "Wunschzeitraum: " + (get("#f-zeit") || "flexibel"),
        "",
        "Name: " + get("#f-name"),
        "Telefon: " + (get("#f-tel") || "-"),
        "E-Mail: " + get("#f-mail"),
        "",
        "Nachricht:",
        get("#f-nachricht") || "-",
        "",
        "Viele Grüße",
        get("#f-name")
      ];
      var to = form.getAttribute("data-mail");
      var subject = "Terminanfrage: " + behandlung;
      window.location.href = "mailto:" + to + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(lines.join("\n"));
      var done = document.getElementById("form-done");
      if (done) done.hidden = false;
    });
  }

  // Jahr im Footer
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
