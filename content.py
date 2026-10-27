"""Inhalte der Website – hier werden Texte, Preise und Kontaktdaten gepflegt.

Nach einer Änderung:  python3 build.py   (erzeugt den Ordner docs/ neu)
"""

# ---------------------------------------------------------------------------
# Stammdaten
# ---------------------------------------------------------------------------
SITE = {
    "url": "https://www.schick-aesthetik.de",  # ohne Schrägstrich am Ende
    "brand": "Schick Medical Aesthetics",
    "brand_short": "Schick",
    "owner": "Dr. Karina Schick",
    "practice": "Praxis für Heilkunde",
    "claim": "Präzision · Ästhetik · Gesundheit",
    "profession": "Zahnärztin & Heilpraktikerin",
    "email": "praxis@schick-aesthetik.de",
    # Telefonnummer eintragen, sobald vorhanden (z. B. "+49 2663 123456").
    # Solange leer, werden Anruf-Buttons automatisch ausgeblendet.
    "phone": "",
    "phone_display": "",
    # WhatsApp-Nummer im internationalen Format ohne +, z. B. "491701234567" (leer = aus)
    "whatsapp": "",
    # Externes Online-Buchungstool (z. B. Doctolib, Calendly, Planity).
    # Leer = Terminanfrage-Formular auf /termin-buchen/ wird genutzt.
    "booking_url": "",
    "street": "Schloß Westerburg",
    "zip": "56457",
    "city": "Westerburg",
    "region": "Rheinland-Pfalz",
    "region_short": "Westerwald",
    "country": "DE",
    "maps_url": "https://www.google.com/maps/search/?api=1&query=Schlo%C3%9F+Westerburg%2C+56457+Westerburg",
    "hours": "Termine nach Vereinbarung",
    "payment": ["Bar", "EC-Karte", "PayPal"],
    "area_served": ["Westerburg", "Westerwaldkreis", "Montabaur", "Hachenburg", "Bad Marienberg", "Rennerod", "Limburg an der Lahn", "Wallmerod"],
    "authority": "Kreisverwaltung des Westerwaldkreises – Gesundheitsamt, Peter-Altmeier-Platz 1, 56410 Montabaur",
}

# ---------------------------------------------------------------------------
# Preise (Orientierungspreise aus der Preisinformation)
# ---------------------------------------------------------------------------
PRICES = {
    "infusionen": {
        "title": "Infusionen",
        "items": [
            ("Vitamin-Infusion", "ab 120 €"),
            ("Immun-Boost", "ab 150 €"),
            ("Energy-Cocktail", "ab 200 €"),
            ("Detox & Anti-Aging", "ab 250 €"),
        ],
        "note": "Zzgl. Rechnung der Apotheke für die individuell hergestellte Infusionslösung.",
    },
    "hyaluron": {
        "title": "Faltenunterspritzung mit Hyaluronsäure & Lippen",
        "items": [
            ("Lippenunterspritzung", "ab 400 €"),
            ("Nasolabialfalte", "ab 400 €"),
            ("Marionettenfalten", "ab 400 €"),
            ("Jawline / Kieferkontur", "ab 400 €"),
            ("Wangenaufbau", "ab 400 €"),
        ],
    },
    "biostimulatoren": {
        "title": "Biostimulatoren & Skinbooster",
        "items": [
            ("Polynukleotide – Gesicht", "ab 400 €"),
            ("Polynukleotide – Augenpartie", "ab 300 €"),
            ("Profhilo® (Gesicht, Hals oder Dekolleté)", "1 Areal 300 €"),
            ("Profhilo® Structura", "1 Areal 500 €"),
            ("Profhilo® – Hände", "550 €"),
        ],
        "note": "Ein Areal ist z. B. das gesamte Gesicht, der Hals oder das Dekolleté. Wird innerhalb einer Sitzung ein weiteres Areal behandelt, wird ein Aufpreis pro Areal berechnet. Profhilo® und Profhilo® Structura werden in zwei Terminen im Abstand von 2–4 Wochen durchgeführt.",
    },
    "microneedling": {
        "title": "Microneedling & Mesotherapie",
        "items": [
            ("Gesicht", "ab 350 €"),
            ("Hals / Dekolleté", "ab 400 €"),
            ("Gesicht, Hals & Dekolleté", "ab 600 €"),
            ("Mesotherapie bei Haarausfall – pro Sitzung", "500 €"),
        ],
    },
    "lipolyse": {
        "title": "Lipolyse („Fett-weg-Spritze“)",
        "items": [
            ("PB Serum – Kinn", "300 €"),
            ("PB Serum – Gesicht", "400 €"),
            ("PB Serum – Bauch", "ab 400 €"),
            ("PB Serum – Körper", "ab 500 €"),
            ("Suisselle Cellbooster® Shape – Gesicht (3 ml)", "ab 400 €"),
        ],
    },
    "biobotox": {
        "title": "„Bio-Botox“",
        "items": [
            ("Eine Zone", "150 €"),
            ("Zwei Zonen", "300 €"),
            ("Drei Zonen", "400 €"),
            ("Full Face", "500 €"),
            ("Nofretete-Lift (Hals & Jawline)", "400 €"),
            ("Gesicht & Hals komplett", "600 €"),
            ("Masseter (Gesichtsverschmälerung)", "400 €"),
            ("Bruxismus (Zähneknirschen)", "400 €"),
            ("Hyperhidrose (starkes Schwitzen)", "400 €"),
        ],
    },
}

PRICE_INTRO = (
    "Transparenz und eine individuelle Beratung liegen mir besonders am Herzen. Die nachfolgend genannten Preise dienen "
    "ausschließlich der Orientierung. Die endgültigen Kosten kann ich erst nach einem persönlichen Beratungsgespräch "
    "festlegen, da sich der Preis nach benötigter Menge, Aufwand, Anzahl der Sitzungen und Ihren persönlichen Wünschen richtet. "
    "Als Zahnärztin und Heilpraktikerin lege ich großen Wert auf höchste Qualität und arbeite ausschließlich mit sorgfältig "
    "ausgewählten, hochwertigen Produkten und Materialien."
)

