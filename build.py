#!/usr/bin/env python3
"""Statischer Seitengenerator für schick-aesthetik.de.

    python3 build.py

Erzeugt die komplette Website im Ordner docs/ (für GitHub Pages oder jeden
beliebigen Webspace – einfach den Inhalt von docs/ hochladen).
Jede Seite liegt als <permalink>/index.html vor, dadurch entstehen saubere
URLs wie https://www.schick-aesthetik.de/leistungen/hyaluron-faltenbehandlung/
"""
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

from content import EXTRA_SERVICES, FAQ, PRICE_INTRO, PRICES, SERVICES, SITE

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"
SRC = ROOT / "src"
TODAY = date.today().isoformat()
ASSET_VERSION = TODAY.replace("-", "")

esc = html.escape
SERVICE_BY_SLUG = {s["slug"]: s for s in SERVICES}
GROUPS = [
    ("aesthetik", "Ästhetische Medizin", "Natürliche Ästhetik mit Hyaluron, Biostimulatoren, Microneedling & Co. – präzise geplant mit dem Blick einer Zahnärztin."),
    ("naturheilkunde", "Naturheilkunde & Vitalität", "Infusionen, Labordiagnostik und naturheilkundliche Verfahren – ganzheitlich und ehrlich beraten."),
]

# ---------------------------------------------------------------------------
# Icons (Linien-Icons, currentColor)
# ---------------------------------------------------------------------------
def svg(path, vb="0 0 24 24", extra=""):
    return f'<svg viewBox="{vb}" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"{extra}>{path}</svg>'

ICONS = {
    "drop": svg('<path d="M12 3.5c3.2 4 5.5 7.2 5.5 10.2a5.5 5.5 0 0 1-11 0c0-3 2.3-6.2 5.5-10.2z"/><path d="M9.3 14.2a2.8 2.8 0 0 0 2.4 2.6"/>'),
    "sparkle": svg('<path d="M12 3v4M12 17v4M3 12h4M17 12h4"/><path d="M12 8.5l1.2 2.3 2.3 1.2-2.3 1.2L12 15.5l-1.2-2.3L8.5 12l2.3-1.2z"/>'),
    "dots": svg('<circle cx="6" cy="6" r="1"/><circle cx="12" cy="6" r="1"/><circle cx="18" cy="6" r="1"/><circle cx="6" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="18" cy="12" r="1"/><circle cx="6" cy="18" r="1"/><circle cx="12" cy="18" r="1"/><circle cx="18" cy="18" r="1"/>'),
    "plasma": svg('<path d="M9 3h6M10 3v11a2 2 0 0 0 4 0V3"/><path d="M10 9h4"/><path d="M6 20h12"/>'),
    "lotus": svg('<path d="M12 5c2 2.2 2.6 5.3 0 9-2.6-3.7-2-6.8 0-9z"/><path d="M12 14c-2.5-.2-5.6-1.6-7-4.5 3-.3 5.4.8 7 4.5zM12 14c2.5-.2 5.6-1.6 7-4.5-3-.3-5.4.8-7 4.5z"/><path d="M5 17.5c4 1.6 10 1.6 14 0"/>'),
    "contour": svg('<path d="M8 3c-2.5 2.5-3 6-1.5 9.5S8 19 12 21c4-2 4-5 5.5-8.5S18.5 5.5 16 3"/><path d="M10 9.5h4"/>'),
    "infusion": svg('<rect x="8" y="2.5" width="8" height="10" rx="2"/><path d="M8 6h8M12 12.5v4M10.5 16.5h3l-1.5 5z"/>'),
    "leaf": svg('<path d="M5 19c0-8 5-13 14-14-1 9-6 14-14 14z"/><path d="M5 19c3-4 6-7 9-9"/>'),
    "lab": svg('<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 1.8 3h10.4A2 2 0 0 0 19 18l-5-9V3"/><path d="M7.5 15h9"/>'),
    "check": svg('<path d="M4.5 12.5l4.5 4.5 10.5-11"/>'),
    "calendar": svg('<rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/>'),
    "phone": svg('<path d="M5 4h3.5l1.7 4.3-2.2 1.4a11 11 0 0 0 6.3 6.3l1.4-2.2L20 15.5V19a1.5 1.5 0 0 1-1.6 1.5A16.5 16.5 0 0 1 3.5 5.6 1.5 1.5 0 0 1 5 4z"/>'),
    "mail": svg('<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="M3.5 6.5l8.5 6.5 8.5-6.5"/>'),
    "pin": svg('<path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>'),
    "clock": svg('<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>'),
    "heart": svg('<path d="M12 20s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.3a4.3 4.3 0 0 1 7.5 2.5C19.5 15.4 12 20 12 20z"/>'),
    "tooth": svg('<path d="M7.5 3.5c-2.5 0-4 2-4 4.5 0 3 1.5 4 2 7s.8 5.5 2.2 5.5S9.5 16 12 16s2.8 4.5 4.3 4.5 1.7-2.5 2.2-5.5 2-4 2-7c0-2.5-1.5-4.5-4-4.5-2 0-2.8 1.2-4.5 1.2S9.5 3.5 7.5 3.5z"/>'),
    "award": svg('<circle cx="12" cy="9" r="5.5"/><path d="M8.5 13.5L7 21l5-2.5 5 2.5-1.5-7.5"/>'),
    "chat": svg('<path d="M4 5.5h16v10H9l-5 4z"/><path d="M8 9.5h8M8 12.5h5"/>'),
    "whatsapp": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12 2.5a9.4 9.4 0 0 0-8.1 14.2L2.6 21.5l4.9-1.3A9.4 9.4 0 1 0 12 2.5zm0 17.1a7.7 7.7 0 0 1-3.9-1.1l-.3-.2-2.9.8.8-2.8-.2-.3A7.7 7.7 0 1 1 12 19.6zm4.2-5.8c-.2-.1-1.4-.7-1.6-.8s-.4-.1-.5.1-.6.8-.8.9-.3.2-.5.1a6.3 6.3 0 0 1-3.1-2.7c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.7-1.7c-.2-.5-.4-.4-.5-.4h-.5a.9.9 0 0 0-.7.3 2.8 2.8 0 0 0-.9 2.1 4.9 4.9 0 0 0 1 2.6 11.2 11.2 0 0 0 4.3 3.8c1.6.7 2.2.7 3 .6a2.6 2.6 0 0 0 1.7-1.2 2.1 2.1 0 0 0 .1-1.2c0-.1-.2-.2-.4-.3z"/></svg>',
    "chev": '<svg class="chev" viewBox="0 0 10 10" aria-hidden="true" focusable="false"><path d="M1.5 3.5L5 7l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.3"/></svg>',
}

# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------
def rel(from_path, to_path):
    """Relativer Link von Seite from_path (z. B. 'leistungen/x/') zu to_path."""
    depth = len([p for p in from_path.split("/") if p])
    prefix = "../" * depth
    if to_path.startswith(("http", "mailto:", "tel:", "#")):
        return to_path
    if from_path == "404/":
        # 404.html wird unter beliebigen URLs ausgeliefert -> absolute Pfade
        return "/" + to_path
    out = prefix + to_path
    return out or "./"


def absurl(path):
    return f"{SITE['url']}/{path}"


def booking_href(page_path, params=""):
    if SITE["booking_url"]:
        return SITE["booking_url"]
    return rel(page_path, "termin-buchen/") + params


def phone_href():
    return "tel:" + re.sub(r"[^\d+]", "", SITE["phone"])


def fill_links(text, page_path):
    return re.sub(r"\{\{rel:([^}]*)\}\}", lambda m: rel(page_path, m.group(1)), text)


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


# ---------------------------------------------------------------------------
# Strukturierte Daten (schema.org, JSON-LD)
# ---------------------------------------------------------------------------
ORG_ID = SITE["url"] + "/#praxis"
PERSON_ID = SITE["url"] + "/#dr-karina-schick"
WEBSITE_ID = SITE["url"] + "/#website"


def schema_base():
    address = {
        "@type": "PostalAddress",
        "streetAddress": SITE["street"],
        "postalCode": SITE["zip"],
        "addressLocality": SITE["city"],
        "addressRegion": SITE["region"],
        "addressCountry": SITE["country"],
    }
    org = {
        "@type": ["MedicalBusiness", "HealthAndBeautyBusiness"],
        "@id": ORG_ID,
        "name": f"{SITE['brand']} – {SITE['owner']}",
        "alternateName": f"{SITE['owner']} – {SITE['practice']}",
        "description": "Praxis für ästhetische Medizin und Naturheilkunde in Westerburg (Westerwald): Hyaluron, Skinbooster, Biostimulatoren, Microneedling, PRP, Infusionen, Akupunktur und Labordiagnostik.",
        "url": SITE["url"] + "/",
        "email": SITE["email"],
        "image": absurl("assets/img/og-image.jpg"),
        "logo": absurl("assets/img/logo.png"),
        "address": address,
        "hasMap": SITE["maps_url"],
        "areaServed": [{"@type": "City", "name": c} for c in SITE["area_served"]],
        "priceRange": "€€",
        "currenciesAccepted": "EUR",
        "paymentAccepted": ", ".join(SITE["payment"]),
        "founder": {"@id": PERSON_ID},
        "employee": {"@id": PERSON_ID},
        "knowsLanguage": "de",
        "medicalSpecialty": ["Dermatology"],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Leistungen",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"], "url": absurl(f"leistungen/{s['slug']}/")}}
                for s in SERVICES
            ],
        },
    }
    if SITE["phone"]:
        org["telephone"] = SITE["phone"]
    if SITE["booking_url"]:
        org["potentialAction"] = {"@type": "ReserveAction", "target": SITE["booking_url"]}
    person = {
        "@type": "Person",
        "@id": PERSON_ID,
        "name": SITE["owner"],
        "givenName": "Karina",
        "familyName": "Schick",
        "honorificPrefix": "Dr.",
        "jobTitle": ["Zahnärztin", "Heilpraktikerin"],
        "image": absurl("assets/img/dr-karina-schick.jpg"),
        "url": absurl("ueber-mich/"),
        "worksFor": {"@id": ORG_ID},
        "knowsAbout": ["Ästhetische Medizin", "Ästhetische Zahnmedizin", "Prothetik", "Oralchirurgie", "Naturheilkunde", "Hyaluronsäure", "Biostimulatoren"],
    }
    website = {
        "@type": "WebSite",
        "@id": WEBSITE_ID,
        "url": SITE["url"] + "/",
        "name": SITE["brand"],
        "inLanguage": "de-DE",
        "publisher": {"@id": ORG_ID},
    }
    return [org, person, website]


def breadcrumb_schema(crumbs):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": absurl(path)}
            for i, (name, path) in enumerate(crumbs)
        ],
    }


def webpage_schema(page, page_type="WebPage"):
    d = {
        "@type": page_type,
        "@id": absurl(page["path"]) + "#webpage",
        "url": absurl(page["path"]),
        "name": page["title"],
        "description": page["description"],
        "inLanguage": "de-DE",
        "isPartOf": {"@id": WEBSITE_ID},
        "about": {"@id": ORG_ID},
        "dateModified": TODAY,
    }
    if page.get("crumbs"):
        d["breadcrumb"] = {"@id": absurl(page["path"]) + "#breadcrumb"}
    return d


def faq_schema(items):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
            for q, a in items
        ],
    }


def price_value(p):
    m = re.search(r"(\d+)\s*€", p)
    return int(m.group(1)) if m else None


