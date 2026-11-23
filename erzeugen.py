#!/usr/bin/env python3
"""Feiertags- und Ferienkalender aus daten/ prüfen und als .ics und JSON erzeugen.

  python3 erzeugen.py pruefen               Daten prüfen (Rückgabe 1 bei Fehlern)
  python3 erzeugen.py erzeugen [ORDNER]     alle Kalender nach ORDNER schreiben (Standard: ausgabe/)
  python3 erzeugen.py liste KALENDER        Termine eines Kalenders ausgeben, z. B. bayern/alle
  python3 erzeugen.py vergleich ALT NEU     Unterschied der Termine zweier Ausgabe-Ordner (Markdown)

Nur Python-Standardbibliothek. Feiertage werden berechnet (Ostern nach Gauß/Meeus), Ferien kommen aus
daten/<land>.json (von/bis einschließlich, wie amtlich veröffentlicht).

Zeitraum: ab 1. Januar des späteren der beiden Jahre (laufendes Jahr − 3) und (Jahr des ersten Ferien-Eintrags des
Landes); Feiertage und schulfreie Tage bis zum letzten Jahr der Ferien-Daten, mindestens laufendes Jahr + 2.

Umgebung: HEUTE (JJJJ-MM-TT) ersetzt das heutige Datum (für Tests), DATEN einen anderen Daten-Ordner.
"""
import datetime as dt
import html
import json
import os
import re
import shutil
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
SEITE = "https://chodid.github.io/feiertage-kalender/"
QUELLTEXT = "https://github.com/chodid/feiertage-kalender"
PRODID = "-//feiertage-kalender//DE"
UID_ENDUNG = "@feiertage-kalender"
FORMAT = 1
JAHRE_ZURUECK = 3
JAHRE_VORAUS = 2
EIN_TAG = dt.timedelta(days=1)


def ostern(j):
    """Ostersonntag (gregorianisch, Gauß/Meeus)."""
    a, b, c = j % 19, j // 100, j % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7  # noqa: E741
    m = (a + 11 * h + 22 * l) // 451
    monat = (h + l - 7 * m + 114) // 31
    tag = (h + l - 7 * m + 114) % 31 + 1
    return dt.date(j, monat, tag)


def buss_und_bettag(j):
    """Mittwoch vor dem 23. November."""
    t = dt.date(j, 11, 22)
    return t - dt.timedelta(days=(t.weekday() - 2) % 7)


def _o(n):
    return lambda j: ostern(j) + dt.timedelta(days=n)


def _f(m, t):
    return lambda j: dt.date(j, m, t)


# Kennung → (Name, Datum(Jahr), Text für die Beschreibung im Kalender)
GESETZLICH = "Gesetzlicher Feiertag in {land}."
TAGE = {
    "neujahr": ("Neujahr", _f(1, 1), GESETZLICH),
    "heilige-drei-koenige": ("Heilige Drei Könige", _f(1, 6), GESETZLICH),
    "karfreitag": ("Karfreitag", _o(-2), GESETZLICH),
    "ostersonntag": ("Ostersonntag", _o(0), GESETZLICH),
    "ostermontag": ("Ostermontag", _o(1), GESETZLICH),
    "tag-der-arbeit": ("Tag der Arbeit", _f(5, 1), GESETZLICH),
    "christi-himmelfahrt": ("Christi Himmelfahrt", _o(39), GESETZLICH),
    "pfingstsonntag": ("Pfingstsonntag", _o(49), GESETZLICH),
    "pfingstmontag": ("Pfingstmontag", _o(50), GESETZLICH),
    "fronleichnam": ("Fronleichnam", _o(60), GESETZLICH),
    "mariae-himmelfahrt": ("Mariä Himmelfahrt", _f(8, 15),
                           "Gesetzlicher Feiertag in {land} nur in Gemeinden mit überwiegend katholischer Bevölkerung."),
    "tag-der-deutschen-einheit": ("Tag der Deutschen Einheit", _f(10, 3), GESETZLICH),
    "reformationstag": ("Reformationstag", _f(10, 31), GESETZLICH),
    "allerheiligen": ("Allerheiligen", _f(11, 1), GESETZLICH),
    "buss-und-bettag": ("Buß- und Bettag (schulfrei)", buss_und_bettag,
                        "Unterrichtsfrei in {land}, kein gesetzlicher Feiertag."),
    "weihnachtstag-1": ("1. Weihnachtstag", _f(12, 25), GESETZLICH),
    "weihnachtstag-2": ("2. Weihnachtstag", _f(12, 26), GESETZLICH),
}

