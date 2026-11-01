/* Schick Medical Aesthetics – Online-Terminbuchung mit Kalender
 * Öffnet sich als Fenster über jeder "Termin buchen"-Schaltfläche und ist auf
 * /termin-buchen/ direkt eingebettet. Daten kommen von api/termine.php. */
(function () {
  "use strict";

  var script = document.currentScript;
  var base = script ? script.src.replace(/assets\/js\/booking\.js.*$/, "") : "/";
  var API = base + "api/termine.php";
  var CFG = window.SCHICK_BOOKING || { types: [], treatments: [], email: "" };

  var MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"];
  var WD_SHORT = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"];
  var WD_LONG = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"];

  function el(tag, attrs, children) {
    var e = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === "class") e.className = attrs[k];
      else if (k === "text") e.textContent = attrs[k];
      else if (k === "html") e.innerHTML = attrs[k];
      else if (k.slice(0, 2) === "on") e.addEventListener(k.slice(2), attrs[k]);
      else if (attrs[k] !== false && attrs[k] != null) e.setAttribute(k, attrs[k] === true ? "" : attrs[k]);
    });
    (children || []).forEach(function (c) { if (c) e.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return e;
  }
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function iso(d) { return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
  function parse(s) { var p = s.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function longDate(s) { var d = parse(s); return WD_LONG[d.getDay()] + ", " + d.getDate() + ". " + MONTHS[d.getMonth()] + " " + d.getFullYear(); }

  var cache = null;
  function load(force) {
    if (cache && !force) return cache;
    cache = fetch(API + "?action=slots", { headers: { Accept: "application/json" }, cache: "no-store" })
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .then(function (d) { if (!d.ok) throw new Error("API"); return d; })
      .catch(function (e) { cache = null; throw e; });
    return cache;
  }

  /* ---------------- Widget ---------------- */
  function Widget(root, opts) {
    this.root = root;
    this.opts = opts || {};
    this.state = { type: opts.art || "praxis", treatment: opts.behandlung || "allgemein", date: null, time: null, month: null, opened: Date.now() };
    this.render();
  }

  Widget.prototype.render = function () {
    var self = this;
    this.root.innerHTML = "";
    this.root.appendChild(el("div", { class: "bk-loading", text: "Freie Termine werden geladen …" }));
    load(this.opts.force).then(function (data) {
      self.opts.force = false;
      self.data = data;
      if (!self.state.month) {
        var first = Object.keys(data.days).filter(function (k) { return data.days[k].status === "frei"; })[0] || data.from;
        var f = parse(first);
        self.state.month = new Date(f.getFullYear(), f.getMonth(), 1);
      }
      self.step1();
    }).catch(function () { self.fallback(); });
  };

  Widget.prototype.head = function (title, step) {
    var steps = el("ol", { class: "bk-steps", "aria-label": "Fortschritt" }, ["Termin wählen", "Ihre Daten", "Bestätigung"].map(function (t, i) {
      return el("li", { class: i + 1 === step ? "is-active" : i + 1 < step ? "is-done" : "", text: t });
    }));
    return el("div", { class: "bk-head" }, [el("h2", { class: "bk-title", text: title, tabindex: "-1" }), steps]);
  };

  Widget.prototype.step1 = function () {
    var self = this, st = this.state, data = this.data;
    var r = this.root; r.innerHTML = "";
    r.appendChild(this.head("Wunschtermin wählen", 1));

    // Art des Termins
    var types = el("div", { class: "bk-types", role: "radiogroup", "aria-label": "Art des Termins" });
    (data.types || CFG.types).forEach(function (t) {
      var b = el("button", { type: "button", class: "bk-type" + (st.type === t.id ? " is-active" : ""), role: "radio", "aria-checked": st.type === t.id ? "true" : "false",
        onclick: function () { st.type = t.id; self.step1(); } }, [el("strong", { text: t.label }), el("small", { text: t.desc })]);
      types.appendChild(b);
    });
    r.appendChild(types);

    // Behandlung
    var sel = el("select", { id: "bk-treat-" + this.uid(), class: "bk-select", onchange: function () { st.treatment = this.value; } });
    CFG.treatments.forEach(function (t) { sel.appendChild(el("option", { value: t[0], text: t[1], selected: st.treatment === t[0] })); });
    r.appendChild(el("div", { class: "bk-field" }, [el("label", { for: sel.id, text: "Ich interessiere mich für" }), sel]));

    // Kalender
    var m = st.month, y = m.getFullYear(), mo = m.getMonth();
    var minM = parse(data.from), maxM = parse(data.to);
    var canPrev = new Date(y, mo, 1) > new Date(minM.getFullYear(), minM.getMonth(), 1);
    var canNext = new Date(y, mo + 1, 1) <= maxM;
    var cal = el("div", { class: "bk-cal" });
    cal.appendChild(el("div", { class: "bk-cal-head" }, [
      el("button", { type: "button", class: "bk-nav", "aria-label": "Vorheriger Monat", disabled: !canPrev, onclick: function () { st.month = new Date(y, mo - 1, 1); self.step1(); }, text: "‹" }),
      el("p", { class: "bk-month", "aria-live": "polite", text: MONTHS[mo] + " " + y }),
      el("button", { type: "button", class: "bk-nav", "aria-label": "Nächster Monat", disabled: !canNext, onclick: function () { st.month = new Date(y, mo + 1, 1); self.step1(); }, text: "›" })
    ]));
    var grid = el("div", { class: "bk-grid", role: "grid" });
    WD_SHORT.forEach(function (w) { grid.appendChild(el("span", { class: "bk-wd", text: w })); });
    var offset = (new Date(y, mo, 1).getDay() + 6) % 7;
    for (var i = 0; i < offset; i++) grid.appendChild(el("span", { class: "bk-day is-empty" }));
    var days = new Date(y, mo + 1, 0).getDate();
    for (var d = 1; d <= days; d++) {
      var key = y + "-" + pad(mo + 1) + "-" + pad(d);
      var info = data.days[key];
      var status = info ? info.status : "aus";
      var label = { frei: "frei", ausgebucht: "ausgebucht", geschlossen: "", aus: "" }[status];
      var btn = el("button", {
        type: "button", class: "bk-day is-" + status + (st.date === key ? " is-selected" : ""),
        disabled: status !== "frei", "aria-pressed": st.date === key ? "true" : "false",
        "aria-label": longDate(key) + (status === "frei" ? ", Termine frei" : status === "ausgebucht" ? ", ausgebucht" : ", keine Termine"),
        onclick: (function (k) { return function () { st.date = k; st.time = null; self.step1(); var t = self.root.querySelector(".bk-times"); if (t) t.scrollIntoView({ block: "nearest", behavior: "smooth" }); }; })(key)
      }, [el("span", { class: "bk-num", text: String(d) }), label ? el("small", { text: label }) : null]);
      grid.appendChild(btn);
    }
    cal.appendChild(grid);
    cal.appendChild(el("p", { class: "bk-legend" }, [
      el("span", { class: "lg lg-frei", text: "freie Termine" }), el("span", { class: "lg lg-ausgebucht", text: "ausgebucht" }), el("span", { class: "lg lg-geschlossen", text: "keine Sprechzeit" })
    ]));
    r.appendChild(cal);

    // Uhrzeiten
    if (st.date && data.days[st.date]) {
      var slots = data.days[st.date].slots;
      var times = el("div", { class: "bk-times" }, [el("p", { class: "bk-sub", text: longDate(st.date) })]);
      var list = el("div", { class: "bk-slots" });
      slots.forEach(function (s) {
        list.appendChild(el("button", {
          type: "button", class: "bk-slot" + (s.free ? "" : " is-taken") + (st.time === s.t ? " is-selected" : ""),
          disabled: !s.free, "aria-label": s.t + " Uhr" + (s.free ? "" : ", belegt"),
          onclick: function () { st.time = s.t; self.step2(); }
        }, [s.t, s.free ? null : el("small", { text: "belegt" })]));
      });
      times.appendChild(list);
      r.appendChild(times);
    } else {
      r.appendChild(el("p", { class: "bk-hint", text: "Bitte wählen Sie einen Tag mit freien Terminen." }));
    }
  };

  Widget.prototype.uid = function () { if (!this._uid) this._uid = Math.random().toString(36).slice(2, 8); return this._uid; };

  Widget.prototype.step2 = function () {
    var self = this, st = this.state, id = this.uid();
    var r = this.root; r.innerHTML = "";
    r.appendChild(this.head("Ihre Daten", 2));
    var typeLabel = (this.data.types.filter(function (t) { return t.id === st.type; })[0] || {}).label || "";
    r.appendChild(el("div", { class: "bk-summary" }, [
      el("strong", { text: longDate(st.date) + " · " + st.time + " Uhr" }),
      el("span", { text: typeLabel }),
      el("button", { type: "button", class: "bk-link", text: "ändern", onclick: function () { self.step1(); } })
    ]));
    var f = el("form", { class: "form bk-form", novalidate: true });
    function field(name, label, type, req, extra) {
      var inp = el(type === "textarea" ? "textarea" : "input", Object.assign({ id: "bk-" + name + "-" + id, name: name, required: !!req }, type === "textarea" ? {} : { type: type }, extra || {}));
      if (st[name]) inp.value = st[name];
      return el("div", {}, [el("label", { for: inp.id, text: label + (req ? " *" : "") }), inp]);
    }
    f.appendChild(el("div", { class: "form-row" }, [field("name", "Vor- und Nachname", "text", true, { autocomplete: "name" }), field("phone", "Telefon", "tel", st.type === "telefon", { autocomplete: "tel" })]));
    f.appendChild(field("email", "E-Mail", "email", true, { autocomplete: "email" }));
    f.appendChild(field("message", "Nachricht (optional)", "textarea", false, { placeholder: "Was wünschen Sie sich? Bitte keine ausführlichen Gesundheitsdaten – diese besprechen wir persönlich." }));
    f.appendChild(el("input", { type: "text", name: "website", tabindex: "-1", autocomplete: "off", class: "bk-hp", "aria-hidden": "true" }));
    var consent = el("input", { type: "checkbox", name: "consent", required: true, id: "bk-consent-" + id });
    f.appendChild(el("label", { class: "check", for: consent.id }, [consent, el("span", { html: 'Ich habe die <a href="' + base + 'datenschutz/" target="_blank">Datenschutzhinweise</a> gelesen und bin mit der Verarbeitung meiner Angaben zur Terminvereinbarung einverstanden. *' })]));
    var err = el("p", { class: "bk-error", role: "alert", hidden: true });
    f.appendChild(err);
    var submit = el("button", { class: "btn", type: "submit", text: "Termin verbindlich buchen" });
    f.appendChild(el("div", { class: "btn-row" }, [submit, el("button", { type: "button", class: "btn btn-ghost", text: "Zurück", onclick: function () { self.step1(); } })]));
    f.appendChild(el("p", { class: "form-hint", text: "Sie erhalten sofort eine Bestätigung per E-Mail. Absagen bitte spätestens 24 Stunden vorher." }));

    f.addEventListener("submit", function (e) {
      e.preventDefault();
      ["name", "phone", "email", "message"].forEach(function (k) { st[k] = f.elements[k].value.trim(); });
      if (!f.checkValidity()) { f.reportValidity(); return; }
      err.hidden = true; submit.disabled = true; submit.textContent = "Wird gebucht …";
      fetch(API + "?action=book", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date: st.date, time: st.time, type: st.type, treatment: st.treatment, name: st.name, email: st.email, phone: st.phone,
          message: st.message, consent: consent.checked, website: f.elements.website.value, elapsed: Date.now() - st.opened })
      }).then(function (res) { return res.json().catch(function () { return { ok: false, error: "Technischer Fehler." }; }); })
        .then(function (d) {
          if (d.ok) { load(true); self.step3(d); return; }
          err.textContent = d.error || "Die Buchung ist fehlgeschlagen."; err.hidden = false;
          submit.disabled = false; submit.textContent = "Termin verbindlich buchen";
          if (d.refresh) { st.time = null; self.opts.force = true; setTimeout(function () { self.render(); }, 2500); }
        }).catch(function () {
          err.textContent = "Keine Verbindung. Bitte versuchen Sie es erneut oder schreiben Sie an " + CFG.email + "."; err.hidden = false;
          submit.disabled = false; submit.textContent = "Termin verbindlich buchen";
        });
    });
    r.appendChild(f);
    var first = f.querySelector("input"); if (first) setTimeout(function () { first.focus(); }, 50);
  };

  Widget.prototype.step3 = function (d) {
    var self = this, r = this.root; r.innerHTML = "";
    r.appendChild(this.head("Ihr Termin ist gebucht", 3));
    r.appendChild(el("div", { class: "bk-done" }, [
      el("span", { class: "bk-check", "aria-hidden": "true", text: "✓" }),
      el("p", { class: "bk-done-date", text: d.label }),
      el("p", { text: d.mail ? "Eine Bestätigung mit allen Details wurde an " + this.state.email + " gesendet. Bitte prüfen Sie ggf. auch Ihren Spam-Ordner." : "Ihr Termin ist eingetragen. Die Bestätigungs-E-Mail konnte leider nicht versendet werden – wir melden uns bei Ihnen." }),
      el("div", { class: "btn-row" }, [
        el("a", { class: "btn btn-ghost", href: base + "patientenformulare/anamnesebogen/", text: "Anamnesebogen vorab ausfüllen" }),
        this.opts.dialog ? el("button", { type: "button", class: "btn", text: "Schließen", onclick: function () { self.opts.dialog.close(); } }) : null
      ])
    ]));
    var t = r.querySelector(".bk-title"); if (t) t.focus();
  };

  Widget.prototype.fallback = function () {
    var r = this.root; r.innerHTML = "";
    var page = document.getElementById("terminanfrage");
    if (page && !this.opts.dialog) { page.hidden = false; r.hidden = true; return; }
    r.appendChild(this.head("Termin anfragen", 1));
    r.appendChild(el("p", { text: "Der Online-Kalender ist gerade nicht erreichbar. Bitte senden Sie uns Ihre Terminanfrage per E-Mail – wir melden uns schnellstmöglich." }));
    r.appendChild(el("div", { class: "btn-row" }, [
      el("a", { class: "btn", href: "mailto:" + CFG.email + "?subject=" + encodeURIComponent("Terminanfrage"), text: "E-Mail schreiben" }),
      el("a", { class: "btn btn-ghost", href: base + "termin-buchen/", text: "Zum Anfrageformular" })
    ]));
  };

  /* ---------------- Fenster (Dialog) ---------------- */
  var dialog = null;
  function openDialog(params) {
    if (!dialog) {
      dialog = el("dialog", { class: "booking-dialog", "aria-label": "Termin buchen" });
      var close = el("button", { type: "button", class: "bk-close", "aria-label": "Fenster schließen", html: "&times;", onclick: function () { dialog.close(); } });
      dialog.appendChild(close);
      dialog.appendChild(el("div", { class: "bk-body" }));
      dialog.addEventListener("click", function (e) { if (e.target === dialog) dialog.close(); });
      dialog.addEventListener("close", function () { document.documentElement.classList.remove("bk-open"); });
      document.body.appendChild(dialog);
    }
    var body = dialog.querySelector(".bk-body");
    new Widget(body, { art: params.get("art") || "praxis", behandlung: params.get("behandlung") || "allgemein", dialog: dialog });
    document.documentElement.classList.add("bk-open");
    document.body.classList.remove("nav-open");
    if (typeof dialog.showModal === "function") dialog.showModal(); else dialog.setAttribute("open", "");
  }

  function paramsOf(href) {
    var q = href.indexOf("?") >= 0 ? href.slice(href.indexOf("?") + 1).split("#")[0] : "";
    return new URLSearchParams(q);
  }

  // Alle Links auf die Buchungsseite öffnen das Kalender-Fenster
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest('a[href*="termin-buchen/"]');
    if (!a || e.ctrlKey || e.metaKey || e.shiftKey || e.button !== 0) return;
    if (!window.fetch || !window.URLSearchParams) return;
    e.preventDefault();
    var inline = document.getElementById("booking-widget");
    if (inline && inline._widget) {
      var p = paramsOf(a.getAttribute("href"));
      inline._widget.state.type = p.get("art") || inline._widget.state.type;
      inline._widget.state.treatment = p.get("behandlung") || inline._widget.state.treatment;
      inline._widget.step1 && inline._widget.data ? inline._widget.step1() : inline._widget.render();
      inline.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }
    openDialog(paramsOf(a.getAttribute("href")));
  });

  // Eingebettet auf /termin-buchen/
  var inline = document.getElementById("booking-widget");
  if (inline && window.fetch) {
    var p = new URLSearchParams(window.location.search);
    inline._widget = new Widget(inline, { art: p.get("art") || "praxis", behandlung: p.get("behandlung") || "allgemein" });
  }
})();