def service_schema(s):
    d = {
        "@type": "Service",
        "@id": absurl(f"leistungen/{s['slug']}/") + "#service",
        "name": s["name"],
        "serviceType": s["service_type"],
        "description": s["description"],
        "url": absurl(f"leistungen/{s['slug']}/"),
        "provider": {"@id": ORG_ID},
        "areaServed": [{"@type": "City", "name": c} for c in SITE["area_served"][:5]],
    }
    vals = [price_value(p) for key in s["prices"] for _, p in PRICES[key]["items"]]
    vals = [v for v in vals if v]
    if vals:
        d["offers"] = {
            "@type": "AggregateOffer",
            "priceCurrency": "EUR",
            "lowPrice": min(vals),
            "highPrice": max(vals),
            "offerCount": len(vals),
            "url": absurl("preise/"),
        }
    return d


def jsonld(graph):
    data = {"@context": "https://schema.org", "@graph": graph}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "</script>"


# ---------------------------------------------------------------------------
# Layout-Bausteine
# ---------------------------------------------------------------------------
NAV = [
    ("Start", ""),
    ("Über mich", "ueber-mich/"),
    ("Leistungen", "leistungen/"),
    ("Preise", "preise/"),
    ("Ihr Termin", "ihr-termin/"),
    ("FAQ", "faq/"),
    ("Kontakt", "kontakt/"),
]


def brand_html(p):
    return (
        f'<a class="brand" href="{rel(p, "")}" aria-label="{esc(SITE["brand"])} – zur Startseite">'
        f'<span class="brand-name">{SITE["brand_short"]}</span>'
        f'<span class="brand-sub">Medical Aesthetics</span></a>'
    )


def header(page):
    p = page["path"]
    items = []
    for label, path in NAV:
        current = ' aria-current="page"' if p == path else ""
        if path == "leistungen/":
            active = p.startswith("leistungen/")
            cols = []
            for gkey, gname, _ in GROUPS:
                links = "".join(
                    f'<li><a href="{rel(p, "leistungen/" + s["slug"] + "/")}"'
                    f'{" aria-current=\"page\"" if p == "leistungen/" + s["slug"] + "/" else ""}>{esc(s["nav"])}</a></li>'
                    for s in SERVICES if s["group"] == gkey
                )
                cols.append(f"<div><p>{gname}</p><ul>{links}</ul></div>")
            items.append(
                f'<li class="has-sub" data-open="false">'
                f'<button class="nav-link" type="button" aria-expanded="false" aria-controls="submenu-leistungen"'
                f'{" aria-current=\"true\"" if active else ""}>Leistungen {ICONS["chev"]}</button>'
                f'<div class="submenu glass" id="submenu-leistungen">{"".join(cols)}'
                f'<div class="all"><a href="{rel(p, "leistungen/")}"{current}>Alle Leistungen im Überblick →</a></div></div></li>'
            )
        else:
            items.append(f'<li><a class="nav-link" href="{rel(p, path)}"{current}>{label}</a></li>')
    phone_btn = (
        f'<a class="btn btn-ghost" href="{phone_href()}">{ICONS["phone"]} {esc(SITE["phone_display"] or SITE["phone"])}</a>'
        if SITE["phone"] else ""
    )
    return f"""<a class="skip-link" href="#inhalt">Zum Inhalt springen</a>
<header class="site-header">
  <div class="container header-inner">
    {brand_html(p)}
    <nav class="main-nav" id="hauptnavigation" aria-label="Hauptnavigation">
      <ul>{"".join(items)}</ul>
      <div class="mobile-cta">
        <a class="btn" href="{booking_href(p)}">{ICONS["calendar"]} Termin buchen</a>
        {phone_btn}
        <a class="btn btn-ghost" href="mailto:{SITE["email"]}">{ICONS["mail"]} E-Mail schreiben</a>
      </div>
    </nav>
    <a class="btn btn-sm header-cta" href="{booking_href(p)}">{ICONS["calendar"]} Termin buchen</a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="hauptnavigation" aria-label="Menü öffnen"><span></span><span></span><span></span></button>
  </div>
</header>"""


def footer(page):
    p = page["path"]
    srv = "".join(f'<li><a href="{rel(p, "leistungen/" + s["slug"] + "/")}">{esc(s["nav"])}</a></li>' for s in SERVICES)
    phone = f'<li><a href="{phone_href()}">{esc(SITE["phone_display"] or SITE["phone"])}</a></li>' if SITE["phone"] else ""
    nav = "".join(f'<li><a href="{rel(p, path)}">{label}</a></li>' for label, path in NAV[1:])
    return f"""<footer class="site-footer">
  <div class="container footer-grid">
    <div>
      {brand_html(p)}
      <p class="footer-claim">{SITE["claim"]}</p>
      <p>{SITE["owner"]}<br>{SITE["profession"]}</p>
    </div>
    <div>
      <h2>Praxis</h2>
      <address><ul>
        <li>{SITE["owner"]} – {SITE["practice"]}</li>
        <li>{SITE["street"]}</li>
        <li>{SITE["zip"]} {SITE["city"]}</li>
        {phone}
        <li><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></li>
      </ul></address>
      <p style="margin-top:14px">{SITE["hours"]}</p>
    </div>
    <div>
      <h2>Leistungen</h2>
      <ul>{srv}</ul>
    </div>
    <div>
      <h2>Navigation</h2>
      <ul>{nav}<li><a href="{booking_href(p)}">Termin buchen</a></li></ul>
    </div>
  </div>
  <div class="container footer-bottom">
    <span>© <span data-year>{date.today().year}</span> {SITE["owner"]} · {SITE["brand"]}</span>
    <ul>
      <li><a href="{rel(p, "impressum/")}">Impressum</a></li>
      <li><a href="{rel(p, "datenschutz/")}">Datenschutz</a></li>
      <li><a href="{rel(p, "patientenformulare/")}">Patientenformulare</a></li>
    </ul>
  </div>
</footer>"""


def action_bar(page):
    p = page["path"]
    second = (
        f'<a href="{phone_href()}">{ICONS["phone"]} Anrufen</a>' if SITE["phone"]
        else f'<a href="mailto:{SITE["email"]}">{ICONS["mail"]} E-Mail</a>'
    )
    wa = f'<a href="https://wa.me/{SITE["whatsapp"]}" aria-label="WhatsApp">{ICONS["whatsapp"]}</a>' if SITE["whatsapp"] else ""
    return f'<div class="action-bar" role="navigation" aria-label="Schnellkontakt">{second}{wa}<a class="primary" href="{booking_href(p)}">{ICONS["calendar"]} Termin buchen</a></div>'


def breadcrumb_html(page):
    crumbs = page.get("crumbs")
    if not crumbs:
        return ""
    lis = []
    for i, (name, path) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            lis.append(f'<li aria-current="page">{esc(name)}</li>')
        else:
            lis.append(f'<li><a href="{rel(page["path"], path)}">{esc(name)}</a></li>')
    return f'<nav class="breadcrumb" aria-label="Brotkrumen-Navigation"><ol>{"".join(lis)}</ol></nav>'


def render(page):
    p = page["path"]
    a = lambda x: rel(p, "assets/" + x)
    graph = schema_base()
    graph.append(webpage_schema(page, page.get("page_type", "WebPage")))
    if page.get("crumbs"):
        bc = breadcrumb_schema(page["crumbs"])
        bc["@id"] = absurl(p) + "#breadcrumb"
        graph.append(bc)
    graph.extend(page.get("schema", []))
    robots = "noindex, follow" if page.get("noindex") else "index, follow, max-image-preview:large, max-snippet:-1"
    og_img = absurl("assets/img/og-image.jpg")
    title = esc(page["title"])
    desc = esc(page["description"])
    canonical = absurl(p)
    preload = f'<link rel="preload" href="{a("img/drops-hero.webp")}" as="image" type="image/webp">' if p == "" else ""
    body = fill_links(page["body"], p)
    return f"""<!DOCTYPE html>
<html lang="de" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="de" href="{canonical}">
<meta name="author" content="{SITE["owner"]}">
<meta name="geo.region" content="DE-RP">
<meta name="geo.placename" content="{SITE["city"]}">
<meta property="og:type" content="{"website" if p == "" else "article"}">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="{esc(SITE["brand"])}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(SITE["brand"])} – {SITE["owner"]}, {SITE["profession"]}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og_img}">
<meta name="theme-color" content="#f6f4f1">
<link rel="icon" href="{a("img/favicon.svg")}" type="image/svg+xml">
<link rel="icon" href="{a("img/favicon-32.png")}" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{a("img/apple-touch-icon.png")}">
<link rel="manifest" href="{rel(p, "site.webmanifest")}">
<link rel="sitemap" type="application/xml" href="{rel(p, "sitemap.xml")}">
<link rel="preload" href="{a("fonts/cormorant-garamond-latin-500-normal.woff2")}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{a("fonts/jost-latin-300-normal.woff2")}" as="font" type="font/woff2" crossorigin>
{preload}
<link rel="stylesheet" href="{a("css/style.css")}?v={ASSET_VERSION}">
{jsonld(graph)}
</head>
<body>
<div class="water-bg" aria-hidden="true"></div>
{header(page)}
<main id="inhalt">
{body}
</main>
{footer(page)}
{action_bar(page)}
<script src="{a("js/main.js")}?v={ASSET_VERSION}" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Wiederkehrende Inhaltsbausteine
# ---------------------------------------------------------------------------
def page_hero(page, eyebrow, h1, lead, ctas=True, extra=""):
    p = page["path"]
    btns = ""
    if ctas:
        btns = f"""<div class="btn-row">
      <a class="btn" href="{booking_href(p, "?art=praxis")}">{ICONS["calendar"]} Erstgespräch vereinbaren</a>
      <a class="btn btn-ghost" href="{booking_href(p, "?art=telefon")}">{ICONS["chat"]} Telefonische Beratung</a>
    </div>"""
    return f"""<section class="page-hero">
  <div class="container">
    {breadcrumb_html(page)}
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>
    {btns}
    {extra}
  </div>
</section>"""


def cta_band(page, heading="Lernen wir uns kennen", text=None, params=""):
    p = page["path"]
    text = text or "In einem persönlichen Erstgespräch nehme ich mir Zeit für Ihre Wünsche, berate Sie ehrlich zu Möglichkeiten und Grenzen und erstelle Ihnen einen individuellen Behandlungsplan."
    phone = f'<a class="btn btn-ghost" href="{phone_href()}">{ICONS["phone"]} Anrufen</a>' if SITE["phone"] else f'<a class="btn btn-ghost" href="mailto:{SITE["email"]}">{ICONS["mail"]} E-Mail schreiben</a>'
    return f"""<section class="section-sm">
  <div class="container">
    <div class="cta-band glass reveal">
      <p class="eyebrow" style="color:#f1dccb">Termin & Beratung</p>
      <h2>{heading}</h2>
      <p>{text}</p>
      <div class="btn-row">
        <a class="btn" href="{booking_href(p, params or "?art=praxis")}">{ICONS["calendar"]} Termin buchen</a>
        <a class="btn btn-ghost" href="{booking_href(p, "?art=telefon")}">{ICONS["chat"]} Telefonische Beratung</a>
        {phone}
      </div>
    </div>
  </div>