# ---------------------------------------------------------------------------
# Leistungen
# group: "aesthetik" oder "naturheilkunde"
# ---------------------------------------------------------------------------
SERVICES = [
    {
        "slug": "hyaluron-faltenbehandlung",
        "group": "aesthetik",
        "icon": "drop",
        "nav": "Hyaluron & Lippen",
        "name": "Hyaluron-Faltenbehandlung & Lippenunterspritzung",
        "card": "Sanfte Faltenglättung, harmonische Lippen und Konturen – mit gut verträglicher Hyaluronsäure.",
        "tags": ["Lippen", "Nasolabialfalte", "Jawline", "Wangen"],
        "title": "Hyaluron & Lippenunterspritzung in Westerburg | Dr. Schick",
        "description": "Faltenunterspritzung mit Hyaluronsäure, Lippen, Jawline & Wangenaufbau in Westerburg (Westerwald) – natürlich und harmonisch, mit 25 Jahren Erfahrung.",
        "h1": "Hyaluron-Faltenbehandlung & Lippenunterspritzung in Westerburg",
        "lead": "Dermalfiller auf Basis von Hyaluronsäure können Falten mildern, verloren gegangenes Volumen ausgleichen und Gesichtskonturen sanft betonen – mit dem Ziel, dass Sie frischer aussehen und trotzdem ganz Sie selbst bleiben.",
        "facts": [("Behandlungsdauer", "ca. 30–45 Minuten"), ("Ergebnis", "direkt nach der Behandlung sichtbar"), ("Haltbarkeit", "mehrere Monate, je nach Areal & Produkt"), ("Kosten", "ab 400 €")],
        "service_type": "Faltenunterspritzung mit Hyaluronsäure",
        "body": """
<h2>Was sind Dermalfiller?</h2>
<p>Dermalfiller sind gelartige Füllstoffe, die unter die Haut injiziert werden, um Falten zu glätten und verloren gegangenes Volumen im Gesicht wieder aufzubauen. Ich verwende dafür Hyaluronsäure – einen Stoff, der natürlicherweise im Körper vorkommt, in der Regel sehr gut verträglich ist und nach einigen Monaten vom Körper wieder abgebaut wird.</p>
<h2>Wie wirkt Hyaluronsäure?</h2>
<ul>
<li><strong>Volumenaufbau:</strong> Der Filler unterstützt das Gewebe unter der Haut von innen.</li>
<li><strong>Feuchtigkeit:</strong> Hyaluronsäure bindet Wasser und kann die Haut frischer wirken lassen.</li>
<li><strong>Sofortige Wirkung:</strong> Das Ergebnis ist in der Regel direkt nach der Behandlung sichtbar und entwickelt sich nach Abklingen einer möglichen Schwellung voll.</li>
</ul>
<h2>Für welche Bereiche eignet sich die Behandlung?</h2>
<h3>Falten mildern</h3>
<p>Zum Beispiel Nasolabialfalten (zwischen Nase und Mundwinkel) oder Marionettenfalten, die vom Mundwinkel Richtung Kinn verlaufen und das Gesicht müde oder traurig wirken lassen können.</p>
<h3>Lippen</h3>
<p>Mehr Fülle, Feuchtigkeit und Definition – oder einfach eine ausgeglichene Symmetrie. Mein Ziel sind Lippen, die zu Ihrem Gesicht passen, nicht ein bestimmter Trend.</p>
<h3>Gesichtskontur</h3>
<p>Sanfte Betonung von Wangenknochen, Kinn oder der Kieferlinie (Jawline) für ein harmonisches Gesamtbild.</p>
<h3>Narben</h3>
<p>Eingesunkene Aknenarben können optisch ausgeglichen werden.</p>
<h2>Mein Blick als Zahnärztin</h2>
<p>Seit 25 Jahren arbeite ich täglich mit Proportionen, Symmetrie und der Ästhetik des Mund- und Gesichtsbereichs. Gerade bei Lippen, Mundpartie und Kieferlinie hilft mir dieses Wissen um Anatomie, Zahnstellung und Gesichtsproportionen, Behandlungen besonders präzise und harmonisch zu planen.</p>
<h2>Ablauf der Behandlung</h2>
<ol>
<li><strong>Beratung & Analyse:</strong> Wir besprechen Ihre Wünsche, Möglichkeiten und Grenzen. Ich kläre Sie ausführlich über Wirkung, Risiken und Alternativen auf.</li>
<li><strong>Vorbereitung:</strong> Gründliche Desinfektion; auf Wunsch wird die Region mit einer betäubenden Creme vorbereitet. Viele Präparate enthalten zusätzlich ein Lokalanästhetikum.</li>
<li><strong>Behandlung:</strong> Die Hyaluronsäure wird mit feinen Nadeln oder einer stumpfen Kanüle präzise eingebracht.</li>
<li><strong>Nachsorge:</strong> Sie erhalten individuelle Hinweise für die ersten Tage. Auf Wunsch vereinbaren wir einen Kontrolltermin.</li>
</ol>
<h2>Mögliche Nebenwirkungen</h2>
<p>Direkt nach der Behandlung können Rötungen, Schwellungen, Druckempfindlichkeit oder kleine Blutergüsse auftreten, die in der Regel nach wenigen Tagen abklingen. Seltene Risiken wie Entzündungen, Knötchenbildung oder Gefäßkomplikationen bespreche ich ausführlich mit Ihnen im Aufklärungsgespräch.</p>
<p class="info"><strong>Wichtig:</strong> In Schwangerschaft und Stillzeit, bei akuten Entzündungen oder Herpes im Behandlungsbereich sowie bei bestimmten Vorerkrankungen wird nicht behandelt. Das klären wir gemeinsam anhand des Anamnesebogens.</p>
""",
        "prices": ["hyaluron"],
        "faq": [
            ("Sieht man nach der Behandlung „gemacht“ aus?", "Mein Ziel ist ein natürliches, harmonisches Ergebnis. Ich arbeite lieber behutsam und ergänze bei Bedarf in einem zweiten Termin, statt zu viel auf einmal zu machen."),
            ("Ist die Behandlung schmerzhaft?", "Die meisten Patientinnen und Patienten empfinden die Behandlung als gut auszuhalten. Betäubende Creme und lokalanästhetikahaltige Präparate machen sie deutlich angenehmer."),
            ("Wie lange hält das Ergebnis?", "Das hängt vom Areal, vom Produkt und von Ihrem Stoffwechsel ab – in der Regel mehrere Monate. Die Hyaluronsäure wird vom Körper nach und nach abgebaut."),
        ],
    },
    {
        "slug": "skinbooster-biostimulatoren",
        "group": "aesthetik",
        "icon": "sparkle",
        "nav": "Skinbooster & Biostimulatoren",
        "name": "Skinbooster, Profhilo® & Polynukleotide",
        "card": "Tiefenfeuchtigkeit und Regeneration für mehr Hautqualität – ohne die Gesichtszüge zu verändern.",
        "tags": ["Profhilo®", "Polynukleotide", "Hals & Dekolleté"],
        "title": "Skinbooster, Profhilo® & Polynukleotide | Dr. Schick",
        "description": "Skinbooster, Profhilo® und Polynukleotide in Westerburg: Tiefenhydratation und natürliche Hautverjüngung für Gesicht, Augenpartie, Hals, Dekolleté und Hände.",
        "h1": "Skinbooster & Biostimulatoren in Westerburg",
        "lead": "Für mehr Spannkraft, Feuchtigkeit und einen frischen Glow: Skinbooster und Biostimulatoren verbessern die Hautqualität von innen – ganz ohne künstliches Volumen.",
        "facts": [("Behandlungsdauer", "ca. 15–30 Minuten"), ("Sitzungen", "meist 2–3 im Abstand von 3–4 Wochen"), ("Haltbarkeit", "ca. 4–9 Monate, teils länger"), ("Kosten", "ab 300 €")],
        "service_type": "Skinbooster und Biostimulatoren",
        "body": """
<h2>Skinbooster: Feuchtigkeit aus der Tiefe</h2>
<p>Ein Skinbooster ist eine minimal-invasive Behandlung, bei der feuchtigkeitsspendende Hyaluronsäure flächig in die tieferen Hautschichten eingebracht wird.</p>
<ul>
<li><strong>Tiefenhydratation:</strong> Die Hyaluronsäure bindet Wasser im Gewebe und versorgt die Haut von innen mit Feuchtigkeit.</li>
<li><strong>Kein Volumenaufbau:</strong> Anders als klassische Filler verändert ein Skinbooster nicht die natürlichen Gesichtszüge.</li>
<li><strong>Verbesserte Hautqualität:</strong> Feine Knitterfältchen können geglättet und das Hautbild verfeinert werden – für einen natürlichen Frische-Glow.</li>
<li><strong>Einsatzbereiche:</strong> Gesicht, Hals, Dekolleté und Handrücken.</li>
</ul>
<h2>Profhilo® und Profhilo® Structura</h2>
<p>Profhilo® ist ein bekannter Vertreter der Skinbooster mit besonders hoch konzentrierter Hyaluronsäure. Es verteilt sich gleichmäßig im Gewebe und unterstützt die Haut in ihrer Spannkraft. Profhilo® Structura wurde speziell für tiefere Gewebeschichten entwickelt, etwa im Bereich der seitlichen Gesichtspartie. Beide Behandlungen erfolgen in zwei Terminen im Abstand von 2–4 Wochen.</p>
<h2>Polynukleotide: Regeneration auf Zellebene</h2>
<p>Polynukleotide sind Ketten aus DNA-Bausteinen, die in der ästhetischen Medizin als Biostimulatoren zur natürlichen Hautverjüngung eingesetzt werden. Es handelt sich um hochgereinigte DNA-Fragmente, die meist aus Lachs- oder Forellen-DNA gewonnen werden.</p>
<ul>
<li><strong>Kein klassischer Filler:</strong> Im Gegensatz zu Hyaluronsäure-Fillern wird kein Volumen erzeugt.</li>
<li><strong>Wirkprinzip:</strong> Polynukleotide wirken als Signalmoleküle, die die körpereigene Bildung von Kollagen und Elastin anregen, die Feuchtigkeitsspeicherung verbessern und die Zellregeneration unterstützen sollen.</li>
</ul>
<h3>Anwendungsbereiche</h3>
<ul>
<li><strong>Hautverjüngung:</strong> Milderung feiner Linien und Knitterfältchen.</li>
<li><strong>Empfindliche Zonen:</strong> Besonders geeignet für die dünne Haut um die Augen (z. B. bei Augenringen), am Hals und am Dekolleté.</li>
<li><strong>Hautbild:</strong> Unterstützung bei Aknenarben, Pigmentflecken sowie müder oder strapazierter Haut.</li>
</ul>
<h2>Ablauf der Behandlung</h2>
<p>Das Gel wird mikroinvasiv mit feinen Nadeln direkt unter die Haut eingebracht. Danach entstehen kleine Quaddeln, die nach ein bis zwei Tagen verschwinden. Für ein nachhaltiges Ergebnis empfehle ich bei Polynukleotiden meist eine Kur von etwa drei Behandlungen im Abstand von je drei Wochen, bei Skinboostern 2–3 Sitzungen im Abstand von etwa vier Wochen.</p>
<h2>Haltbarkeit</h2>
<p>Je nach Produkt und Hauttyp hält das Ergebnis etwa 4 bis 9 Monate, teilweise auch 12 bis 18 Monate. Eine Auffrischung ist jederzeit möglich.</p>
<p class="info"><strong>Gut zu wissen:</strong> Die Ergebnisse entwickeln sich schrittweise und wirken natürlich. Kleine Rötungen, Quaddeln oder Blutergüsse sind möglich und klingen in der Regel schnell ab.</p>
""",
        "prices": ["biostimulatoren"],
        "faq": [
            ("Was ist der Unterschied zwischen Skinbooster und Filler?", "Ein Filler baut gezielt Volumen auf (z. B. Lippen, Wangen). Ein Skinbooster verteilt sich flächig und verbessert vor allem die Feuchtigkeit und Qualität der Haut, ohne Konturen zu verändern."),
            ("Bin ich nach der Behandlung gesellschaftsfähig?", "Die kleinen Quaddeln verschwinden meist innerhalb von ein bis zwei Tagen. Planen Sie wichtige Termine am besten nicht direkt am Behandlungstag."),
        ],
    },
    {
        "slug": "microneedling-mesotherapie",
        "group": "aesthetik",
        "icon": "dots",
        "nav": "Microneedling & Mesotherapie",
        "name": "Microneedling & Mesotherapie",
        "card": "Regt die hauteigene Erneuerung an – für ein feineres Hautbild, frischen Teint und bei Haarausfall.",
        "tags": ["Hautbild", "Aknenarben", "Haarausfall"],
        "title": "Microneedling & Mesotherapie in Westerburg | Dr. Schick",
        "description": "Microneedling & Mesotherapie in Westerburg: für ein feineres Hautbild, mildere Aknenarben, frischen Teint und als Mesotherapie bei Haarausfall.",
        "h1": "Microneedling & Mesotherapie in Westerburg",
        "lead": "Microneedling regt die körpereigene Kollagen- und Elastinbildung an, kann das Hautbild verfeinern und sorgt für einen frischeren Teint. In Kombination mit Wirkstoffen sprechen wir von Mesotherapie.",
        "facts": [("Behandlungsdauer", "ca. 45–60 Minuten"), ("Sitzungen", "mehrere, im Abstand von einigen Wochen"), ("Ausfallzeit", "1–3 Tage leichte Rötung"), ("Kosten", "ab 350 €")],
        "service_type": "Microneedling und Mesotherapie",
        "body": """
<h2>Was bewirkt Microneedling?</h2>
<ul>
<li><strong>Kollagen-Stimulation:</strong> Feine Nadeln erzeugen winzige Mikroverletzungen in der Haut, die den natürlichen Regenerationsprozess und die Zellerneuerung aktivieren.</li>
<li><strong>Glattere Hautstruktur:</strong> Das Verfahren kann feine Fältchen, vergrößerte Poren, Aknenarben und Dehnungsstreifen mildern.</li>
<li><strong>Bessere Wirkstoffaufnahme:</strong> Durch die feinen Kanäle können Seren wie Hyaluronsäure oder Vitamin C tiefer in die Haut gelangen.</li>
<li><strong>Ebenmäßiger Teint:</strong> Leichte Pigmentflecken können aufgehellt werden, die Haut wirkt frischer.</li>
</ul>
<h2>Mesotherapie – gezielte Wirkstoffe für Haut und Kopfhaut</h2>
<p>Bei der Mesotherapie werden individuell ausgewählte Wirkstoffkombinationen (z. B. Hyaluronsäure, Vitamine, Aminosäuren) in die oberen Hautschichten eingebracht. Im Gesicht, am Hals und am Dekolleté dient sie der Verbesserung der Hautqualität.</p>
<h3>Mesotherapie bei Haarausfall</h3>
<p>Bei erblich bedingtem oder diffusem Haarausfall kann die Mesotherapie die Kopfhaut mit Wirkstoffen versorgen und die Haarwurzeln unterstützen. Vorab kläre ich mögliche Ursachen ab – bei Bedarf auch mithilfe einer <a href="{{rel:leistungen/labordiagnostik/}}">Laboruntersuchung</a>.</p>
<h2>Ablauf</h2>
<ol>
<li>Reinigung und Desinfektion der Haut, auf Wunsch eine betäubende Creme.</li>
<li>Behandlung mit einem sterilen, professionellen Microneedling-Pen und passenden Wirkstoffen.</li>
<li>Beruhigende Pflege und individuelle Hinweise für die Nachsorge.</li>
</ol>
<h2>Grenzen und Risiken</h2>
<ul>
<li><strong>Schrittweise Ergebnisse:</strong> Die Effekte bauen sich über mehrere Sitzungen auf und wirken dezent – nicht wie ein operativer Eingriff.</li>
<li><strong>Nebenwirkungen:</strong> Direkt nach der Behandlung ist die Haut oft gerötet, leicht geschwollen und empfindlich.</li>
<li><strong>Hygiene:</strong> Ich arbeite ausschließlich mit sterilen Einmal-Nadelmodulen. Von Heimanwendungen mit einfachen Dermarollern rate ich ab, da hier Infektionen und Narben drohen können.</li>
</ul>
<p class="info"><strong>Kombinierbar:</strong> Microneedling lässt sich sehr gut mit <a href="{{rel:leistungen/vampirlifting-prp/}}">Eigenblutplasma (PRP)</a> kombinieren.</p>
""",
        "prices": ["microneedling"],
        "faq": [
            ("Wie viele Sitzungen brauche ich?", "Das hängt von Ihrem Hautbild und Ihrem Ziel ab. Häufig sind 3–4 Sitzungen im Abstand von einigen Wochen sinnvoll. Im Beratungsgespräch erstelle ich Ihnen einen individuellen Plan."),
            ("Wann ist meine Haut wieder „vorzeigbar“?", "Meist ist die Haut 1–3 Tage gerötet, ähnlich einem leichten Sonnenbrand. Make-up sollte erst nach 24 Stunden wieder verwendet werden."),
        ],
    },
    {
        "slug": "vampirlifting-prp",
        "group": "aesthetik",
        "icon": "plasma",
        "nav": "Vampirlifting (PRP)",
        "name": "Vampirlifting / PRP-Eigenbluttherapie",
        "card": "Plättchenreiches Plasma aus Ihrem eigenen Blut – für natürliche Hautregeneration und Kopfhaut.",
        "tags": ["Eigenblut", "Augenringe", "Kopfhaut"],
        "title": "Vampirlifting / PRP-Behandlung in Westerburg | Dr. Schick",
        "description": "Vampirlifting (PRP) in Westerburg: Hautverjüngung mit plättchenreichem Plasma aus dem eigenen Blut – für Gesicht, Hals, Dekolleté, Augenpartie und Kopfhaut.",
        "h1": "Vampirlifting (PRP) in Westerburg",
        "lead": "Beim Vampirlifting wird plättchenreiches Plasma (PRP) aus Ihrem eigenen Blut gewonnen und in die Haut eingebracht – eine natürliche Methode ohne Fremdstoffe.",
        "facts": [("Behandlungsdauer", "ca. 60 Minuten"), ("Blutmenge", "ca. 4–8 ml Eigenblut"), ("Ausfallzeit", "wenige Tage leichte Rötung"), ("Kosten", "nach Beratung")],
        "service_type": "PRP-Eigenbluttherapie (Vampirlifting)",
        "body": """
<h2>Was ist ein Vampirlifting?</h2>
<p>Das Vampirlifting (PRP-Therapie, „Platelet Rich Plasma“) ist eine minimalinvasive Behandlung zur Hautverjüngung, bei der plättchenreiches Plasma aus dem eigenen Blut in die Haut injiziert oder eingearbeitet wird.</p>
<h2>Ablauf der Behandlung</h2>
<ol>
<li><strong>Blutentnahme:</strong> Ich entnehme eine kleine Menge Eigenblut (ca. 4 bis 8 ml).</li>
<li><strong>Zentrifugation:</strong> Das Blut wird in einer Zentrifuge getrennt, um das plättchenreiche Plasma mit seinen Wachstumsfaktoren zu gewinnen.</li>
<li><strong>Anwendung:</strong> Das Plasma wird mit feinen Nadeln direkt in die Haut eingebracht oder mit einem <a href="{{rel:leistungen/microneedling-mesotherapie/}}">Microneedling</a> kombiniert.</li>
</ol>
<h2>Vorteile und Wirkprinzip</h2>
<ul>
<li><strong>Natürlichkeit:</strong> Es werden keine synthetischen Stoffe verwendet – ausschließlich körpereigenes Material.</li>
<li><strong>Regeneration:</strong> Die Wachstumsfaktoren sollen ruhende Zellen, die Durchblutung sowie die Bildung von Kollagen und Elastin anregen.</li>
<li><strong>Vielseitig:</strong> Die Behandlung eignet sich für feine Fältchen im Gesicht, am Hals oder Dekolleté, für Augenringe und zur Stimulation der Haarwurzeln an der Kopfhaut.</li>
<li><strong>Gesellschaftsfähig:</strong> Nach der Behandlung ist die Haut meist nur für wenige Tage leicht gerötet.</li>
</ul>
<h2>Für wen ist PRP geeignet?</h2>
<p>PRP eignet sich für Menschen, die ihre Hautqualität auf möglichst natürliche Weise verbessern möchten. Da körpereigenes Material verwendet wird, sind allergische Reaktionen sehr unwahrscheinlich. Bei Blutgerinnungsstörungen, bestimmten Blut- oder Tumorerkrankungen, akuten Infektionen sowie in Schwangerschaft und Stillzeit wird nicht behandelt.</p>
<p class="info"><strong>Hinweis:</strong> Ergebnisse entwickeln sich schrittweise über mehrere Wochen und sind individuell verschieden. Meist sind mehrere Sitzungen sinnvoll.</p>
""",
        "prices": [],
        "faq": [
            ("Ist das Vampirlifting schmerzhaft?", "Die Blutentnahme entspricht einer normalen Blutabnahme. Für die Behandlung der Haut verwende ich auf Wunsch eine betäubende Creme."),
            ("Wie viele Behandlungen sind sinnvoll?", "Häufig empfehle ich 2–3 Sitzungen im Abstand von etwa vier Wochen, danach eine Auffrischung nach Bedarf."),
        ],
    },
    {
        "slug": "bio-botox",
        "group": "aesthetik",
        "icon": "lotus",
        "nav": "„Bio-Botox“",
        "name": "„Bio-Botox“ – sanfte Entspannung mimischer Fältchen",
        "card": "Behandlung mimischer Fältchen an Stirn, Zornesfalte und Augen – transparent erklärt.",
        "tags": ["Stirn", "Zornesfalte", "Krähenfüße"],
        "title": "„Bio-Botox“ in Westerburg – mimische Fältchen | Dr. Schick",
        "description": "„Bio-Botox“ in Westerburg: Was genau dahintersteckt, welche Zonen behandelt werden können und was Sie erwarten dürfen – ehrlich und transparent erklärt.",
        "h1": "„Bio-Botox“ – mimische Fältchen sanft behandeln",
        "lead": "Stirnfalten, Zornesfalte oder Krähenfüße entstehen durch Mimik. „Bio-Botox“-Behandlungen zielen darauf ab, diese Fältchen sanft zu glätten. Mir ist wichtig, Ihnen genau zu erklären, was dahintersteckt.",
        "facts": [("Behandlungsdauer", "ca. 20–30 Minuten"), ("Zonen", "Stirn, Zornesfalte, Augenpartie u. a."), ("Ausfallzeit", "in der Regel keine"), ("Kosten", "ab 150 € pro Zone")],
        "service_type": "Behandlung mimischer Falten",
        "body": """
<h2>Was bedeutet „Bio-Botox“?</h2>
<p>Der Begriff „Bio-Botox“ wird für Behandlungen verwendet, die einen Botox-ähnlichen, glättenden Effekt auf mimische Fältchen anstreben – <strong>jedoch ohne Botulinumtoxin</strong>. Weil der Begriff missverständlich sein kann, nenne ich Ihnen im Beratungsgespräch ganz genau, welches Präparat bzw. welcher Wirkstoff bei Ihnen zum Einsatz kommt, wie es wirkt und was Sie realistisch erwarten können.</p>
<h2>Welche Zonen können behandelt werden?</h2>
<ul>
<li><strong>Stirn:</strong> horizontale Stirnfalten</li>
<li><strong>Zornesfalte:</strong> senkrechte Falten zwischen den Augenbrauen</li>
<li><strong>Krähenfüße:</strong> Lachfältchen an den äußeren Augenwinkeln</li>
<li><strong>Hals & Kieferlinie:</strong> als sogenannter „Nofretete-Lift“</li>
<li><strong>Kaumuskel (Masseter):</strong> bei Wunsch nach einer schmaleren Gesichtsform</li>
</ul>
<h2>Abgrenzung zu anderen Behandlungen</h2>
<p>Mimische Fältchen entstehen durch Muskelbewegung, statische Falten und Volumenverlust dagegen durch die Alterung des Gewebes. Für statische Falten oder Volumen eignen sich eher <a href="{{rel:leistungen/hyaluron-faltenbehandlung/}}">Hyaluronsäure</a> oder <a href="{{rel:leistungen/skinbooster-biostimulatoren/}}">Skinbooster und Biostimulatoren</a>. Welche Methode für Sie passt, besprechen wir ehrlich im Erstgespräch.</p>
<h2>Ablauf</h2>
<ol>
<li>Ausführliche Beratung, Mimik-Analyse und Aufklärung.</li>
<li>Reinigung und Desinfektion der Haut.</li>
<li>Präzise Behandlung der ausgewählten Zonen mit sehr feinen Nadeln.</li>
<li>Hinweise zum Verhalten in den ersten Stunden nach der Behandlung.</li>
</ol>
<p class="info"><strong>Transparenz:</strong> Ein bestimmtes Ergebnis kann bei keiner ästhetischen Behandlung garantiert werden. Wirkung und Haltbarkeit sind individuell verschieden und hängen vom verwendeten Präparat ab.</p>
""",
        "prices": ["biobotox"],
        "faq": [
            ("Enthält „Bio-Botox“ Botulinumtoxin?", "Nein. Der Begriff beschreibt Behandlungen mit einem Botox-ähnlichen Ziel, aber ohne Botulinumtoxin. Welches Präparat genau verwendet wird, erkläre ich Ihnen vor der Behandlung."),
            ("Was zählt als eine Zone?", "Eine Zone ist z. B. die Stirn, die Zornesfalte oder die Augenpartie (Krähenfüße). Bei mehreren Zonen gelten die Paketpreise."),
        ],
    },
    {
        "slug": "lipolyse",
        "group": "aesthetik",
        "icon": "contour",
        "nav": "Lipolyse",
        "name": "Lipolyse – „Fett-weg-Spritze“",
        "card": "Gezielte Behandlung kleiner, hartnäckiger Fettpolster an Kinn, Gesicht oder Körper.",
        "tags": ["Doppelkinn", "Gesicht", "Bauch"],
        "title": "Lipolyse / Fett-weg-Spritze in Westerburg | Dr. Schick",
        "description": "Lipolyse („Fett-weg-Spritze“) in Westerburg: gezielte Behandlung kleiner Fettpolster an Kinn, Gesicht, Bauch und Körper – nach ausführlicher Beratung.",
        "h1": "Lipolyse („Fett-weg-Spritze“) in Westerburg",
        "lead": "Kleine Fettpolster, die sich trotz Sport und bewusster Ernährung hartnäckig halten – etwa am Kinn oder am Bauch – können mit einer Injektionslipolyse gezielt behandelt werden.",
        "facts": [("Behandlungsdauer", "ca. 20–40 Minuten"), ("Sitzungen", "meist mehrere"), ("Ausfallzeit", "einige Tage Schwellung möglich"), ("Kosten", "ab 300 €")],
        "service_type": "Injektionslipolyse",
        "body": """
<h2>Wie funktioniert die Injektionslipolyse?</h2>
<p>Bei der Lipolyse werden spezielle Wirkstoffkomplexe in das Unterhautfettgewebe eingebracht. Sie sollen helfen, Fettzellen in kleinen, umschriebenen Bereichen abzubauen; die Bestandteile werden anschließend über den Stoffwechsel abtransportiert.</p>
<h2>Welche Präparate verwende ich?</h2>
<ul>
<li><strong>PB Serum:</strong> für Kinn, Gesichtskontur, Bauch und weitere Körperzonen.</li>
<li><strong>Suisselle Cellbooster® Shape:</strong> für eine definiertere Gesichtskontur.</li>
</ul>
<h2>Für wen ist die Behandlung geeignet?</h2>
<p>Die Lipolyse ist keine Methode zur Gewichtsreduktion, sondern zur Formung kleiner, lokal begrenzter Fettdepots bei ansonsten stabilem Gewicht. Typische Bereiche sind das Doppelkinn, die Wangen- und Kieferpartie sowie kleine Polster an Bauch oder Hüfte.</p>
<h2>Ablauf und Nachsorge</h2>
<ol>
<li>Beratung, Untersuchung der Region und Aufklärung.</li>
<li>Markierung und Desinfektion, anschließend Injektion mit feinen Nadeln.</li>
<li>In den Tagen danach können Schwellung, Rötung, Wärmegefühl und Druckempfindlichkeit auftreten – das ist eine normale Reaktion.</li>
</ol>
<p class="info"><strong>Wichtig:</strong> Je nach Ausgangsbefund sind mehrere Sitzungen sinnvoll. Ergebnisse sind individuell und können nicht garantiert werden.</p>
""",
        "prices": ["lipolyse"],
        "faq": [
            ("Wie schnell sieht man ein Ergebnis?", "Der Abbau erfolgt schrittweise über mehrere Wochen. Eine Beurteilung ist meist nach 6–8 Wochen sinnvoll."),
        ],
    },
    {
        "slug": "infusionstherapie",
        "group": "naturheilkunde",
        "icon": "infusion",
        "nav": "Infusionen & Vitaminkuren",
        "name": "Infusionstherapie & Vitamin-Aufbaukuren",
        "card": "Individuell zusammengestellte Infusionen mit Vitaminen und Mikronährstoffen – z. B. zur Unterstützung in fordernden Phasen.",
        "tags": ["Vitamine", "Immun-Boost", "Energy"],
        "title": "Infusionstherapie & Vitamin-Infusion Westerburg | Dr. Schick",
        "description": "Vitamin-Infusion, Immun-Boost, Energy-Cocktail und Detox & Anti-Aging in Westerburg (Westerwald) – individuell abgestimmt nach Anamnese und Laborwerten.",
        "h1": "Infusionstherapie & Vitamin-Aufbaukuren in Westerburg",
        "lead": "Infusionen ermöglichen es, Vitamine und Mikronährstoffe direkt über die Vene zuzuführen. Ich stelle sie individuell zusammen – abgestimmt auf Ihre Anamnese und, wenn sinnvoll, auf Ihre Laborwerte.",
        "facts": [("Dauer", "ca. 30–60 Minuten"), ("Kur", "z. B. 4–6 Infusionen"), ("Vorab", "Anamnese, ggf. Laborwerte"), ("Kosten", "ab 120 €")],
        "service_type": "Infusionstherapie",
        "body": """
<h2>Wann kann eine Infusion sinnvoll sein?</h2>
<p>Viele Menschen interessieren sich für Infusionen in Phasen hoher Belastung, nach Infekten, bei einseitiger Ernährung oder wenn ein nachgewiesener Mangel an bestimmten Mikronährstoffen besteht. Vor jeder Infusion steht ein ausführliches Gespräch – und wo sinnvoll eine <a href="{{rel:leistungen/labordiagnostik/}}">Blutuntersuchung</a>, damit wir gezielt statt „nach Gefühl“ vorgehen.</p>
<h2>Meine Infusionen</h2>
<h3>Vitamin-Infusion</h3>
<p>Eine Basis-Infusion mit wichtigen Vitaminen, zum Beispiel aus dem B-Komplex und Vitamin C.</p>
<h3>Immun-Boost</h3>
<p>Kombination aus u. a. hochdosiertem Vitamin C und Zink – häufig gewünscht in der Erkältungszeit oder nach Infekten.</p>
<h3>Energy-Cocktail</h3>
<p>Eine Mischung aus B-Vitaminen, Magnesium und Aminosäuren für Phasen, in denen Sie sich erschöpft fühlen.</p>
<h3>Detox & Anti-Aging</h3>
<p>Mit antioxidativen Bestandteilen wie Glutathion und Vitamin C – eine beliebte Ergänzung zu ästhetischen Behandlungen.</p>
<h2>Vitamin-Aufbaukuren</h2>
<p>Bei einer Aufbaukur erhalten Sie mehrere Infusionen in festgelegten Abständen. Häufigkeit und Zusammensetzung stimmen wir individuell ab und überprüfen sie im Verlauf.</p>
<h2>Ablauf</h2>
<ol>
<li>Anamnese und Klärung möglicher Gegenanzeigen (z. B. Herz- oder Nierenerkrankungen).</li>
<li>Individuelle Zusammenstellung; die Infusionslösung wird in der Apotheke hergestellt.</li>
<li>Entspannte Infusion in ruhiger Atmosphäre, ca. 30–60 Minuten.</li>
</ol>
<p class="info"><strong>Hinweis:</strong> Infusionen ersetzen keine ausgewogene Ernährung und keine ärztliche Abklärung von Beschwerden. Die Wirksamkeit von Infusionen ist nicht für alle Anwendungsbereiche wissenschaftlich belegt.</p>
""",
        "prices": ["infusionen"],
        "faq": [
            ("Warum kommt noch eine Apothekenrechnung hinzu?", "Die Infusionslösung wird individuell für Sie in der Apotheke hergestellt und von der Apotheke direkt abgerechnet. Meine Preise umfassen Beratung, Anlage und Betreuung der Infusion."),
            ("Brauche ich vorher Laborwerte?", "Nicht immer. Bei bestimmten Fragestellungen oder Kuren ist eine Blutuntersuchung aber sinnvoll, um gezielt zu ergänzen. Die Blutentnahme kann direkt in meiner Praxis erfolgen."),
        ],
    },
    {
        "slug": "naturheilverfahren-akupunktur",
        "group": "naturheilkunde",
        "icon": "leaf",
        "nav": "Naturheilverfahren & Akupunktur",
        "name": "Naturheilverfahren, Akupunktur & Eigenbluttherapie",
        "card": "Ganzheitliche Begleitung mit Akupunktur, Eigenbluttherapie und bewährten naturheilkundlichen Verfahren.",
        "tags": ["Akupunktur", "Eigenblut", "Ganzheitlich"],
        "title": "Naturheilkunde & Akupunktur in Westerburg | Dr. Schick",
        "description": "Heilpraktikerin in Westerburg: Naturheilverfahren, Akupunktur und Eigenbluttherapie – ganzheitliche Begleitung mit 25 Jahren medizinischer Erfahrung.",
        "h1": "Naturheilverfahren, Akupunktur & Eigenbluttherapie",
        "lead": "Als Heilpraktikerin verbinde ich naturheilkundliche Verfahren mit meiner langjährigen medizinischen Erfahrung – ergänzend, ganzheitlich und immer mit Blick auf den ganzen Menschen.",
        "facts": [("Erstgespräch", "ca. 30 Minuten"), ("Folgetermine", "ca. 30–60 Minuten"), ("Überweisung", "nicht erforderlich"), ("Kosten", "nach Aufwand")],
        "service_type": "Naturheilkunde",
        "body": """
<h2>Mein Verständnis von Naturheilkunde</h2>
<p>Naturheilkundliche Verfahren können eine schulmedizinische Behandlung sinnvoll ergänzen. Mir ist wichtig, ehrlich zu beraten: Was kann ein Verfahren leisten, wo liegen seine Grenzen – und wann gehört eine Beschwerde in fachärztliche Hände? Am Anfang steht deshalb immer eine ausführliche Anamnese.</p>
<h2>Akupunktur</h2>
<p>Die Akupunktur stammt aus der traditionellen chinesischen Medizin. Dabei werden sehr feine, sterile Einmalnadeln an ausgewählten Punkten gesetzt. Akupunktur wird häufig begleitend eingesetzt, zum Beispiel bei:</p>
<ul>
<li>Verspannungen und Beschwerden im Kiefer-, Nacken- und Schulterbereich</li>
<li>Stress, innerer Unruhe und Schlafproblemen</li>
<li>Kopfschmerzen und Spannungszuständen</li>
<li>zur allgemeinen Entspannung und Regulation</li>
</ul>
<p>Als Zahnärztin kenne ich die enge Verbindung zwischen Kiefergelenk, Kaumuskulatur und Verspannungen besonders gut.</p>
<h2>Eigenbluttherapie</h2>
<p>Bei der klassischen Eigenbluttherapie wird eine kleine Menge Blut aus der Vene entnommen und – unverändert oder mit naturheilkundlichen Zusätzen – in den Muskel zurückgegeben. Das Verfahren wird traditionell zur Anregung der körpereigenen Regulationskräfte eingesetzt, zum Beispiel begleitend bei Infektanfälligkeit oder in Erholungsphasen.</p>
<h2>Weitere naturheilkundliche Verfahren</h2>
<p>Je nach Anliegen können weitere Verfahren wie Vitalstoff- und Ernährungsberatung oder <a href="{{rel:leistungen/infusionstherapie/}}">Infusionstherapien</a> sinnvoll sein. Welche Kombination passt, entscheiden wir gemeinsam.</p>
<p class="info"><strong>Pflichthinweis:</strong> Die hier genannten naturheilkundlichen Verfahren gehören überwiegend nicht zu den wissenschaftlich allgemein anerkannten Methoden im Sinne der Schulmedizin. Ihre Wirksamkeit ist nicht für alle Anwendungsbereiche wissenschaftlich belegt. Sie ersetzen keine ärztliche Diagnose oder Behandlung.</p>
""",
        "prices": [],
        "faq": [
            ("Tut Akupunktur weh?", "Die Nadeln sind sehr fein. Die meisten Menschen spüren nur einen kurzen, leichten Stich und empfinden die Behandlung als entspannend."),
            ("Übernimmt die Krankenkasse die Kosten?", "Gesetzliche Krankenkassen erstatten Heilpraktikerleistungen in der Regel nicht. Private Krankenversicherungen und Zusatzversicherungen übernehmen je nach Tarif teilweise die Kosten."),
        ],
    },
    {
        "slug": "labordiagnostik",
        "group": "naturheilkunde",
        "icon": "lab",
        "nav": "Labordiagnostik & Blutentnahme",
        "name": "Labordiagnostik & Blutentnahme",
        "card": "Blutentnahme direkt in der Praxis – als fundierte Grundlage für Infusionen, Vitalstoffe und Beratung.",
        "tags": ["Blutbild", "Vitamine", "Mineralstoffe"],
        "title": "Labordiagnostik & Blutentnahme in Westerburg | Dr. Schick",
        "description": "Blutentnahme in Westerburg: Vitamin- und Mineralstoffstatus, Blutbild und weitere Laborwerte als fundierte Grundlage für Ihre Behandlung.",
        "h1": "Labordiagnostik & Blutentnahme in Westerburg",
        "lead": "Gute Entscheidungen brauchen eine gute Grundlage. Mit einer Blutuntersuchung können wir Ihren Vitalstoffstatus und weitere Werte gezielt überprüfen – die Blutentnahme erfolgt direkt in meiner Praxis.",
        "facts": [("Blutentnahme", "wenige Minuten"), ("Ergebnisse", "meist nach wenigen Tagen"), ("Besprechung", "persönlich in der Praxis"), ("Kosten", "je nach Laborprofil")],
        "service_type": "Labordiagnostik",
        "body": """
<h2>Welche Laboruntersuchungen biete ich an?</h2>
<p>Welche Werte sinnvoll sind, richtet sich nach Ihrem Anliegen. Häufig untersuchte Parameter sind zum Beispiel:</p>
<ul>
<li><strong>Blutbild</strong> (kleines oder großes Blutbild)</li>
<li><strong>Vitamine</strong> wie Vitamin D, Vitamin B12 und Folsäure</li>
<li><strong>Mineralstoffe und Spurenelemente</strong> wie Eisen/Ferritin, Zink, Magnesium und Selen</li>
<li><strong>Schilddrüsenwerte</strong> (z. B. TSH)</li>
<li>weitere Werte nach individueller Fragestellung</li>
</ul>
<h2>Wie läuft die Blutentnahme ab?</h2>
<ol>
<li><strong>Gespräch:</strong> Wir besprechen Ihr Anliegen und legen fest, welche Werte sinnvoll sind. Sie erhalten vorab eine transparente Kosteninformation.</li>
<li><strong>Blutentnahme:</strong> Die Blutentnahme erfolgt in meiner Praxis – schnell und mit routinierter Hand. Für manche Werte sollten Sie nüchtern kommen; das sage ich Ihnen vorher.</li>
<li><strong>Labor:</strong> Die Proben werden von einem externen, spezialisierten Fachlabor ausgewertet.</li>
<li><strong>Befundbesprechung:</strong> Wir besprechen die Ergebnisse persönlich und leiten gemeinsam die nächsten Schritte ab – z. B. eine gezielte <a href="{{rel:leistungen/infusionstherapie/}}">Infusionstherapie</a>.</li>
</ol>
<h2>Was kostet eine Laboruntersuchung?</h2>
<p>Die Kosten hängen von den gewählten Parametern ab. Die Laborkosten werden nach der Gebührenordnung des Labors berechnet. Vor der Blutentnahme erhalten Sie von mir eine Übersicht über die voraussichtlichen Kosten.</p>
<p class="info"><strong>Hinweis:</strong> Bei akuten oder unklaren Beschwerden gehört eine Abklärung in ärztliche bzw. fachärztliche Hände. Die Labordiagnostik in meiner Praxis dient vor allem der Planung meiner Behandlungen.</p>
""",
        "prices": [],
        "faq": [
            ("Muss ich nüchtern sein?", "Das hängt von den Werten ab. Ich teile Ihnen bei der Terminvereinbarung mit, ob Sie nüchtern kommen sollten."),
            ("Kann ich vorhandene Laborwerte mitbringen?", "Sehr gern – aktuelle Befunde helfen mir bei der Einschätzung und vermeiden doppelte Untersuchungen."),
        ],
    },
]