# Feste Prüfliste, unabhängig von der Berechnung oben (Ostersonntag, Buß- und Bettag)
PRUEFLISTE_OSTERN = ["2023-04-09", "2024-03-31", "2025-04-20", "2026-04-05", "2027-03-28", "2028-04-16", "2029-04-01",
                     "2030-04-21", "2031-04-13", "2032-03-28"]
PRUEFLISTE_BUSSTAG = ["2023-11-22", "2024-11-20", "2025-11-19", "2026-11-18", "2027-11-17", "2028-11-22", "2029-11-21",
                      "2030-11-20", "2031-11-19", "2032-11-17"]

DATUM = re.compile(r"\d{4}-\d{2}-\d{2}")
KENNUNG = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
FERIEN_NAME = re.compile(r"[A-Za-zÄÖÜäöüß0-9 .()\-]{1,60}")


def heute():
    return dt.date.fromisoformat(os.environ["HEUTE"]) if os.environ.get("HEUTE") else dt.date.today()


def daten_ordner():
    return os.environ.get("DATEN") or os.path.join(REPO, "daten")


def laender_lesen(ordner=None):
    """([Land, …] sortiert nach Ordner, [Fehler, …]) – Dateien, die sich nicht lesen lassen, werden als Fehler gemeldet."""
    ordner = ordner or daten_ordner()
    laender, fehler = [], []
    for datei in sorted(os.listdir(ordner)):
        if not datei.endswith(".json"):
            continue
        try:
            with open(os.path.join(ordner, datei), encoding="utf-8") as f:
                land = json.load(f)
        except (OSError, ValueError) as e:
            fehler.append(f"{datei}: nicht lesbar ({e})")
            continue
        if not isinstance(land, dict):
            fehler.append(f"{datei}: oberste Ebene muss ein Objekt sein")
            continue
        land["_datei"] = datei
        laender.append(land)
    if not laender and not fehler:
        fehler.append(f"{ordner}: keine Daten gefunden")
    return laender, fehler


def _datum(wert):
    if isinstance(wert, str) and DATUM.fullmatch(wert):
        try:
            return dt.date.fromisoformat(wert)
        except ValueError:
            return None
    return None