</section>"""


def price_block(key, heading_level=2, cls="glass price-group"):
    g = PRICES[key]
    items = "".join(
        f'<li><span class="label">{esc(label)}</span><span class="price">{esc(price)}</span></li>' for label, price in g["items"]
    )
    note = f'<p class="price-note">{esc(g["note"])}</p>' if g.get("note") else ""
    return f'<div class="{cls}" id="preise-{key}"><h{heading_level}>{esc(g["title"])}</h{heading_level}><ul class="price-list">{items}</ul>{note}</div>'


def faq_html(items, heading_level=3):
    out = []
    for q, a in items:
        out.append(
            f'<details><summary><h{heading_level}>{esc(q)}</h{heading_level}></summary><div class="answer"><p>{a}</p></div></details>'
        )
    return f'<div class="faq">{"".join(out)}</div>'


def service_card(s, p, level=3):
    tags = "".join(f"<li>{esc(t)}</li>" for t in s["tags"])
    return f"""<a class="card glass reveal" href="{rel(p, "leistungen/" + s["slug"] + "/")}">
  <span class="icon-drop">{ICONS[s["icon"]]}</span>
  <h{level}>{esc(s["name"])}</h{level}>
  <ul class="tags">{tags}</ul>
  <p>{esc(s["card"])}</p>
  <span class="more">Mehr erfahren</span>
</a>"""


def faq_items():
    phone_text = f" oder telefonisch unter {SITE['phone_display'] or SITE['phone']}" if SITE["phone"] else ""
    return [(q, a.replace("{phone_text}", phone_text)) for q, a in FAQ]


# ---------------------------------------------------------------------------
# Seiten
# ---------------------------------------------------------------------------
def page_home():
    page = {
        "path": "",
        "title": "Ästhetische Medizin & Naturheilkunde Westerburg | Dr. Schick",
        "description": "Dr. Karina Schick, Zahnärztin & Heilpraktikerin in Westerburg: Hyaluron, Skinbooster, Microneedling, Infusionen & Naturheilkunde. Jetzt Termin buchen.",
    }
    p = ""
    aest = "".join(service_card(s, p, 4) for s in SERVICES if s["group"] == "aesthetik")
    nat = "".join(service_card(s, p, 4) for s in SERVICES if s["group"] == "naturheilkunde")
    faq_short = faq_items()[:4]
    page["body"] = f"""
<section class="hero">
  <div class="container hero-grid">
    <div>
      <p class="eyebrow">{SITE["profession"]} · {SITE["city"]}</p>
      <h1>Ästhetische Medizin &amp; Naturheilkunde in Westerburg – <span class="serif-i">natürlich schön</span></h1>
      <p class="lead">Ich bin Dr. Karina Schick – seit 25 Jahren Zahnärztin und heute zusätzlich Heilpraktikerin. In meiner Praxis auf Schloß Westerburg verbinde ich medizinische Präzision mit meiner Leidenschaft für Ästhetik: Ihre natürliche Ausstrahlung sichtbar machen, statt Sie zu verändern.</p>
      <div class="btn-row">
        <a class="btn" href="{booking_href(p, "?art=praxis")}">{ICONS["calendar"]} Erstgespräch buchen</a>
        <a class="btn btn-ghost" href="{booking_href(p, "?art=telefon")}">{ICONS["chat"]} Telefonische Beratung</a>
      </div>
      <ul class="hero-badges">
        <li>{ICONS["check"]} 25 Jahre medizinische Erfahrung</li>
        <li>{ICONS["check"]} Ausführliche, ehrliche Beratung</li>
        <li>{ICONS["check"]} Hochwertige Markenprodukte</li>
      </ul>
    </div>
    <div class="portrait">
      <div class="ripple" aria-hidden="true"><span></span><span></span><span></span></div>
      <div class="portrait-card">
        <picture>
          <source type="image/webp" srcset="assets/img/dr-karina-schick-400.webp 400w, assets/img/dr-karina-schick.webp 600w" sizes="(max-width: 900px) 80vw, 440px">
          <img src="assets/img/dr-karina-schick.jpg" width="600" height="850" alt="Porträt von Dr. Karina Schick, Zahnärztin und Heilpraktikerin in Westerburg" fetchpriority="high">
        </picture>
        <p class="portrait-hello"><small>Hallo, ich bin</small><span>Karina</span></p>
      </div>
      <span class="note note-4">{ICONS["tooth"]} Zahnärztin seit 25 Jahren</span>
      <span class="note note-1">{ICONS["award"]} Heilpraktikerin</span>
      <span class="note note-2">{ICONS["heart"]} Mutter von 4 Kindern</span>
      <span class="note note-3">{ICONS["lotus"]} Ästhetik mit Herz</span>
    </div>
  </div>
</section>

<section class="section-sm" aria-label="Auf einen Blick">
  <div class="container">
    <div class="trust glass reveal">
      <div><strong>25</strong><span>Jahre Erfahrung als Zahnärztin</span></div>
      <div><strong>HP</strong><span>Staatliche Heilpraktikererlaubnis</span></div>
      <div><strong>1:1</strong><span>Persönliche Beratung &amp; Behandlung</span></div>
      <div><strong>100 %</strong><span>Ausgewählte Markenprodukte</span></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head center">
      <p class="eyebrow">Leistungen</p>
      <h2>Meine Schwerpunkte</h2>
      <p class="lead">Von sanfter Faltenbehandlung bis zur naturheilkundlichen Begleitung – jede Behandlung beginnt mit einer ausführlichen Beratung.</p>
    </div>
    <h3 class="eyebrow" style="font-size:.8rem">Ästhetische Medizin</h3>
    <div class="grid grid-3">{aest}</div>
    <h3 class="eyebrow" style="font-size:.8rem;margin-top:48px">Naturheilkunde &amp; Vitalität</h3>
    <div class="grid grid-3">{nat}</div>
  </div>
</section>

<section class="section">
  <div class="container split">
    <div class="reveal">
      <div class="photo-frame">
        <picture>
          <source type="image/webp" srcset="assets/img/dr-karina-schick.webp">
          <img src="assets/img/dr-karina-schick.jpg" width="600" height="850" alt="Dr. Karina Schick lächelnd vor grauem Hintergrund" loading="lazy">
        </picture>
      </div>
    </div>
    <div class="glass panel reveal">
      <p class="eyebrow">Über mich</p>
      <h2>Ästhetik bedeutet nicht, einen Menschen zu verändern</h2>
      <p class="quote">„Es bedeutet, seine natürliche Schönheit sichtbar zu machen.“</p>
      <p>Seit 25 Jahren bin ich mit Leidenschaft Zahnärztin – mit den Schwerpunkten ästhetische Zahnmedizin, Prothetik und Chirurgie. In dieser Zeit habe ich gelernt, wie eng medizinische Qualität, Ästhetik und persönliches Wohlbefinden miteinander verbunden sind.</p>
      <p>Als Heilpraktikerin erweitere ich diesen Blick um weitere Möglichkeiten der ästhetischen und naturheilkundlichen Behandlung. Bei mir steht der Mensch im Mittelpunkt – nicht ein bestimmtes Schönheitsideal.</p>
      <p class="signature">Dr. Karina Schick</p>
      <a class="btn btn-ghost" href="{rel(p, "ueber-mich/")}">Mehr über mich</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head center">
      <p class="eyebrow">Ihr Weg zu mir</p>
      <h2>So läuft Ihre Behandlung ab</h2>
    </div>
    <ol class="steps">
      <li class="glass reveal"><h3>Termin buchen</h3><p>Online-Anfrage, E-Mail oder telefonische Erstberatung – ganz wie es Ihnen passt.</p></li>
      <li class="glass reveal"><h3>Erstgespräch</h3><p>Ca. 30 Minuten für Anamnese, Ihre Wünsche und eine ehrliche Einschätzung.</p></li>
      <li class="glass reveal"><h3>Ihr Plan</h3><p>Transparente Empfehlung mit Ablauf, Risiken und Kosten – ohne Zeitdruck.</p></li>
      <li class="glass reveal"><h3>Behandlung</h3><p>Präzise, hygienisch und mit hochwertigen Produkten – inklusive Nachsorge.</p></li>
    </ol>
    <p class="center" style="margin-top:28px"><a href="{rel(p, "ihr-termin/")}">Alles zum Ablauf &amp; zur Vorbereitung →</a></p>
  </div>
</section>

<section class="section">
  <div class="container grid grid-2" style="align-items:start">
    <div class="glass panel reveal">
      <p class="eyebrow">Preise</p>
      <h2>Transparente Orientierungspreise</h2>
      <p>Gerade bei Selbstzahlerleistungen ist mir Transparenz wichtig. Hier ein Auszug – die vollständige Übersicht finden Sie auf der Preisseite.</p>
      <ul class="price-list">
        <li><span class="label">Lippenunterspritzung</span><span class="price">ab 400 €</span></li>
        <li><span class="label">Profhilo® – 1 Areal</span><span class="price">300 €</span></li>
        <li><span class="label">Microneedling Gesicht</span><span class="price">ab 350 €</span></li>
        <li><span class="label">Vitamin-Infusion</span><span class="price">ab 120 €</span></li>
      </ul>
      <p style="margin-top:20px"><a class="btn btn-ghost" href="{rel(p, "preise/")}">Alle Preise ansehen</a></p>
    </div>
    <div class="reveal">
      <p class="eyebrow">Häufige Fragen</p>
      <h2>Gut zu wissen</h2>
      {faq_html(faq_short)}
      <p style="margin-top:20px"><a href="{rel(p, "faq/")}">Alle Fragen &amp; Antworten →</a></p>
    </div>
  </div>
</section>

<section class="section-sm">
  <div class="container grid grid-2" style="align-items:center">
    <div class="reveal">
      <p class="eyebrow">Praxis im Westerwald</p>
      <h2>Ihre Praxis auf Schloß Westerburg</h2>
      <p>Meine Praxis befindet sich im historischen Schloß Westerburg – gut erreichbar aus Westerburg, Montabaur, Hachenburg, Bad Marienberg, Rennerod, Wallmerod und Limburg an der Lahn.</p>
      <p><strong>{SITE["hours"]}</strong></p>
    </div>
    <div class="glass panel reveal">
      <ul class="contact-list">
        <li><span class="icon-drop">{ICONS["pin"]}</span><div><strong>Adresse</strong><address>{SITE["owner"]} – {SITE["practice"]}<br>{SITE["street"]}<br>{SITE["zip"]} {SITE["city"]}</address><a href="{SITE["maps_url"]}" target="_blank" rel="noopener">Route planen ↗</a></div></li>
        <li><span class="icon-drop">{ICONS["mail"]}</span><div><strong>E-Mail</strong><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></div></li>
        {f'<li><span class="icon-drop">{ICONS["phone"]}</span><div><strong>Telefon</strong><a href="{phone_href()}">{esc(SITE["phone_display"] or SITE["phone"])}</a></div></li>' if SITE["phone"] else ""}
      </ul>
    </div>
  </div>