# Weitere Leistungen ohne eigene Seite (noch keine Detailinfos)
EXTRA_SERVICES = [
    ("Laserbehandlung", "Informationen zu Laserbehandlungen erhalten Sie gern persönlich im Beratungsgespräch."),
]

# ---------------------------------------------------------------------------
# FAQ
# ---------------------------------------------------------------------------
FAQ = [
    ("Wie läuft ein erster Termin ab?", "Beim Ersttermin nehme ich mir Zeit für Ihre Anamnese, Ihre Beschwerden und Ihre Wünsche. Wir besprechen Ziele, mögliche Ursachen und bisherige Befunde und erstellen gemeinsam einen individuellen Behandlungsplan."),
    ("Wie lange dauert ein Termin?", "Ein Ersttermin dauert ca. 30 Minuten, Folgetermine ca. 30–60 Minuten – je nach Behandlung."),
    ("Welche Unterlagen soll ich mitbringen?", "Bitte bringen Sie – falls vorhanden – aktuelle Arztberichte, Laborwerte, eine Medikamentenliste, relevante Befunde (z. B. Blutbild, Schilddrüse, Stuhl- und Darmbefunde) sowie Ihren Impf- und Allergiepass mit. Bei ästhetischen Behandlungen bringen Sie bitte, falls vorhanden, Ihren Injektionspass mit."),
    ("Wie vereinbare ich einen Termin?", "Am einfachsten über den Button „Termin buchen“. Alternativ erreichen Sie mich per E-Mail{phone_text}."),
    ("Wie kann ich bezahlen?", "Sie können bar, mit EC-Karte oder per PayPal bezahlen."),
    ("Werden die Kosten von der Krankenkasse erstattet?", "Das ist individuell. Private Krankenversicherungen, Beihilfe oder Zusatzversicherungen erstatten Heilpraktikerleistungen teilweise – abhängig vom Tarif. Gesetzliche Krankenkassen erstatten in der Regel nicht; einzelne Leistungen können je nach Kasse oder Bonusprogramm möglich sein. Bitte klären Sie das direkt mit Ihrer Versicherung. Rein ästhetische Behandlungen sind grundsätzlich Selbstzahlerleistungen."),
    ("Brauche ich eine Überweisung?", "Nein, Sie können auch ohne Überweisung einen Termin vereinbaren."),
    ("Was passiert, wenn ich einen Termin absagen muss?", "Bitte sagen Sie Termine spätestens 24 Stunden vorher ab, da ansonsten ein Ausfallhonorar anfällt."),
    ("Wer sollte nicht ästhetisch behandelt werden?", "In Schwangerschaft und Stillzeit, bei akuten Infektionen oder Entzündungen im Behandlungsbereich, bei bestimmten Autoimmun- und Gerinnungserkrankungen sowie bei bekannten Allergien gegen Bestandteile der Präparate wird nicht oder nur nach sorgfältiger Abwägung behandelt. Das klären wir gemeinsam anhand des Anamnesebogens."),
    ("Mit welchen Nebenwirkungen muss ich rechnen?", "Nach Injektionsbehandlungen sind leichte Rötungen, Schwellungen, Druckempfindlichkeit oder kleine Blutergüsse möglich, die meist nach wenigen Tagen abklingen. Über seltene Risiken kläre ich Sie vor jeder Behandlung ausführlich und individuell auf."),
    ("Wie bereite ich mich auf eine ästhetische Behandlung vor?", "Verzichten Sie – sofern medizinisch vertretbar und mit Ihrem Arzt abgesprochen – einige Tage vorher möglichst auf blutverdünnende Schmerzmittel und Alkohol, um das Risiko von Blutergüssen zu verringern. Kommen Sie am besten ungeschminkt. Alles Weitere bespreche ich individuell mit Ihnen."),
]