def pruefe_land(land, basis=None):
    """Fehler in den Daten eines Landes als Liste von Texten (leer = in Ordnung)."""
    basis = basis or REPO
    d = land.get("_datei", "?")
    f = []
    for feld in ("kuerzel", "ordner", "name"):
        if not isinstance(land.get(feld), str) or not land.get(feld):
            f.append(f"{d}: Feld „{feld}“ fehlt oder ist kein Text")
    if isinstance(land.get("kuerzel"), str) and not re.fullmatch(r"[a-z]{2}", land["kuerzel"]):
        f.append(f"{d}: kuerzel „{land['kuerzel']}“ muss aus zwei Kleinbuchstaben bestehen")
    if isinstance(land.get("ordner"), str) and not KENNUNG.fullmatch(land["ordner"]):
        f.append(f"{d}: ordner „{land['ordner']}“ nur Kleinbuchstaben, Ziffern und Bindestrich")
    gesehen = set()
    for feld in ("feiertage", "feiertage_wahlweise", "schulfrei"):
        liste = land.get(feld)
        if not isinstance(liste, list):
            f.append(f"{d}: Feld „{feld}“ fehlt oder ist keine Liste")
            continue
        for k in liste:
            if k not in TAGE:
                f.append(f"{d}: {feld} – Kennung „{k}“ unbekannt (erzeugen.py, TAGE)")
            elif k in gesehen:
                f.append(f"{d}: Kennung „{k}“ steht mehrfach in feiertage, feiertage_wahlweise oder schulfrei")
            gesehen.add(k)
    if isinstance(land.get("feiertage_wahlweise"), list) and len(land["feiertage_wahlweise"]) > 1:
        f.append(f"{d}: höchstens ein Feiertag in feiertage_wahlweise")
    quelle = land.get("quelle")
    if not isinstance(quelle, dict):
        f.append(f"{d}: Feld „quelle“ fehlt")
    else:
        for feld in ("titel", "fundstelle", "beleg", "uebernommen"):
            if not isinstance(quelle.get(feld), str) or not quelle.get(feld):
                f.append(f"{d}: quelle.{feld} fehlt")
        if "adresse" in quelle and not str(quelle["adresse"]).startswith("https://"):
            f.append(f"{d}: quelle.adresse muss mit https:// beginnen")
        if isinstance(quelle.get("uebernommen"), str) and _datum(quelle["uebernommen"]) is None:
            f.append(f"{d}: quelle.uebernommen ist kein Datum (JJJJ-MM-TT)")
        beleg = quelle.get("beleg")
        if isinstance(beleg, str) and beleg:
            if not re.fullmatch(r"belege/[A-Za-z0-9._-]+", beleg):
                f.append(f"{d}: quelle.beleg „{beleg}“ muss eine Datei in belege/ sein")
            elif not os.path.isfile(os.path.join(basis, beleg)):
                f.append(f"{d}: Beleg-Datei {beleg} fehlt")
    ferien = land.get("ferien")
    if not isinstance(ferien, list) or not ferien:
        f.append(f"{d}: Feld „ferien“ fehlt oder ist leer")
        return f
    gueltig = []
    for i, e in enumerate(ferien, 1):
        wo = f"{d}: ferien Nr. {i}"
        if not isinstance(e, dict) or set(e) != {"name", "von", "bis"}:
            f.append(f"{wo}: erwartet genau name, von, bis")
            continue
        wo += f" ({e['name']} {e['von']})"
        if not isinstance(e["name"], str) or not FERIEN_NAME.fullmatch(e["name"]):
            f.append(f"{wo}: Name höchstens 60 Zeichen aus Buchstaben, Ziffern, Leerzeichen und - . ( )")
        von, bis = _datum(e["von"]), _datum(e["bis"])
        if von is None or bis is None:
            f.append(f"{wo}: von und bis müssen Datumsangaben sein (JJJJ-MM-TT)")
            continue
        if bis < von:
            f.append(f"{wo}: bis liegt vor von")
            continue
        if (bis - von).days + 1 > 70:
            f.append(f"{wo}: länger als 70 Tage")
        gueltig.append((von, bis, e["name"]))
    gueltig.sort()
    for (v1, b1, n1), (v2, b2, n2) in zip(gueltig, gueltig[1:]):
        if v1 == v2:
            f.append(f"{d}: zwei Ferien beginnen am {v1} ({n1}, {n2})")
        elif v2 <= b1:
            f.append(f"{d}: Ferien überschneiden sich: {n1} {v1}–{b1} und {n2} {v2}–{b2}")
    return f


def pruefe_berechnung():
    """Berechnete Tage gegen die feste Prüfliste."""
    f = []
    for soll in PRUEFLISTE_OSTERN:
        j = int(soll[:4])
        if ostern(j).isoformat() != soll:
            f.append(f"Ostersonntag {j}: berechnet {ostern(j)}, Prüfliste {soll}")
    for soll in PRUEFLISTE_BUSSTAG:
        j = int(soll[:4])
        if buss_und_bettag(j).isoformat() != soll:
            f.append(f"Buß- und Bettag {j}: berechnet {buss_und_bettag(j)}, Prüfliste {soll}")
    return f