</section>
{cta_band(page)}
"""
    page["schema"] = []
    return page


def page_about():
    page = {
        "path": "ueber-mich/",
        "title": "Über mich – Dr. Karina Schick, Zahnärztin & Heilpraktikerin",
        "description": "Dr. Karina Schick: seit 25 Jahren Zahnärztin (ästhetische Zahnmedizin, Prothetik, Chirurgie), Heilpraktikerin, Mutter von vier Kindern – Praxis in Westerburg.",
        "crumbs": [("Start", ""), ("Über mich", "ueber-mich/")],
        "page_type": "ProfilePage",
    }
    p = page["path"]
    page["body"] = f"""
{page_hero(page, "Über mich", "Dr. Karina Schick – Zahnärztin, Heilpraktikerin, Mutter von 4 Kindern", "Seit 25 Jahren bin ich mit Leidenschaft Zahnärztin. Heute verbinde ich diese Erfahrung mit meiner Begeisterung für Ästhetik und Naturheilkunde – in meiner eigenen Praxis in Westerburg.")}
<section class="section-sm">
  <div class="container split">
    <div class="portrait reveal" style="margin-inline:0">
      <div class="portrait-card">
        <picture>
          <source type="image/webp" srcset="{rel(p, "assets/img/dr-karina-schick.webp")}">
          <img src="{rel(p, "assets/img/dr-karina-schick.jpg")}" width="600" height="850" alt="Porträt von Dr. Karina Schick" loading="eager">
        </picture>
        <p class="portrait-hello"><small>Hallo, ich bin</small><span>Karina</span></p>
      </div>
    </div>
    <div class="glass panel prose reveal">
      <h2>Mein Weg</h2>
      <p>Seit 25 Jahren bin ich mit Leidenschaft als Zahnärztin tätig. Mein besonderer Schwerpunkt liegt dabei in der ästhetischen Zahnmedizin, Prothetik und Chirurgie. In all diesen Jahren habe ich gelernt, wie eng medizinische Qualität, Ästhetik und das persönliche Wohlbefinden eines Menschen miteinander verbunden sind.</p>
      <p>Ästhetik hat mich dabei schon immer besonders fasziniert. Mich interessiert nicht nur, was man verändern kann, sondern vor allem, wie man Schönheit natürlich, harmonisch und individuell unterstützen kann.</p>
      <p>Aus diesem Interesse heraus habe ich mich entschieden, zusätzlich den Weg als Heilpraktikerin zu gehen. Für mich ist das keine Abkehr von meiner Tätigkeit als Zahnärztin, sondern eine wertvolle Erweiterung meiner bisherigen Arbeit und meiner medizinischen Perspektive.</p>
      <p>Ich werde auch weiterhin als Zahnärztin tätig sein. Gleichzeitig möchte ich mit meiner Praxis für ästhetische Medizin einen Raum schaffen, in dem ich meine langjährige medizinische Erfahrung mit meiner Leidenschaft für Ästhetik verbinden kann.</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="container narrow">
    <div class="glass panel prose reveal">
      <h2>Was mir wichtig ist</h2>
      <p>Bei jeder Behandlung steht für mich der Mensch im Mittelpunkt. Ich möchte keine Gesichter verändern und keinem bestimmten Schönheitsideal folgen. Mein Ziel ist es, Ihre individuelle Schönheit und natürliche Ausstrahlung zu bewahren und dort zu unterstützen, wo Sie sich selbst eine Veränderung wünschen.</p>
      <p>Eine ausführliche und ehrliche Beratung ist für mich die Grundlage jeder Behandlung. Ich nehme mir Zeit, Ihre Wünsche zu verstehen, Möglichkeiten und Grenzen offen zu besprechen und gemeinsam mit Ihnen einen Weg zu finden, der zu Ihnen passt.</p>
      <p>Dabei sind mir Natürlichkeit, Harmonie und ein verantwortungsvoller Umgang mit ästhetischen Behandlungen besonders wichtig.</p>
      <h3>Der Blick einer Zahnärztin</h3>
      <p>Meine 25-jährige Erfahrung als Zahnärztin hat meinen Blick für Proportionen, Symmetrie und Ästhetik geprägt. Die Heilpraktik erweitert diesen Blick um weitere Möglichkeiten der ästhetischen Behandlung.</p>
      <p class="quote">Ich möchte, dass Sie meine Praxis mit einem guten Gefühl verlassen – und vor allem das Gefühl haben, Sie selbst zu sein. Nur vielleicht ein bisschen frischer, strahlender und wohler in Ihrer eigenen Haut.</p>
      <p>Denn für mich bedeutet Ästhetik nicht, einen Menschen zu verändern. Es bedeutet, seine natürliche Schönheit sichtbar zu machen.</p>
      <p class="signature">Ihre Dr. Karina Schick</p>
    </div>
  </div>
</section>

<section class="section-sm">
  <div class="container">
    <div class="section-head center"><p class="eyebrow">Qualifikation</p><h2>Ausbildung &amp; Erfahrung</h2></div>
    <div class="grid grid-3">
      <div class="card glass reveal"><span class="icon-drop">{ICONS["tooth"]}</span><h3>Zahnärztin seit 25 Jahren</h3><p>Promovierte Zahnärztin mit den Schwerpunkten ästhetische Zahnmedizin, Prothetik und Chirurgie.</p></div>
      <div class="card glass reveal"><span class="icon-drop">{ICONS["award"]}</span><h3>Heilpraktikerin</h3><p>Staatliche Erlaubnis zur Ausübung der Heilkunde nach dem Heilpraktikergesetz.</p></div>
      <div class="card glass reveal"><span class="icon-drop">{ICONS["sparkle"]}</span><h3>Ästhetische Medizin</h3><p>Regelmäßige Fortbildungen in Injektionstechniken, Biostimulatoren und Hautgesundheit.</p></div>
    </div>
  </div>
</section>
{cta_band(page, "Lernen wir uns persönlich kennen")}
"""
    page["schema"] = []
    return page


def page_services():
    page = {
        "path": "leistungen/",
        "title": "Leistungen: Ästhetik & Naturheilkunde | Dr. Karina Schick",
        "description": "Leistungen in Westerburg: Hyaluron, Skinbooster, Profhilo®, Polynukleotide, Microneedling, PRP, Lipolyse, Infusionen, Akupunktur und Labordiagnostik.",
        "crumbs": [("Start", ""), ("Leistungen", "leistungen/")],
        "page_type": "CollectionPage",
    }
    p = page["path"]
    sections = []
    for gkey, gname, gtext in GROUPS:
        cards = "".join(service_card(s, p) for s in SERVICES if s["group"] == gkey)
        sections.append(f"""<section class="section-sm">
  <div class="container">
    <div class="section-head"><p class="eyebrow">Schwerpunkt</p><h2>{gname}</h2><p class="lead">{gtext}</p></div>
    <div class="grid grid-3">{cards}</div>
  </div>
</section>""")
    extra = "".join(f'<div class="glass panel reveal"><h3>{esc(n)}</h3><p class="muted">{esc(t)}</p><a href="{booking_href(p, "?art=praxis")}">Beratung anfragen →</a></div>' for n, t in EXTRA_SERVICES)
    page["body"] = f"""
{page_hero(page, "Leistungen", "Leistungen für Ästhetik, Naturheilkunde &amp; Vitalität", "Ich stelle nicht alles gleichwertig nebeneinander, sondern konzentriere mich auf zwei Schwerpunkte: ästhetische Medizin sowie Naturheilkunde mit Infusionen und Labordiagnostik. Jede Behandlung beginnt mit einem ausführlichen Gespräch.")}
{"".join(sections)}
<section class="section-sm"><div class="container"><div class="section-head"><h2>Weitere Leistungen</h2></div><div class="grid grid-2">{extra}
<div class="glass panel reveal"><h3>Wichtiger Hinweis</h3><p class="muted">Ästhetische Behandlungen und naturheilkundliche Verfahren unterscheiden sich in Zielsetzung und Wirkweise. Ästhetische Behandlungen verfolgen keinen Heilzweck. Ein bestimmtes Ergebnis kann bei keiner Behandlung garantiert werden.</p></div></div></div></section>
{cta_band(page, "Welche Behandlung passt zu mir?", "Sie sind unsicher, welche Behandlung für Sie infrage kommt? Im Erstgespräch analysieren wir gemeinsam Ihre Wünsche und ich empfehle Ihnen ehrlich, was sinnvoll ist – und was nicht.")}
"""
    page["schema"] = [{
        "@type": "ItemList",
        "name": "Leistungen",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": absurl(f"leistungen/{s['slug']}/"), "name": s["name"]}
            for i, s in enumerate(SERVICES)
        ],
    }]
    return page


def page_service(s):
    path = f"leistungen/{s['slug']}/"
    page = {
        "path": path,
        "title": s["title"],
        "description": s["description"],
        "crumbs": [("Start", ""), ("Leistungen", "leistungen/"), (s["nav"], path)],
    }
    p = path
    facts = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in s["facts"])
    prices = "".join(price_block(k, 3, "price-group") for k in s["prices"])
    price_section = (
        f'<h2 id="kosten">Kosten</h2>{prices}<p class="small muted">Orientierungspreise. Die genauen Kosten lege ich nach dem Beratungsgespräch transparent mit Ihnen fest. <a href="{rel(p, "preise/")}">Zur vollständigen Preisliste →</a></p>'
        if s["prices"]
        else f'<h2 id="kosten">Kosten</h2><p>Die Kosten richten sich nach Aufwand und Umfang der Behandlung. Sie erhalten im Beratungsgespräch vorab eine transparente Kostenaufstellung. <a href="{rel(p, "preise/")}">Zur Preisübersicht →</a></p>'
    )
    faq = f'<h2>Häufige Fragen zu {esc(s["nav"])}</h2>{faq_html(s["faq"])}' if s["faq"] else ""
    group_name = dict((g[0], g[1]) for g in GROUPS)[s["group"]]
    siblings = "".join(
        f'<li><a href="{rel(p, "leistungen/" + o["slug"] + "/")}"{" aria-current=\"page\"" if o is s else ""}>{esc(o["nav"])}</a></li>'
        for o in SERVICES if o["group"] == s["group"]
    )
    params = f"?behandlung={s['slug']}"
    phone_line = f'<a class="btn btn-ghost" href="{phone_href()}">{ICONS["phone"]} Anrufen</a>' if SITE["phone"] else f'<a class="btn btn-ghost" href="mailto:{SITE["email"]}">{ICONS["mail"]} E-Mail</a>'
    page["body"] = f"""
{page_hero(page, group_name, esc(s["h1"]), esc(s["lead"]), ctas=False, extra=f'''<div class="btn-row"><a class="btn" href="{booking_href(p, params + "&art=praxis")}">{ICONS["calendar"]} Beratung zu dieser Behandlung</a><a class="btn btn-ghost" href="#kosten">Kosten ansehen</a></div>''')}
<section class="section-sm">
  <div class="container content-layout">
    <article class="glass panel prose">
      <dl class="facts">{facts}</dl>
      {s["body"]}
      {price_section}
      {faq}
      <div class="cta-band" style="margin-top:40px;border-radius:18px">
        <h2>Beratung zu {esc(s["nav"])} vereinbaren</h2>
        <p>Im persönlichen Erstgespräch kläre ich, ob die Behandlung für Sie geeignet ist, und bespreche Ablauf, Risiken und Kosten.</p>
        <div class="btn-row"><a class="btn" href="{booking_href(p, params + "&art=praxis")}">{ICONS["calendar"]} Termin buchen</a><a class="btn btn-ghost" href="{booking_href(p, params + "&art=telefon")}">{ICONS["chat"]} Telefonische Beratung</a></div>
      </div>
    </article>
    <aside class="sidebar" aria-label="Termin und weitere Leistungen">
      <div class="glass panel">
        <h2>Termin vereinbaren</h2>
        <p class="small muted">Erstgespräch ca. 30 Minuten · {SITE["hours"]}</p>
        <a class="btn" href="{booking_href(p, params + "&art=praxis")}">{ICONS["calendar"]} Termin buchen</a>
        <a class="btn btn-ghost" href="{booking_href(p, params + "&art=telefon")}">{ICONS["chat"]} Telefonische Beratung</a>
        {phone_line}
      </div>
      <nav class="glass panel" aria-label="{group_name}">
        <h2>{group_name}</h2>
        <ul>{siblings}</ul>
      </nav>
    </aside>
  </div>
