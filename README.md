# Schick Medical Aesthetics – Website

Website für **Dr. Karina Schick, Zahnärztin & Heilpraktikerin**, Praxis für Heilkunde, Schloß Westerburg.
Ziel-Domain: <https://www.schick-aesthetik.de>

Eine schnelle, statische Website ohne Baukasten, ohne Cookies und ohne Tracking. Die fertigen Seiten liegen im Ordner **`docs/`**.

## Was drin ist

- **23 Seiten mit sauberen Permalinks**, z. B. `/leistungen/hyaluron-faltenbehandlung/`, `/preise/`, `/termin-buchen/`
- **Wassertropfen-Hintergrund**: eigens gerenderte, realistische Tropfen (`tools/make_drops.py`), keine Stockfotos
- **SEO**: eigener Meta-Title (≤ 60 Zeichen) und eigene Meta-Description (≤ 160 Zeichen) pro Seite, Canonical, Open Graph und Twitter-Card mit Vorschaubild, genau eine H1 pro Seite und eine saubere H2/H3-Struktur
- **Schema.org (JSON-LD)**: `MedicalBusiness`/`HealthAndBeautyBusiness`, `Person`, `WebSite`, `BreadcrumbList`, `Service` mit Preisen, `FAQPage`, `OfferCatalog`
- **`sitemap.xml`**, **`robots.txt`**, **`llms.txt`** (für KI-Suchen), Web-Manifest und Favicons
- **Terminbuchung**: Auf jeder Seite gibt es die Buttons „Termin buchen“ und „Telefonische Beratung“. Auf Leistungsseiten ist die Behandlung im Formular schon vorausgewählt. Auf dem Handy gibt es zusätzlich eine feste Aktionsleiste am unteren Rand.
- **Datenschutz**: Schriften sind lokal eingebunden (keine Google Fonts) und es gibt keine eingebettete Google-Karte, nur einen Link dorthin.
- **Patientenformulare** zum Ausdrucken: Anamnesebogen und Datenschutzinformation nach Art. 13 DSGVO
- Impressum, Datenschutzerklärung und eine 404-Seite

## Inhalte ändern

Alle Texte, Preise und Kontaktdaten stehen in **`content.py`**. Danach einmal neu bauen:

```bash
python3 build.py
```

Die wichtigsten Schalter oben in `content.py`:

| Feld | Wirkung |
|---|---|
| `phone` / `phone_display` | Sobald eine Nummer eingetragen ist, erscheinen überall automatisch „Anrufen“-Buttons. |
| `whatsapp` | Blendet einen WhatsApp-Button ein (z. B. `491701234567`). |
| `booking_url` | Link zu einem Online-Kalender (Doctolib, Calendly …). Alle „Termin buchen“-Buttons führen dann direkt dorthin. |

Die Grafiken lassen sich bei Bedarf neu erzeugen: `python3 tools/make_drops.py` und `node tools/make_brand_assets.js`.

## Veröffentlichen

**GitHub Pages:** Repository → *Settings → Pages* → *Deploy from a branch* → Branch wählen, Ordner **`/docs`**.
Für die eigene Domain eine Datei `docs/CNAME` mit dem Inhalt `www.schick-aesthetik.de` anlegen und beim Domain-Anbieter einen CNAME-Eintrag auf `<benutzername>.github.io` setzen.

**Hostinger (Git-Verbindung):** Das Repository wird komplett nach `public_html` geladen. Die Datei `.htaccess` im Hauptordner leitet alle Aufrufe intern auf `docs/` um. So funktionieren die sauberen Adressen, und Quellcode-Dateien sind nicht abrufbar. Wichtig: Bei Hostinger muss das Installationsverzeichnis **leer** bleiben (also direkt `public_html`).

**Anderer Webspace (z. B. IONOS, Strato):** einfach den *Inhalt* von `docs/` per FTP hochladen.

Danach die Sitemap in der **Google Search Console** einreichen und ein **Google-Unternehmensprofil** anlegen. Das ist wichtig für die lokale Suche.

## Bitte vor dem Livegang prüfen ⚠️

1. **„Bio-Botox“**: Das genaue Präparat bzw. den Wirkstoff benennen. Botulinumtoxin ist verschreibungspflichtig, und für verschreibungspflichtige Arzneimittel ist Publikumswerbung verboten (§ 10 HWG). Die Preispositionen Masseter, Bruxismus und Hyperhidrose sind klassische Botulinum-Anwendungen. Bitte rechtlich prüfen, ob sie so auf der Seite stehen dürfen.
2. **Rechtstexte** (Impressum, Datenschutz, Pflichthinweise zur Naturheilkunde) von einer Anwältin oder einem Anwalt bzw. einem Abmahnschutz-Dienst prüfen lassen. Das gilt auch für die Frage, ob für die Berufsbezeichnung „Zahnärztin“ zusätzlich die Zahnärztekammer im Impressum stehen muss.
3. **Ergänzte Texte**: Für Infusionen (beispielhafte Inhaltsstoffe), Akupunktur, Eigenblut, Labordiagnostik und Lipolyse gab es keine Vorlage. Diese Texte habe ich vorsichtig formuliert. Bitte fachlich gegenlesen.
4. **Telefonnummer** eintragen, sobald sie vorhanden ist.
5. **Fortbildungen und Zertifikate** auf „Über mich“ ergänzen. Das schafft Vertrauen.
6. **Preise**: Profhilo® „Hände 550 €“ wurde als eigene Position übernommen. Bitte prüfen.
7. **Laserbehandlung**: Es gibt noch keine Detailseite, weil die Informationen fehlen.
8. **Logo**: Aktuell ist eine Text-Wortmarke im Logo-Stil umgesetzt. Sobald das Logo als Datei vorliegt (SVG oder PNG mit transparentem Hintergrund), kann es eingesetzt werden.

**Bewusst nicht veröffentlicht:** Steuernummer, Steuer-ID, Kontonummer und die Privatadresse.