def pruefe_alles(ordner=None, basis=None):
    laender, fehler = laender_lesen(ordner)
    fehler += pruefe_berechnung()
    for land in laender:
        fehler += pruefe_land(land, basis)
    for feld in ("kuerzel", "ordner"):
        werte = [l.get(feld) for l in laender if isinstance(l.get(feld), str)]  # noqa: E741
        for w in sorted(set(werte)):
            if werte.count(w) > 1:
                fehler.append(f"{feld} „{w}“ kommt in mehreren Dateien vor")
    if not fehler:
        for land in laender:
            for kal in kalender_des_landes(land):
                uids = [t["uid"] for t in kal["termine"]]
                doppelt = sorted({u for u in uids if uids.count(u) > 1})
                if doppelt:
                    fehler.append(f"{kal['kennung']}: Kennung mehrfach vergeben: {', '.join(doppelt)}")
    return laender, fehler


def fenster(land, tag=None):
    """(erster Tag, letztes Jahr der Feiertage, letzter Ferientag) eines Landes."""
    tag = tag or heute()
    erstes = min(dt.date.fromisoformat(e["von"]) for e in land["ferien"]).year
    ferien_bis = max(dt.date.fromisoformat(e["bis"]) for e in land["ferien"])
    von = dt.date(max(tag.year - JAHRE_ZURUECK, erstes), 1, 1)
    return von, max(ferien_bis.year, tag.year + JAHRE_VORAUS), ferien_bis


def _termin(uid, name, art, von, bis, text):
    return {"uid": uid + UID_ENDUNG, "name": name, "art": art, "von": von.isoformat(), "bis": bis.isoformat(),
            "bis_exklusiv": (bis + EIN_TAG).isoformat(), "_text": text}


def termine_des_landes(land, tag=None):
    """(Feiertage ohne wahlweise, wahlweise Feiertage, Ferien samt schulfreien Tagen) – je Liste von Terminen."""
    von, bis_jahr, _ = fenster(land, tag)
    k, name = land["kuerzel"], land["name"]

    def berechnet(kennungen, art):
        aus = []
        for jahr in range(von.year, bis_jahr + 1):
            for kennung in kennungen:
                titel, datum, text = TAGE[kennung]
                d = datum(jahr)
                uid = f"ff-feiertag-{k}-{jahr}-{kennung}" if art == "feiertag" else f"ff-ferien-{k}-{d.isoformat()}"
                aus.append(_termin(uid, titel, art, d, d, text.format(land=name)))
        return aus

    ferien = berechnet(land["schulfrei"], "ferien")
    quelle = f"Schulferien {name}. Quelle: {land['quelle']['fundstelle']}."
    for e in land["ferien"]:
        v, b = dt.date.fromisoformat(e["von"]), dt.date.fromisoformat(e["bis"])
        if b >= von:
            ferien.append(_termin(f"ff-ferien-{k}-{v.isoformat()}", e["name"], "ferien", v, b, quelle))
    return berechnet(land["feiertage"], "feiertag"), berechnet(land["feiertage_wahlweise"], "feiertag"), ferien


def kalender_des_landes(land, tag=None, erzeugt=None):
    """Alle Kalender eines Landes als Liste von Objekten (JSON-Aufbau, dazu _text je Termin für die .ics)."""
    fest, wahl, ferien = termine_des_landes(land, tag)
    von, _, ferien_bis = fenster(land, tag)
    erzeugt = erzeugt or dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    name, ordner = land["name"], land["ordner"]
    arten = [("feiertage", f"Feiertage {name}", fest + wahl), ("ferien", f"Schulferien {name}", ferien),
             ("alle", f"Feiertage & Ferien {name}", fest + wahl + ferien)]
    if wahl:
        kennung = land["feiertage_wahlweise"][0]
        zusatz = f" (ohne {TAGE[kennung][0]})"
        arten[1:1] = [(f"feiertage-ohne-{kennung}", f"Feiertage {name}{zusatz}", fest)]
        arten.append((f"alle-ohne-{kennung}", f"Feiertage & Ferien {name}{zusatz}", fest + ferien))
    quelle = {x: land["quelle"][x] for x in ("titel", "fundstelle", "adresse") if x in land["quelle"]}
    return [{
        "format": FORMAT,
        "kalender": {"kennung": f"{ordner}/{datei}", "name": titel},
        "land": {"kuerzel": land["kuerzel"], "name": name},
        "erzeugt": erzeugt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fenster_von": von.isoformat(),
        "ferien_bis": ferien_bis.isoformat(),
        "quelle": quelle,
        "lizenz": "CC0-1.0",
        "termine": sorted(termine, key=lambda t: (t["von"], t["uid"])),
    } for datei, titel, termine in arten]