</section>
"""
    page["schema"] = [service_schema(s)]
    if s["faq"]:
        page["schema"].append(faq_schema(s["faq"]))
    return page


def page_prices():
    page = {
        "path": "preise/",
        "title": "Preise – Hyaluron, Profhilo®, Infusionen & mehr | Dr. Schick",
        "description": "Preise für Hyaluron, Lippen, Profhilo®, Polynukleotide, Microneedling, Lipolyse, Bio-Botox und Infusionen in Westerburg. Zahlung bar, EC-Karte oder PayPal.",
        "crumbs": [("Start", ""), ("Preise", "preise/")],
    }
    p = page["path"]
    order = ["hyaluron", "biostimulatoren", "biobotox", "microneedling", "lipolyse", "infusionen"]
    service_for = {k: s for s in SERVICES for k in s["prices"]}
    blocks = []
    for k in order:
        s = service_for.get(k)
        link = f'<p class="small" style="margin-top:12px"><a href="{rel(p, "leistungen/" + s["slug"] + "/")}">Mehr zu {esc(s["nav"])} →</a></p>' if s else ""
        blocks.append(f'<div class="reveal">{price_block(k, 2)}{link}</div>')
    offers = []
    for k in order:
        for label, price in PRICES[k]["items"]:
            v = price_value(price)
            if v:
                offers.append({"@type": "Offer", "name": f'{PRICES[k]["title"]}: {label}', "priceCurrency": "EUR",
                               "priceSpecification": {"@type": "PriceSpecification", "minPrice" if "ab" in price else "price": v, "priceCurrency": "EUR"},
                               "offeredBy": {"@id": ORG_ID}})
    page["body"] = f"""
{page_hero(page, "Preise", "Preise &amp; Kosten", esc(PRICE_INTRO), ctas=False)}
<section class="section-sm">
  <div class="container">
    <div class="grid grid-2" style="align-items:start">{"".join(blocks)}</div>
    <div class="grid grid-2" style="margin-top:28px">
      <div class="glass panel reveal">
        <h2>Ohne feste Preisangabe</h2>
        <p>Für <a href="{rel(p, "leistungen/vampirlifting-prp/")}">Vampirlifting (PRP)</a>, <a href="{rel(p, "leistungen/naturheilverfahren-akupunktur/")}">Naturheilverfahren &amp; Akupunktur</a>, <a href="{rel(p, "leistungen/labordiagnostik/")}">Labordiagnostik</a> und Laserbehandlungen richten sich die Kosten nach Umfang und Aufwand. Sie erhalten vorab eine transparente Kostenaufstellung.</p>
      </div>
      <div class="glass panel reveal">
        <h2>Zahlung &amp; Erstattung</h2>
        <p>Sie können <strong>bar, mit EC-Karte oder per PayPal</strong> bezahlen. Ästhetische Behandlungen sind Selbstzahlerleistungen. Private Krankenversicherungen, Beihilfe oder Zusatzversicherungen erstatten Heilpraktikerleistungen je nach Tarif teilweise.</p>
        <p class="small muted">Bitte sagen Sie Termine spätestens 24 Stunden vorher ab, da ansonsten ein Ausfallhonorar anfällt.</p>
      </div>
    </div>
  </div>
</section>
{cta_band(page, "Individuelles Angebot erhalten", "Nach dem Beratungsgespräch erhalten Sie eine verbindliche, auf Sie abgestimmte Kostenaufstellung – ohne versteckte Kosten.")}
"""
    page["schema"] = [{"@type": "OfferCatalog", "name": "Preisübersicht", "url": absurl(p), "itemListElement": offers}]
    return page


def page_appointment():
    page = {
        "path": "ihr-termin/",
        "title": "Ihr Termin – Ablauf, Vorbereitung & Unterlagen | Dr. Schick",
        "description": "So läuft Ihr erster Termin in der Praxis Dr. Karina Schick in Westerburg ab: Dauer, Vorbereitung, mitzubringende Unterlagen, Bezahlung und Absagen.",
        "crumbs": [("Start", ""), ("Ihr Termin", "ihr-termin/")],
    }
    p = page["path"]
    page["body"] = f"""
{page_hero(page, "Ablauf", "Ihr Termin: Ablauf, Vorbereitung &amp; Unterlagen", "Damit Sie sich rundum wohlfühlen, erfahren Sie hier, was Sie bei Ihrem ersten Besuch erwartet und wie Sie sich am besten vorbereiten.")}
<section class="section-sm">
  <div class="container">
    <ol class="steps">
      <li class="glass reveal"><h2 style="font-size:1.35rem">Terminanfrage</h2><p>Über „Termin buchen“, per E-Mail oder als telefonische Erstberatung.</p></li>
      <li class="glass reveal"><h2 style="font-size:1.35rem">Erstgespräch</h2><p>Ca. 30 Minuten: Anamnese, Wünsche, Ziele und bisherige Befunde.</p></li>
      <li class="glass reveal"><h2 style="font-size:1.35rem">Behandlungsplan</h2><p>Individuelle Empfehlung, Aufklärung zu Risiken und transparente Kosten.</p></li>
      <li class="glass reveal"><h2 style="font-size:1.35rem">Behandlung &amp; Nachsorge</h2><p>Folgetermine ca. 30–60 Minuten, inklusive Hinweisen für die Zeit danach.</p></li>
    </ol>
  </div>
</section>
<section class="section-sm">
  <div class="container grid grid-2" style="align-items:start">
    <div class="glass panel prose reveal">
      <h2>Was sollte ich mitbringen?</h2>
      <p>Bitte bringen Sie – falls vorhanden – folgende Unterlagen mit:</p>
      <ul>
        <li>aktuelle Arztberichte und Laborwerte</li>
        <li>eine Liste Ihrer Medikamente und Nahrungsergänzungsmittel</li>
        <li>relevante Befunde (z. B. Blutbild, Schilddrüse, Stuhl-/Darmbefunde)</li>
        <li>Impfpass und Allergiepass</li>
        <li>bei ästhetischen Behandlungen: Ihren Injektionspass</li>
      </ul>
      <h3>Anamnesebogen vorab ausfüllen</h3>
      <p>Sie sparen Zeit, wenn Sie den <a href="{rel(p, "patientenformulare/anamnesebogen/")}">Anamnesebogen</a> zu Hause ausdrucken, ausfüllen und zum Termin mitbringen. Selbstverständlich können Sie ihn auch vor Ort ausfüllen.</p>
    </div>
    <div class="glass panel prose reveal">
      <h2>Gut zu wissen</h2>
      <h3>Dauer</h3>
      <p>Ersttermin ca. 30 Minuten, Folgetermine ca. 30–60 Minuten.</p>
      <h3>Überweisung</h3>
      <p>Nicht erforderlich – Sie können direkt einen Termin vereinbaren.</p>
      <h3>Bezahlung</h3>
      <p>Bar, EC-Karte oder PayPal.</p>
      <h3>Absagen</h3>
      <p>Bitte sagen Sie Termine spätestens 24 Stunden vorher ab, da ansonsten ein Ausfallhonorar anfällt.</p>
      <h3>Vor ästhetischen Behandlungen</h3>
      <p>Kommen Sie möglichst ungeschminkt. Informieren Sie mich über blutverdünnende Medikamente, Schwangerschaft/Stillzeit, Herpes oder akute Entzündungen.</p>
    </div>
  </div>
</section>
{cta_band(page)}
"""
    page["schema"] = []
    return page


def page_faq():
    page = {
        "path": "faq/",
        "title": "Häufige Fragen (FAQ) – Kosten, Ablauf & Termine | Dr. Schick",
        "description": "Antworten auf häufige Fragen: Ablauf des Ersttermins, Dauer, Unterlagen, Bezahlung, Kostenerstattung, Überweisung, Absagen, Nebenwirkungen und Vorbereitung.",
        "crumbs": [("Start", ""), ("FAQ", "faq/")],
        "page_type": "WebPage",
    }
    items = faq_items()
    page["body"] = f"""
{page_hero(page, "FAQ", "Häufige Fragen &amp; Antworten", "Kosten, Dauer, Ablauf, Vorbereitung, Nebenwirkungen und Erstattung – hier finden Sie die wichtigsten Antworten. Ihre Frage ist nicht dabei? Schreiben Sie mir gern.", ctas=False)}
<section class="section-sm">
  <div class="container narrow">
    {faq_html(items, 2)}
  </div>
</section>
{cta_band(page, "Noch Fragen?", "Gern beantworte ich Ihre Fragen persönlich – in einer telefonischen Erstberatung oder direkt im Erstgespräch in meiner Praxis.", "?art=telefon")}
"""
    page["schema"] = [faq_schema(items)]
    return page


def page_booking():
    page = {
        "path": "termin-buchen/",
        "title": "Termin buchen – Erstgespräch & Beratung | Dr. Karina Schick",
        "description": "Jetzt Termin anfragen: persönliches Erstgespräch in der Praxis in Westerburg oder telefonische Erstberatung bei Dr. Karina Schick, Zahnärztin & Heilpraktikerin.",
        "crumbs": [("Start", ""), ("Termin buchen", "termin-buchen/")],
    }
    p = page["path"]
    options = "".join(f'<option value="{s["slug"]}">{esc(s["name"])}</option>' for s in SERVICES)
    external = ""
    if SITE["booking_url"]:
        external = f"""<div class="glass panel reveal" style="margin-bottom:24px"><h2>Online-Terminbuchung</h2><p>Wählen Sie Ihren Wunschtermin direkt in meinem Online-Kalender.</p><a class="btn" href="{SITE["booking_url"]}" target="_blank" rel="noopener">{ICONS["calendar"]} Zum Online-Kalender</a></div>"""
    phone_li = f'<li><span class="icon-drop">{ICONS["phone"]}</span><div><strong>Telefon</strong><a href="{phone_href()}">{esc(SITE["phone_display"] or SITE["phone"])}</a></div></li>' if SITE["phone"] else ""
    wa_li = f'<li><span class="icon-drop">{ICONS["whatsapp"]}</span><div><strong>WhatsApp</strong><a href="https://wa.me/{SITE["whatsapp"]}">Nachricht senden</a></div></li>' if SITE["whatsapp"] else ""
    page["body"] = f"""
{page_hero(page, "Termin &amp; Beratung", "Termin buchen", "Wählen Sie, ob Sie ein persönliches Erstgespräch in der Praxis oder zunächst eine telefonische Erstberatung wünschen. Ich melde mich schnellstmöglich mit einem Terminvorschlag bei Ihnen.", ctas=False)}
<section class="section-sm">
  <div class="container content-layout">
    <div>
      {external}
      <form class="glass panel form" id="terminanfrage" data-mail="{SITE["email"]}" action="mailto:{SITE["email"]}" method="post" enctype="text/plain">
        <h2>Terminanfrage</h2>
        <fieldset>
          <legend>Art des Termins</legend>
          <div class="choice">
            <label><input type="radio" name="art" value="praxis" data-label="Persönliches Erstgespräch in der Praxis" checked><span><strong>Erstgespräch in der Praxis</strong><small>ca. 30 Minuten, persönlich in Westerburg</small></span></label>
            <label><input type="radio" name="art" value="telefon" data-label="Telefonische Erstberatung (Rückruf)"><span><strong>Telefonische Beratung</strong><small>Ich rufe Sie zum Wunschzeitpunkt zurück</small></span></label>
            <label><input type="radio" name="art" value="behandlung" data-label="Behandlungstermin (nach erfolgter Beratung)"><span><strong>Behandlungstermin</strong><small>nach bereits erfolgter Beratung</small></span></label>
            <label><input type="radio" name="art" value="nachsorge" data-label="Kontroll-/Nachsorgetermin"><span><strong>Kontrolle / Nachsorge</strong><small>für bestehende Patientinnen &amp; Patienten</small></span></label>
          </div>
        </fieldset>
        <div>
          <label for="f-behandlung">Ich interessiere mich für</label>
          <select id="f-behandlung" name="behandlung">
            <option value="allgemein">Allgemeine Beratung / noch unsicher</option>
            {options}
            <option value="laser">Laserbehandlung</option>
          </select>
        </div>
        <div class="form-row">
          <div><label for="f-name">Vor- und Nachname *</label><input id="f-name" name="name" type="text" autocomplete="name" required></div>
          <div><label for="f-tel">Telefon</label><input id="f-tel" name="telefon" type="tel" autocomplete="tel"></div>
        </div>
        <div class="form-row">
          <div><label for="f-mail">E-Mail *</label><input id="f-mail" name="email" type="email" autocomplete="email" required></div>
          <div><label for="f-zeit">Wunschtermin / Erreichbarkeit</label><input id="f-zeit" name="wunschtermin" type="text" placeholder="z. B. dienstags ab 15 Uhr"></div>
        </div>
        <div><label for="f-nachricht">Ihre Nachricht</label><textarea id="f-nachricht" name="nachricht" placeholder="Was wünschen Sie sich? (Bitte keine ausführlichen Gesundheitsdaten – diese besprechen wir persönlich.)"></textarea></div>
        <label class="check"><input type="checkbox" required> <span>Ich habe die <a href="{rel(p, "datenschutz/")}">Datenschutzerklärung</a> gelesen. Mir ist bewusst, dass die Anfrage über mein E-Mail-Programm unverschlüsselt versendet wird. *</span></label>
        <div><button class="btn" type="submit">{ICONS["mail"]} Terminanfrage senden</button></div>
        <p class="form-hint">Beim Absenden öffnet sich Ihr E-Mail-Programm mit einer vorausgefüllten Nachricht an {SITE["email"]}. * Pflichtfelder</p>
        <p class="form-hint" id="form-done" hidden><strong>Danke!</strong> Bitte senden Sie die vorbereitete E-Mail in Ihrem E-Mail-Programm ab. Falls sich kein Programm geöffnet hat, schreiben Sie mir direkt an <a href="mailto:{SITE["email"]}">{SITE["email"]}</a>.</p>
      </form>
    </div>
    <aside class="sidebar" aria-label="Kontaktmöglichkeiten">
      <div class="glass panel">
        <h2>Direkter Kontakt</h2>
        <ul class="contact-list">
          {phone_li}{wa_li}
          <li><span class="icon-drop">{ICONS["mail"]}</span><div><strong>E-Mail</strong><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></div></li>
          <li><span class="icon-drop">{ICONS["clock"]}</span><div><strong>Sprechzeiten</strong>{SITE["hours"]}</div></li>
          <li><span class="icon-drop">{ICONS["pin"]}</span><div><strong>Praxis</strong>{SITE["street"]}, {SITE["zip"]} {SITE["city"]}</div></li>
        </ul>
      </div>
      <div class="glass panel">
        <h2>Gut vorbereitet</h2>
        <p class="small">Füllen Sie den <a href="{rel(p, "patientenformulare/anamnesebogen/")}">Anamnesebogen</a> gern vorab aus. Infos zu Dauer, Unterlagen und Absagen finden Sie unter <a href="{rel(p, "ihr-termin/")}">Ihr Termin</a>.</p>
      </div>
    </aside>
  </div>
</section>
"""
    page["schema"] = []
    return page


def page_contact():
    page = {
        "path": "kontakt/",
        "title": "Kontakt & Anfahrt – Praxis Schloß Westerburg | Dr. Schick",
        "description": "Kontakt und Anfahrt zur Praxis Dr. Karina Schick, Schloß Westerburg, 56457 Westerburg. E-Mail: praxis@schick-aesthetik.de – Termine nach Vereinbarung.",
        "crumbs": [("Start", ""), ("Kontakt", "kontakt/")],
        "page_type": "ContactPage",
    }
    p = page["path"]
    phone_li = f'<li><span class="icon-drop">{ICONS["phone"]}</span><div><strong>Telefon</strong><a href="{phone_href()}">{esc(SITE["phone_display"] or SITE["phone"])}</a></div></li>' if SITE["phone"] else ""
    page["body"] = f"""
{page_hero(page, "Kontakt", "Kontakt &amp; Anfahrt", "Ich freue mich auf Ihre Nachricht. Termine vergebe ich nach Vereinbarung – am schnellsten über die Terminanfrage.")}
<section class="section-sm">
  <div class="container grid grid-2" style="align-items:start">
    <div class="glass panel reveal">
      <h2>So erreichen Sie mich</h2>
      <ul class="contact-list">
        <li><span class="icon-drop">{ICONS["pin"]}</span><div><strong>Praxisadresse</strong><address>{SITE["owner"]}<br>{SITE["practice"]}<br>{SITE["street"]}<br>{SITE["zip"]} {SITE["city"]}</address></div></li>
        {phone_li}
        <li><span class="icon-drop">{ICONS["mail"]}</span><div><strong>E-Mail</strong><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></div></li>
        <li><span class="icon-drop">{ICONS["clock"]}</span><div><strong>Sprechzeiten</strong>{SITE["hours"]}</div></li>
      </ul>
    </div>
    <div class="glass panel reveal">
      <h2>Anfahrt</h2>
      <p>Die Praxis befindet sich im Schloß Westerburg im Herzen des Westerwalds. Aus Montabaur, Hachenburg, Bad Marienberg, Rennerod, Wallmerod oder Limburg an der Lahn erreichen Sie Westerburg bequem mit dem Auto; der Bahnhof Westerburg liegt ebenfalls in der Nähe.</p>
      <p><a class="btn btn-ghost" href="{SITE["maps_url"]}" target="_blank" rel="noopener">{ICONS["pin"]} Route in Google Maps planen</a></p>
      <p class="small muted">Datenschutzhinweis: Die Karte wird erst nach Klick auf den Link bei Google Maps geöffnet. Auf dieser Website werden keine Kartendienste eingebunden.</p>
    </div>
  </div>
</section>
{cta_band(page)}
"""
    page["schema"] = []
    return page


def page_imprint():
    page = {
        "path": "impressum/",
        "title": "Impressum | Dr. Karina Schick – Praxis für Heilkunde",
        "description": "Impressum der Website schick-aesthetik.de – Dr. Karina Schick, Praxis für Heilkunde, Schloß Westerburg, 56457 Westerburg.",
        "crumbs": [("Start", ""), ("Impressum", "impressum/")],
    }
    phone = f"<br>Telefon: {esc(SITE['phone_display'] or SITE['phone'])}" if SITE["phone"] else ""
    page["body"] = f"""
{page_hero(page, "Rechtliches", "Impressum", "Angaben gemäß § 5 Digitale-Dienste-Gesetz (DDG)", ctas=False)}
<section class="section-sm"><div class="container narrow"><div class="glass panel prose">
<h2>Anbieterin</h2>
<p>{SITE["owner"]}<br>{SITE["practice"]}<br>{SITE["street"]}<br>{SITE["zip"]} {SITE["city"]}<br>Deutschland</p>
<h2>Kontakt</h2>
<p>E-Mail: <a href="mailto:{SITE["email"]}">{SITE["email"]}</a>{phone}</p>
<h2>Berufsbezeichnung und berufsrechtliche Regelungen</h2>
<p><strong>Berufsbezeichnung:</strong> Heilpraktikerin (Erlaubnis zur Ausübung der Heilkunde nach dem Heilpraktikergesetz, erteilt in der Bundesrepublik Deutschland)</p>
<p><strong>Zuständige Aufsichtsbehörde:</strong><br>{SITE["authority"]}</p>
<p><strong>Berufsrechtliche Regelungen:</strong> Gesetz über die berufsmäßige Ausübung der Heilkunde ohne Bestallung (Heilpraktikergesetz) sowie die Erste Durchführungsverordnung zum Heilpraktikergesetz, einsehbar unter <a href="https://www.gesetze-im-internet.de/heilprg/" target="_blank" rel="noopener">www.gesetze-im-internet.de/heilprg</a>.</p>
<h2>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h2>
<p>{SITE["owner"]}, Anschrift wie oben</p>
<h2>Verbraucherstreitbeilegung</h2>
<p>Ich bin nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
<h2>Haftung für Inhalte</h2>
<p>Die Inhalte dieser Website wurden mit größter Sorgfalt erstellt. Sie dienen der allgemeinen Information und ersetzen keine persönliche Beratung, Untersuchung oder Diagnose. Für die Richtigkeit, Vollständigkeit und Aktualität der Inhalte kann keine Gewähr übernommen werden.</p>
<h2>Haftung für Links</h2>
<p>Diese Website enthält Links zu externen Websites Dritter, auf deren Inhalte ich keinen Einfluss habe. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber verantwortlich. Bei Bekanntwerden von Rechtsverletzungen werden derartige Links umgehend entfernt.</p>
<h2>Urheberrecht</h2>
<p>Die Inhalte und Bilder dieser Website unterliegen dem deutschen Urheberrecht. Eine Vervielfältigung oder Verwendung ist ohne ausdrückliche Zustimmung nicht gestattet. Die Wassertropfen-Grafiken wurden eigens für diese Website erstellt. Verwendete Schriftarten: Cormorant Garamond und Jost (SIL Open Font License), lokal eingebunden.</p>
</div></div></section>
"""
    page["schema"] = []
    return page


def page_privacy():
    page = {
        "path": "datenschutz/",
        "title": "Datenschutzerklärung | Dr. Karina Schick",
        "description": "Datenschutzerklärung der Website schick-aesthetik.de: Informationen zur Verarbeitung personenbezogener Daten gemäß DSGVO.",
        "crumbs": [("Start", ""), ("Datenschutz", "datenschutz/")],
    }
    phone = f"<br>Telefon: {esc(SITE['phone_display'] or SITE['phone'])}" if SITE["phone"] else ""
    page["body"] = f"""
{page_hero(page, "Rechtliches", "Datenschutzerklärung", "Der Schutz Ihrer persönlichen Daten – insbesondere Ihrer Gesundheitsdaten – ist mir ein besonderes Anliegen.", ctas=False)}
<section class="section-sm"><div class="container narrow"><div class="glass panel prose">
<h2>1. Verantwortliche</h2>
<p>{SITE["owner"]}, {SITE["practice"]}<br>{SITE["street"]}, {SITE["zip"]} {SITE["city"]}<br>E-Mail: <a href="mailto:{SITE["email"]}">{SITE["email"]}</a>{phone}</p>

<h2>2. Grundsätzliches</h2>
<p>Diese Website kommt ohne Cookies, ohne Tracking- oder Analyse-Tools, ohne Social-Media-Plugins und ohne eingebettete Inhalte Dritter aus. Schriftarten werden lokal von diesem Server geladen; es findet keine Verbindung zu Google Fonts oder anderen Schriftanbietern statt.</p>