# --- Ausgabe --------------------------------------------------------------------------------------------------

def ics_text(t):
    return t.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def falten(zeile):
    """Zeile nach RFC 5545 auf höchstens 75 Oktette falten, ohne ein UTF-8-Zeichen zu zerteilen."""
    teile, aktuell, laenge = [], "", 0
    for zeichen in zeile:
        n = len(zeichen.encode("utf-8"))
        if laenge + n > 75:
            teile.append(aktuell)
            aktuell, laenge = " ", 1
        aktuell += zeichen
        laenge += n
    teile.append(aktuell)
    return "\r\n".join(teile)


def ics(kal):
    stempel = kal["erzeugt"].replace("-", "").replace(":", "")
    z = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:{PRODID}", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
         f"X-WR-CALNAME:{ics_text(kal['kalender']['name'])}", "X-WR-TIMEZONE:Europe/Berlin",
         "REFRESH-INTERVAL;VALUE=DURATION:P1D", "X-PUBLISHED-TTL:P1D"]
    for t in kal["termine"]:
        text = f"{t['_text']} Kalender: {QUELLTEXT} – ohne Gewähr."
        z += ["BEGIN:VEVENT", f"UID:{t['uid']}", f"DTSTAMP:{stempel}",
              f"DTSTART;VALUE=DATE:{t['von'].replace('-', '')}", f"DTEND;VALUE=DATE:{t['bis_exklusiv'].replace('-', '')}",
              f"SUMMARY:{ics_text(t['name'])}", f"DESCRIPTION:{ics_text(text)}",
              "CATEGORIES:" + ("Feiertag" if t["art"] == "feiertag" else "Schulferien"),
              "TRANSP:TRANSPARENT", "X-MICROSOFT-CDO-BUSYSTATUS:FREE", "END:VEVENT"]
    z.append("END:VCALENDAR")
    return "\r\n".join(falten(x) for x in z) + "\r\n"


def als_json(kal):
    sauber = dict(kal, termine=[{k: v for k, v in t.items() if not k.startswith("_")} for t in kal["termine"]])
    return json.dumps(sauber, ensure_ascii=False, indent=1) + "\n"


MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November",
          "Dezember"]
APPS = [("Apple Kalender", "iPhone, iPad, Mac: auf „Abonnieren“ tippen. Oder im Kalender „Kalenderabo hinzufügen“ wählen "
         "und die Adresse einfügen."),
        ("Google Kalender", "Im Browser links bei „Weitere Kalender“ auf „+“, dann „Per URL“ und die kopierte Adresse "
         "einfügen."),
        ("Outlook", "„Kalender hinzufügen“, dann „Aus dem Internet abonnieren“ und die kopierte Adresse einfügen."),
        ("Thunderbird", "„Neuer Kalender“, dann „Im Netzwerk“ und die kopierte Adresse einfügen.")]


def datum_lang(text):
    d = dt.date.fromisoformat(text[:10])
    return f"{d.day}. {MONATE[d.month - 1]} {d.year}"


def untertitel(land, kennung):
    """Ein Satz zum Inhalt eines Kalenders für die Eingangsseite."""
    datei = kennung.split("/", 1)[1]
    wahl = [TAGE[k][0] for k in land["feiertage_wahlweise"]]
    frei = [TAGE[k][0].replace(" (schulfrei)", "") for k in land["schulfrei"]]
    feiertage = "Gesetzliche Feiertage"
    if wahl:
        feiertage += f" {'ohne' if '-ohne-' in datei else 'mit'} {wahl[0]}"
    ferien = "Schulferien" + (f" und {frei[0]}" if frei else "")
    if datei.startswith("feiertage"):
        return feiertage
    return ferien if datei == "ferien" else f"{feiertage}, dazu {ferien}"