<h2>3. Hosting und Server-Logfiles</h2>
<p>Beim Aufruf dieser Website verarbeitet der Hosting-Anbieter automatisch Informationen, die Ihr Browser übermittelt (sog. Server-Logfiles): IP-Adresse, Datum und Uhrzeit des Zugriffs, aufgerufene Seite, Referrer-URL, Browsertyp und Betriebssystem. Die Verarbeitung erfolgt zur Gewährleistung eines sicheren und stabilen Betriebs der Website auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO.</p>
<p>Diese Website wird bei GitHub Pages gehostet, einem Dienst der GitHub B.V., Prins Bernhardplein 200, 1097 JB Amsterdam, Niederlande (Muttergesellschaft: GitHub, Inc., USA). Dabei kann eine Übermittlung von Daten in die USA nicht ausgeschlossen werden. GitHub, Inc. ist unter dem EU-US Data Privacy Framework zertifiziert. Weitere Informationen: <a href="https://docs.github.com/de/site-policy/privacy-policies/github-general-privacy-statement" target="_blank" rel="noopener">Datenschutzerklärung von GitHub</a>.</p>

<h2>4. Kontaktaufnahme und Terminanfrage</h2>
<p>Wenn Sie mich per E-Mail oder über das Terminanfrage-Formular kontaktieren, öffnet sich Ihr eigenes E-Mail-Programm; es werden keine Daten über diese Website an einen Server übertragen. Die von Ihnen per E-Mail übermittelten Daten (z. B. Name, E-Mail-Adresse, Telefonnummer, Ihr Anliegen) verarbeite ich zur Bearbeitung Ihrer Anfrage und zur Terminvereinbarung auf Grundlage von Art. 6 Abs. 1 lit. b DSGVO (vorvertragliche Maßnahmen). Soweit Sie Gesundheitsdaten mitteilen, erfolgt die Verarbeitung auf Grundlage von Art. 9 Abs. 2 lit. h DSGVO.</p>
<p><strong>Hinweis:</strong> Die Kommunikation per E-Mail ist in der Regel unverschlüsselt. Bitte übermitteln Sie keine ausführlichen Gesundheitsdaten per E-Mail; diese besprechen wir persönlich.</p>

<h2>5. Externe Links</h2>
<p>Für die Routenplanung wird ein Link zu Google Maps angeboten. Erst wenn Sie diesen Link anklicken, werden Sie zur Website von Google weitergeleitet; ab dann gilt die Datenschutzerklärung von Google. Auf dieser Website selbst wird keine Karte eingebunden.</p>

<h2>6. Speicherdauer</h2>
<p>Personenbezogene Daten werden nur so lange gespeichert, wie es für den jeweiligen Zweck erforderlich ist oder gesetzliche Aufbewahrungsfristen bestehen. Die Behandlungsdokumentation wird gemäß § 630f BGB grundsätzlich zehn Jahre nach Abschluss der Behandlung aufbewahrt.</p>

<h2>7. Ihre Rechte</h2>
<p>Sie haben im Rahmen der gesetzlichen Voraussetzungen das Recht auf Auskunft (Art. 15 DSGVO), Berichtigung (Art. 16), Löschung (Art. 17), Einschränkung der Verarbeitung (Art. 18), Datenübertragbarkeit (Art. 20) sowie Widerspruch gegen die Verarbeitung (Art. 21 DSGVO). Eine erteilte Einwilligung können Sie jederzeit mit Wirkung für die Zukunft widerrufen.</p>

<h2>8. Beschwerderecht</h2>
<p>Sie haben das Recht, sich bei einer Datenschutzaufsichtsbehörde zu beschweren. Zuständig ist: Der Landesbeauftragte für den Datenschutz und die Informationsfreiheit Rheinland-Pfalz, Hintere Bleiche 34, 55116 Mainz, <a href="https://www.datenschutz.rlp.de" target="_blank" rel="noopener">www.datenschutz.rlp.de</a>.</p>

<h2>9. Patientendaten in der Praxis</h2>
<p>Informationen zur Verarbeitung Ihrer Daten im Rahmen der Behandlung finden Sie in der <a href="{{{{rel:patientenformulare/datenschutzinformation/}}}}">Datenschutzinformation für Patientinnen und Patienten</a>.</p>
<p class="small muted">Stand: {date.today().strftime("%m/%Y")}</p>
</div></div></section>
"""
    page["schema"] = []
    return page


def line(label):
    return f'<p class="line"><span>{label}:</span><span></span></p>'


def boxes(items):
    return "<ul class=\"boxes\">" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def page_forms():
    page = {
        "path": "patientenformulare/",
        "title": "Patientenformulare – Anamnesebogen & mehr | Dr. Schick",
        "description": "Patientenformulare zum Ausdrucken: Anamnesebogen und Datenschutzinformation nach Art. 13 DSGVO für Ihren Termin bei Dr. Karina Schick in Westerburg.",
        "crumbs": [("Start", ""), ("Patientenformulare", "patientenformulare/")],
    }
    p = page["path"]
    page["body"] = f"""
{page_hero(page, "Service", "Patientenformulare", "Sparen Sie Zeit bei Ihrem Termin: Drucken Sie die Formulare aus und bringen Sie sie ausgefüllt mit. Die Aufklärung und Einwilligung zu Ihrer konkreten Behandlung erfolgt persönlich in der Praxis.", ctas=False)}
<section class="section-sm"><div class="container grid grid-2">
  <a class="card glass" href="{rel(p, "patientenformulare/anamnesebogen/")}"><span class="icon-drop">{ICONS["check"]}</span><h2 style="font-size:1.7rem">Anamnesebogen</h2><p>Medizinische Angaben und Behandlungswunsch – bitte vor dem ersten Termin ausfüllen.</p><span class="more">Öffnen &amp; drucken</span></a>
  <a class="card glass" href="{rel(p, "patientenformulare/datenschutzinformation/")}"><span class="icon-drop">{ICONS["mail"]}</span><h2 style="font-size:1.7rem">Datenschutzinformation</h2><p>Information über die Verarbeitung Ihrer Patientendaten nach Art. 13 DSGVO.</p><span class="more">Öffnen &amp; drucken</span></a>
</div></section>
"""
    page["schema"] = []
    return page


def form_header(title, sub):
    return f"""<div class="no-print btn-row" style="margin-bottom:20px"><button class="btn" type="button" onclick="window.print()">Drucken / als PDF speichern</button></div>
<p class="brand" style="display:inline-flex"><span class="brand-name">Schick</span><span class="brand-sub">Medical Aesthetics</span></p>
<p class="small muted">{SITE["owner"]} · {SITE["practice"]} · {SITE["street"]} · {SITE["zip"]} {SITE["city"]} · {SITE["email"]}</p>
<h2 style="border:0;margin-top:.6em">{title}</h2><p>{sub}</p>"""


def page_anamnesis():
    page = {
        "path": "patientenformulare/anamnesebogen/",
        "title": "Anamnesebogen zum Ausdrucken | Dr. Karina Schick",
        "description": "Anamnesebogen der Heilpraktikerpraxis für Naturheilkunde und ästhetische Medizin Dr. Karina Schick zum Ausdrucken und Ausfüllen.",
        "crumbs": [("Start", ""), ("Patientenformulare", "patientenformulare/"), ("Anamnesebogen", "patientenformulare/anamnesebogen/")],
        "noindex": True,
    }
    yn = '<p>☐ Nein &nbsp; ☐ Ja</p>'
    page["body"] = f"""
{page_hero(page, "Patientenformular", "Anamnesebogen", "Heilpraktikerpraxis für Naturheilkunde und ästhetische Medizin", ctas=False)}
<section class="section-sm"><div class="container narrow"><div class="glass panel form-sheet">
{form_header("Anamnesebogen", "Bitte beantworten Sie die Fragen vollständig und wahrheitsgemäß. Alle Angaben werden vertraulich behandelt und dienen der sicheren Planung und Durchführung Ihrer Behandlung.")}
<h2>1. Persönliche Daten</h2>
{line("Vorname")}{line("Nachname")}{line("Geburtsdatum")}{line("Anschrift")}{line("PLZ / Ort")}{line("Telefon")}{line("E-Mail")}
<h2>2. Behandlungswunsch</h2>
<p>Was möchten Sie behandeln lassen?</p>
{boxes(["Falten", "Stirn", "Zornesfalte", "Krähenfüße", "Lippen", "Nasolabialbereich", "Marionettenfalten", "Wangen", "Kinn", "Jawline / Gesichtskontur", "Hautqualität / Hautstruktur", "Narben", "Akne", "Pigmentstörungen", "Sonstiges: ____________"])}
<p>Was möchten Sie durch die Behandlung erreichen?</p><div class="lines"></div>
<p>Was ist Ihnen bei der Behandlung besonders wichtig?</p><div class="lines"></div>
<h2>3. Vorerkrankungen</h2>
<p>Bestehen oder bestanden relevante Erkrankungen?</p>
{boxes(["Nein", "Herz-/Kreislauferkrankung", "Bluthochdruck", "Diabetes mellitus", "Blutgerinnungsstörung", "Thrombose / Embolie", "Autoimmunerkrankung", "Immunschwäche", "Lebererkrankung", "Nierenerkrankung", "Schilddrüsenerkrankung", "neurologische Erkrankung", "Epilepsie", "Hauterkrankung", "Wundheilungsstörung", "Keloidneigung", "Sonstige"])}
{line("Welche?")}
<h2>4. Allergien / Unverträglichkeiten</h2>
{boxes(["Keine bekannt", "Medikamente", "Lokalanästhetika", "Latex", "Desinfektionsmittel", "Pflaster / Klebematerial", "Kosmetika", "Sonstige"])}
{line("Welche und welche Reaktion?")}
<h2>5. Medikamente</h2>
<p>Nehmen Sie regelmäßig Medikamente ein?</p>{yn}
<table><tr><th>Medikament / Präparat</th><th>Dosierung</th><th>Einnahmegrund</th></tr><tr><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td></tr></table>
<p style="margin-top:14px">Blutgerinnungshemmende Medikamente / Präparate?</p>{yn}{line("Welche?")}
{line("Nahrungsergänzungsmittel / pflanzliche Präparate")}
<h2>6. Haut und aktueller Gesundheitszustand</h2>
<p>Besteht aktuell:</p>
{boxes(["keine Besonderheit", "akute Infektion", "Entzündung", "offene Wunde", "Herpes", "Akne", "Ekzem / Neurodermitis", "Psoriasis", "Hautreizung", "sonstige Hautveränderung"])}
{line("Weitere Angaben")}
<p>Besteht aktuell eine Infektion oder Erkrankung?</p>{yn}{line("Welche?")}
<h2>7. Wundheilung</h2>
<p>Hatten Sie bereits Probleme mit der Wundheilung?</p>{yn}
<p>Neigen Sie zu auffälliger Narbenbildung / Keloiden?</p>{yn}
<h2>8. Schwangerschaft / Stillzeit</h2>
<p>Sind Sie schwanger?</p><p>☐ Nein &nbsp; ☐ Ja &nbsp; ☐ Unklar</p>
<p>Besteht die Möglichkeit einer Schwangerschaft?</p>{yn}
<p>Stillen Sie?</p>{yn}
<h2>9. Frühere ästhetische Behandlungen</h2>
<p>Wurden bereits ästhetische Behandlungen durchgeführt?</p>{yn}
{boxes(["Hyaluronsäure / Filler", "Botulinumtoxin", "PRP / Eigenblut", "Fadenlifting", "Microneedling", "Peeling", "Laser / IPL", "Sonstige"])}
{line("Wann und wo wurde zuletzt behandelt?")}{line("Welche Präparate (soweit bekannt)?")}
<p>Sind aktuell Filler, Implantate oder andere Fremdmaterialien im Behandlungsbereich vorhanden?</p><p>☐ Nein &nbsp; ☐ Ja &nbsp; ☐ Unbekannt</p>{line("Wo?")}
<h2>10. Weitere wichtige Angaben</h2>
<p>Gibt es weitere gesundheitliche Informationen, die für Ihre Behandlung wichtig sein könnten?</p><div class="lines"></div>
<h2>Erklärung</h2>
<p>Ich bestätige, dass ich die Angaben vollständig und wahrheitsgemäß gemacht habe. Ich informiere die Praxis über relevante Änderungen meines Gesundheitszustandes, meiner Medikation oder andere für die Behandlung wesentliche Umstände.</p>
{line("Ort / Datum")}{line("Unterschrift Patient/in")}{line("Von der Praxis geprüft am")}
</div></div></section>
"""
    page["schema"] = []
    return page


def page_patient_privacy():
    page = {
        "path": "patientenformulare/datenschutzinformation/",
        "title": "Datenschutzinformation für Patienten | Dr. Schick",
        "description": "Informationen zur Verarbeitung personenbezogener Daten von Patientinnen und Patienten gemäß Art. 13 DSGVO in der Praxis Dr. Karina Schick.",
        "crumbs": [("Start", ""), ("Patientenformulare", "patientenformulare/"), ("Datenschutzinformation", "patientenformulare/datenschutzinformation/")],
        "noindex": True,
    }
    li = lambda xs: "<ul>" + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"
    page["body"] = f"""
{page_hero(page, "Patientenformular", "Datenschutzinformation für Patientinnen und Patienten", "Informationen zur Verarbeitung personenbezogener Daten gemäß Art. 13 DSGVO", ctas=False)}
<section class="section-sm"><div class="container narrow"><div class="glass panel prose form-sheet">
{form_header("Datenschutzinformation", "Sehr geehrte Patientin, sehr geehrter Patient, der Schutz Ihrer persönlichen und gesundheitlichen Daten ist mir wichtig. Nachfolgend informiere ich Sie darüber, welche personenbezogenen Daten ich im Rahmen Ihrer Behandlung verarbeite und zu welchen Zwecken.")}
<h2>1. Verantwortliche</h2>
<p>{SITE["owner"]}, Heilpraktikerin – {SITE["practice"]}<br>{SITE["street"]}, {SITE["zip"]} {SITE["city"]}<br>E-Mail: {SITE["email"]}</p>
<h2>2. Welche Daten verarbeite ich?</h2>
{li(["Stammdaten und Kontaktdaten", "Geburtsdatum", "Anamneseangaben und Gesundheitsdaten", "Angaben zu Vorerkrankungen, Medikamenten, Allergien und Unverträglichkeiten", "Untersuchungs- und Befunddaten", "Angaben zu durchgeführten Behandlungen und verwendeten Präparaten", "Behandlungs- und Verlaufsdokumentation", "Rechnungs- und Zahlungsdaten", "gegebenenfalls medizinische Fotografien zur Behandlungsdokumentation"])}
<p>Gesundheitsdaten sind besondere Kategorien personenbezogener Daten im Sinne von Art. 9 DSGVO.</p>
<h2>3. Zwecke der Verarbeitung</h2>
{li(["Durchführung und Dokumentation Ihrer Behandlung", "Anamnese und Befunderhebung", "Planung und Durchführung ästhetischer Behandlungen", "Verlaufskontrolle und Nachsorge", "Kommunikation mit Ihnen im Zusammenhang mit Ihrer Behandlung", "Terminverwaltung", "Abrechnung und Zahlungsabwicklung", "Erfüllung gesetzlicher Dokumentations- und Aufbewahrungspflichten", "Wahrnehmung oder Verteidigung rechtlicher Ansprüche"])}
<h2>4. Rechtsgrundlage</h2>
<p>Die Verarbeitung erfolgt – abhängig vom jeweiligen Verarbeitungsvorgang – auf Grundlage der DSGVO und des BDSG, insbesondere Art. 6 Abs. 1 lit. b und c sowie Art. 9 Abs. 2 lit. h DSGVO. Gesundheitsdaten dürfen verarbeitet werden, wenn dies für die medizinische Versorgung bzw. Behandlung erforderlich ist und entsprechende Geheimhaltungspflichten bestehen.</p>
<h2>5. Empfänger Ihrer Daten</h2>
<p>Ihre Daten werden grundsätzlich vertraulich behandelt. Eine Weitergabe kann – soweit erforderlich und rechtlich zulässig – erfolgen an:</p>
{li(["Steuerberatung / Buchhaltung", "Abrechnungsdienstleister", "IT- und Praxissoftwaredienstleister (Auftragsverarbeiter)", "Labore, soweit Laboruntersuchungen beauftragt werden", "Apotheken, soweit individuelle Infusionslösungen hergestellt werden", "Behörden oder Gerichte, soweit eine gesetzliche Verpflichtung besteht", "andere Behandler oder medizinische Einrichtungen, soweit dies für Ihre Behandlung erforderlich und rechtlich zulässig ist"])}
<h2>6. Aufbewahrung</h2>
<p>Nach § 630f BGB ist die Behandlungsakte grundsätzlich zehn Jahre nach Abschluss der Behandlung aufzubewahren, soweit keine anderen Vorschriften längere Aufbewahrungsfristen vorsehen.</p>
<h2>7. Ihre Rechte</h2>
{li(["Auskunft über Ihre personenbezogenen Daten", "Berichtigung unrichtiger Daten", "Löschung, soweit die gesetzlichen Voraussetzungen erfüllt sind", "Einschränkung der Verarbeitung", "Datenübertragbarkeit, soweit anwendbar", "Widerspruch gegen bestimmte Verarbeitungen", "Beschwerde bei einer Datenschutzaufsichtsbehörde"])}
<p>Sie können außerdem Einsicht in Ihre vollständige Behandlungsakte verlangen (§ 630g BGB).</p>
<h2>8. Widerruf einer Einwilligung</h2>
<p>Soweit eine Datenverarbeitung auf Ihrer Einwilligung beruht, können Sie diese jederzeit mit Wirkung für die Zukunft widerrufen. Die Rechtmäßigkeit der bis zum Widerruf erfolgten Verarbeitung bleibt hiervon unberührt.</p>
<h2>9. Zuständige Datenschutzaufsichtsbehörde</h2>
<p>Der Landesbeauftragte für den Datenschutz und die Informationsfreiheit Rheinland-Pfalz, Hintere Bleiche 34, 55116 Mainz</p>
<p>Stand: {date.today().strftime("%m/%Y")}</p>
{line("Ort / Datum")}{line("Unterschrift Patient/in – Erhalt der Information")}
</div></div></section>
"""
    page["schema"] = []
    return page


def page_404():
    page = {
        "path": "404/",
        "title": "Seite nicht gefunden | Dr. Karina Schick",
        "description": "Die angeforderte Seite wurde nicht gefunden.",
        "noindex": True,
    }
    page["body"] = """
<section class="page-hero"><div class="container center">
<p class="eyebrow">Fehler 404</p>
<h1 style="margin-inline:auto">Diese Seite ist wie ein Wassertropfen verdunstet</h1>
<p class="lead">Die gewünschte Seite existiert leider nicht (mehr). Hier geht es weiter:</p>
<div class="btn-row"><a class="btn" href="/">Zur Startseite</a><a class="btn btn-ghost" href="/leistungen/">Leistungen</a><a class="btn btn-ghost" href="/termin-buchen/">Termin buchen</a></div>
</div></section>"""
    page["schema"] = []
    return page


# ---------------------------------------------------------------------------
# Zusatzdateien
# ---------------------------------------------------------------------------
def write_sitemap(pages):
    urls = []
    for pg in pages:
        if pg.get("noindex"):
            continue
        prio = "1.0" if pg["path"] == "" else ("0.9" if pg["path"].startswith("leistungen/") or pg["path"] in ("termin-buchen/", "preise/") else "0.7")
        if pg["path"] in ("impressum/", "datenschutz/"):
            prio = "0.2"
        img = ""
        if pg["path"] in ("", "ueber-mich/"):
            img = f"<image:image><image:loc>{absurl('assets/img/dr-karina-schick.jpg')}</image:loc></image:image>"
        urls.append(f"  <url><loc>{absurl(pg['path'])}</loc><lastmod>{TODAY}</lastmod><priority>{prio}</priority>{img}</url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
           + "\n".join(urls) + "\n</urlset>\n")
    (OUT / "sitemap.xml").write_text(xml, encoding="utf-8")


def write_extras(pages):
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE['url']}/sitemap.xml\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    manifest = {
        "name": SITE["brand"], "short_name": "Schick", "lang": "de", "start_url": "/", "display": "browser",
        "background_color": "#f6f4f1", "theme_color": "#f6f4f1",
        "icons": [{"src": "/assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}],
    }
    (OUT / "site.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    # llms.txt – kompakte Zusammenfassung für KI-Suchmaschinen
    lines = [f"# {SITE['brand']} – {SITE['owner']}", "",
             f"> {SITE['owner']} ist {SITE['profession']} mit 25 Jahren Erfahrung als Zahnärztin (Schwerpunkte ästhetische Zahnmedizin, Prothetik, Chirurgie). "
             f"Praxis für ästhetische Medizin und Naturheilkunde: {SITE['street']}, {SITE['zip']} {SITE['city']} ({SITE['region_short']}, {SITE['region']}). "
             f"Kontakt: {SITE['email']}. {SITE['hours']}.", "", "## Leistungen", ""]
    for s in SERVICES:
        lines.append(f"- [{s['name']}]({absurl('leistungen/' + s['slug'] + '/')}): {s['description']}")
    lines += ["", "## Wichtige Seiten", "",
              f"- [Preise]({absurl('preise/')}): Orientierungspreise aller Behandlungen",
              f"- [Termin buchen]({absurl('termin-buchen/')}): Erstgespräch oder telefonische Beratung anfragen",
              f"- [Häufige Fragen]({absurl('faq/')})",
              f"- [Über mich]({absurl('ueber-mich/')})",
              f"- [Kontakt]({absurl('kontakt/')})", ""]
    (OUT / "llms.txt").write_text("\n".join(lines), encoding="utf-8")
    # 404 auf oberster Ebene (GitHub Pages erwartet /404.html)
    src404 = OUT / "404" / "index.html"
    if src404.exists():
        (OUT / "404.html").write_text(src404.read_text(encoding="utf-8"), encoding="utf-8")
        shutil.rmtree(OUT / "404")


def build():
    if OUT.exists():
        cname = (OUT / "CNAME").read_text() if (OUT / "CNAME").exists() else None
        shutil.rmtree(OUT)
    else:
        cname = None
    OUT.mkdir(parents=True)
    if cname:
        (OUT / "CNAME").write_text(cname)
    shutil.copytree(SRC / "assets", OUT / "assets")

    pages = [page_home(), page_about(), page_services()]
    pages += [page_service(s) for s in SERVICES]
    pages += [page_prices(), page_appointment(), page_faq(), page_booking(), page_contact(),
              page_forms(), page_anamnesis(), page_patient_privacy(), page_imprint(), page_privacy(), page_404()]

    for pg in pages:
        assert len(pg["description"]) <= 160, (pg["path"], len(pg["description"]))
        target = OUT / pg["path"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(pg), encoding="utf-8")
    write_sitemap(pages)
    write_extras(pages)
    print(f"{len(pages)} Seiten erzeugt in {OUT}")
    for pg in pages:
        print(f"  /{pg['path']:<50} {len(pg['title']):>3} Z. Titel | {len(pg['description']):>3} Z. Beschreibung")


if __name__ == "__main__":
    build()