def startseite(alle):
    """Eingangsseite mit den Abo-Adressen; Stil, Schriften und Bildmarke liegen in seite/."""
    esc = html.escape
    teile = []
    for land, kalender in alle:
        zeilen = []
        for kal in kalender:
            k = kal["kalender"]["kennung"]
            name = kal["kalender"]["name"]
            webcal = SEITE.replace("https://", "webcal://") + k + ".ics"
            zeilen.append(
                f'<li>\n<div><h3>{esc(name)}</h3>\n<p>{esc(untertitel(land, k))} · '
                f'<span class="zahl mono">{len(kal["termine"])} Termine</span></p></div>\n'
                f'<div class="knoepfe"><a class="knopf" href="{webcal}">Abonnieren</a>'
                f'<button class="knopf zweit" type="button" data-adresse="{k}.ics">Adresse kopieren</button></div>\n'
                f'<div class="dateien"><a class="mono" href="{k}.ics">{k}.ics</a>'
                f'<a class="mono" href="{k}.json">{k}.json</a></div>\n</li>')
        quelle = land["quelle"]
        beleg = f'{QUELLTEXT}/blob/main/{quelle["beleg"]}'
        teile.append(
            f'<section aria-labelledby="{esc(land["ordner"])}">\n<h2 id="{esc(land["ordner"])}">{esc(land["name"])}</h2>\n'
            f'<ul class="kalender">\n' + "\n".join(zeilen) + '\n</ul>\n'
            f'<div class="hinweis"><p>{esc(land.get("hinweis", ""))}</p>\n'
            f'<p>Ferien eingetragen bis {datum_lang(kalender[0]["ferien_bis"])}. Quelle: '
            f'<a href="{esc(beleg)}">{esc(quelle["fundstelle"])}</a>.</p></div>\n</section>')
    apps = "\n".join(f"<li><h3>{esc(n)}</h3>\n<p>{esc(t)}</p></li>" for n, t in APPS)
    stand = datum_lang(alle[0][1][0]["erzeugt"]) if alle else ""
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Feiertage und Schulferien als Kalender</title>
<meta name="description" content="Gesetzliche Feiertage und Schulferien für Bayern und Brandenburg zum Abonnieren in jeder Kalender-App und als JSON.">
<meta name="theme-color" content="#fcfaf8">
<link rel="icon" href="favicon.ico" sizes="32x32">
<link rel="icon" href="icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preload" href="schriften/young-serif.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="stil.css">
</head>
<body>
<header class="kopf">
<div class="rahmen">
<img src="bildmarke.svg" alt="" width="56" height="83">
<div>
<p class="label">Kalender-Abo</p>
<h1>Feiertage und Schulferien</h1>
<p class="lead">Gesetzliche Feiertage und Schulferien für deinen Kalender – einmal abonnieren, dann bleiben sie von
selbst aktuell. Alle Termine sind ganztägig, als „frei“ markiert und ohne Erinnerung.</p>
</div>
</div>
</header>
<main class="rahmen">
{chr(10).join(teile)}
<section aria-labelledby="anleitung">
<h2 id="anleitung">So abonnierst du</h2>
<ul class="schritte">
{apps}
</ul>
<div class="hinweis"><p>Für Programme und Webseiten gibt es jeden Kalender auch als <code>.json</code>. Das Format und
Hinweise zum Abgleich stehen in der <a href="{QUELLTEXT}#json-format">Beschreibung auf GitHub</a>.</p></div>
</section>
</main>
<footer>
<div class="rahmen">
<p>Angaben ohne Gewähr – maßgeblich sind die amtlichen Veröffentlichungen. Fehler meldest du am besten als
<a href="{QUELLTEXT}/issues">Issue auf GitHub</a>; dort liegen auch die Daten, die Belege und der Quelltext.</p>
<p>Daten frei verwendbar (CC0 1.0). Stand: {stand}.</p>
</div>
</footer>
<script src="kopieren.js" defer></script>
</body>
</html>
"""


def erzeugen(ziel):
    laender, fehler = pruefe_alles()
    if fehler:
        return melde(fehler)
    erzeugt = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    alle = [(land, kalender_des_landes(land, erzeugt=erzeugt)) for land in laender]
    for _, kalender in alle:
        for kal in kalender:
            pfad = os.path.join(ziel, *kal["kalender"]["kennung"].split("/"))
            os.makedirs(os.path.dirname(pfad), exist_ok=True)
            with open(pfad + ".ics", "w", encoding="utf-8", newline="") as f:
                f.write(ics(kal))
            with open(pfad + ".json", "w", encoding="utf-8", newline="\n") as f:
                f.write(als_json(kal))
            print(f"{kal['kalender']['kennung']}: {len(kal['termine'])} Termine, ab {kal['fenster_von']}")
    with open(os.path.join(ziel, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(startseite(alle))
    shutil.copytree(os.path.join(REPO, "seite"), ziel, dirs_exist_ok=True)   # Stil, Schriften, Bildmarke, Favicons
    return 0


def melde(fehler):
    for x in fehler:
        print(f"FEHLER {x}")
    print(f"{len(fehler)} Fehler")
    return 1


def ausgabe_lesen(ordner):
    """{Kennung: {uid: (name, von, bis)}} aus den JSON-Dateien eines Ausgabe-Ordners."""
    aus = {}
    for wurzel, _, dateien in os.walk(ordner):
        for datei in dateien:
            if datei.endswith(".json"):
                with open(os.path.join(wurzel, datei), encoding="utf-8") as f:
                    kal = json.load(f)
                aus[kal["kalender"]["kennung"]] = {t["uid"]: (t["name"], t["von"], t["bis"]) for t in kal["termine"]}
    return aus


def vergleich(alt, neu):
    a = ausgabe_lesen(alt) if os.path.isdir(alt) else {}
    n = ausgabe_lesen(neu)
    print("### Änderungen der Termine\n")
    if not a:
        print("Kein früherer Stand zum Vergleich.\n")
    for kennung in sorted(set(a) | set(n)):
        x, y = a.get(kennung, {}), n.get(kennung, {})
        zeilen = [f"- neu: {y[u][1]} bis {y[u][2]} {y[u][0]}" for u in sorted(set(y) - set(x), key=lambda u: y[u][1])]
        zeilen += [f"- entfällt: {x[u][1]} bis {x[u][2]} {x[u][0]}" for u in sorted(set(x) - set(y), key=lambda u: x[u][1])]
        zeilen += [f"- geändert: {x[u][1]} bis {x[u][2]} {x[u][0]} → {y[u][1]} bis {y[u][2]} {y[u][0]}"
                   for u in sorted(set(x) & set(y)) if x[u] != y[u]]
        print(f"**{kennung}** – {len(y)} Termine, {len(zeilen)} Änderungen")
        for z in zeilen[:40]:
            print(z)
        if len(zeilen) > 40:
            print(f"- … und {len(zeilen) - 40} weitere")
        print()
    return 0


def main(argv):
    modus = argv[1] if len(argv) > 1 else ""
    if modus == "pruefen":
        laender, fehler = pruefe_alles()
        if fehler:
            return melde(fehler)
        for land in laender:
            von, bis_jahr, ferien_bis = fenster(land)
            print(f"{land['name']}: {len(land['ferien'])} Ferien bis {ferien_bis}, Kalender ab {von}, "
                  f"Feiertage bis {bis_jahr}")
        print("Daten in Ordnung")
        return 0
    if modus == "erzeugen":
        return erzeugen(argv[2] if len(argv) > 2 else os.path.join(REPO, "ausgabe"))
    if modus == "liste" and len(argv) > 2:
        laender, fehler = pruefe_alles()
        if fehler:
            return melde(fehler)
        for land in laender:
            for kal in kalender_des_landes(land):
                if kal["kalender"]["kennung"] == argv[2]:
                    for t in kal["termine"]:
                        print(f"{t['von']}\t{t['bis']}\t{t['art']}\t{t['name']}\t{t['uid']}")
                    return 0
        print(f"Kalender {argv[2]} gibt es nicht")
        return 1
    if modus == "vergleich" and len(argv) > 3:
        return vergleich(argv[2], argv[3])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
