# feiertage-kalender

Gesetzliche Feiertage und Schulferien für **Bayern** und **Brandenburg** als Kalender zum Abonnieren (`.ics`) und
als maschinenlesbare Daten (`.json`). Ohne Anmeldung, ohne Passwort, täglich abrufbar.

Übersicht mit allen Adressen: <https://chodid.github.io/feiertage-kalender/>

## Kalender

Jede Adresse gibt es als `.ics` (Kalender-Abo) und als `.json` (für Programme). Für das Abo in einer Kalender-App
entweder die `https://`-Adresse eintragen oder die Adresse mit `webcal://` statt `https://` öffnen.

| Kalender | Adresse (`.ics`) |
|---|---|
| Feiertage Bayern (mit Mariä Himmelfahrt) | `https://chodid.github.io/feiertage-kalender/bayern/feiertage.ics` |
| Feiertage Bayern (ohne Mariä Himmelfahrt) | `https://chodid.github.io/feiertage-kalender/bayern/feiertage-ohne-mariae-himmelfahrt.ics` |
| Schulferien Bayern | `https://chodid.github.io/feiertage-kalender/bayern/ferien.ics` |
| Feiertage & Ferien Bayern (mit Mariä Himmelfahrt) | `https://chodid.github.io/feiertage-kalender/bayern/alle.ics` |
| Feiertage & Ferien Bayern (ohne Mariä Himmelfahrt) | `https://chodid.github.io/feiertage-kalender/bayern/alle-ohne-mariae-himmelfahrt.ics` |
| Feiertage Brandenburg | `https://chodid.github.io/feiertage-kalender/brandenburg/feiertage.ics` |
| Schulferien Brandenburg | `https://chodid.github.io/feiertage-kalender/brandenburg/ferien.ics` |
| Feiertage & Ferien Brandenburg | `https://chodid.github.io/feiertage-kalender/brandenburg/alle.ics` |

Die JSON-Datei liegt jeweils unter derselben Adresse mit der Endung `.json`.

### Abonnieren

- **Apple Kalender (iPhone, iPad, Mac):** Ablage bzw. Kalender → „Kalenderabo hinzufügen“ und die Adresse einfügen.
- **Google Kalender:** im Browser links bei „Weitere Kalender“ auf „+“ → „Per URL“ und die Adresse einfügen.
- **Outlook:** Kalender hinzufügen → „Aus dem Internet abonnieren“ und die Adresse einfügen.
- **Thunderbird:** Neuer Kalender → „Im Netzwerk“ und die Adresse einfügen.

Alle Termine sind ganztägig, als „frei“ markiert und haben keine Erinnerung. Die Kalender-Apps rufen die Adresse
selbst regelmäßig ab; wie oft, bestimmt die App.

## Was enthalten ist

- **Bayern – Feiertage:** Neujahr, Heilige Drei Könige, Karfreitag, Ostermontag, Tag der Arbeit, Christi Himmelfahrt,
  Pfingstmontag, Fronleichnam, Tag der Deutschen Einheit, Allerheiligen, 1. und 2. Weihnachtstag.
- **Mariä Himmelfahrt (15. August)** ist in Bayern nur in Gemeinden mit überwiegend katholischer Bevölkerung
  gesetzlicher Feiertag. Deshalb gibt es die bayerischen Kalender mit und ohne diesen Tag. Welche Gemeinden dazu
  gehören, steht in der
  [Gemeindeliste des Bayerischen Landesamts für Statistik](https://statistik.bayern.de/statistik/gebiet_bevoelkerung/zensus/himmelfahrt/index.php).
- **Buß- und Bettag** ist in Bayern kein gesetzlicher Feiertag, aber unterrichtsfrei. Er steht deshalb als
  „Buß- und Bettag (schulfrei)“ bei den **Ferien**, nicht bei den Feiertagen.
- Das **Augsburger Friedensfest** (8. August, nur Stadt Augsburg) ist nicht enthalten.
- **Brandenburg – Feiertage:** Neujahr, Karfreitag, Ostersonntag, Ostermontag, Tag der Arbeit, Christi Himmelfahrt,
  Pfingstsonntag, Pfingstmontag, Tag der Deutschen Einheit, Reformationstag, 1. und 2. Weihnachtstag.
- **Schulferien** wie amtlich veröffentlicht, mit erstem und letztem Ferientag. In Brandenburg gehören dazu auch
  einzelne unterrichtsfreie Tage („Variabler Ferientag“).

### Zeitraum

Die Kalender beginnen am 1. Januar des dritten Vorjahres, frühestens aber im ersten Jahr, für das Ferien-Daten
vorliegen (derzeit 2025). Ferien reichen so weit, wie sie amtlich veröffentlicht und hier eingetragen sind; das
letzte Datum steht in der JSON-Datei als `ferien_bis`. Feiertage reichen bis zum letzten Jahr der Ferien-Daten,
mindestens bis zum übernächsten Jahr.

### Quellen

| Land | Quelle der Ferien | Beleg im Repo |
|---|---|---|
| Bayern | Ferienordnung und schulfreie Samstage für die Schuljahre 2024/2025 bis 2029/2030, Bekanntmachung des Bayerischen Staatsministeriums für Unterricht und Kultus vom 7. Dezember 2022, BayMBl. 2022 Nr. 747 | [`belege/bayern-baymbl-2022-747.pdf`](belege/bayern-baymbl-2022-747.pdf) |
| Brandenburg | VV-Schulbetrieb, Anlage 1: Schulferien für die Schuljahre 2022/2023 bis 2029/2030; Ministerium für Bildung, Jugend und Sport: <https://mbjs.brandenburg.de/bildung/weitere-themen/schulferien-brandenburg.html> | [`belege/brandenburg-vv-schulbetrieb-anlage-1.pdf`](belege/brandenburg-vv-schulbetrieb-anlage-1.pdf) |

Die Feiertage werden nach den Feiertagsgesetzen der Länder berechnet (bewegliche Tage aus dem Osterdatum).

**Ohne Gewähr.** Maßgeblich sind die amtlichen Veröffentlichungen. Fehler bitte als
[Issue](https://github.com/chodid/feiertage-kalender/issues) melden.

## JSON-Format

Für Webseiten und Programme. Beispiel `bayern/alle.json` (gekürzt):

```json
{
  "format": 1,
  "kalender": {"kennung": "bayern/alle", "name": "Feiertage & Ferien Bayern"},
  "land": {"kuerzel": "by", "name": "Bayern"},
  "erzeugt": "2026-11-23T07:39:17Z",
  "fenster_von": "2025-01-01",
  "ferien_bis": "2030-09-09",
  "quelle": {"titel": "Ferienordnung …", "fundstelle": "BayMBl. 2022 Nr. 747 vom 21.12.2022"},
  "lizenz": "CC0-1.0",
  "termine": [
    {"uid": "ff-feiertag-by-2026-ostermontag@feiertage-kalender", "name": "Ostermontag", "art": "feiertag",
     "von": "2026-04-06", "bis": "2026-04-06", "bis_exklusiv": "2026-04-07"},
    {"uid": "ff-ferien-by-2026-08-03@feiertage-kalender", "name": "Sommerferien", "art": "ferien",
     "von": "2026-08-03", "bis": "2026-09-14", "bis_exklusiv": "2026-09-15"}
  ]
}
```

| Feld | Bedeutung |
|---|---|
| `format` | Version des Formats, derzeit `1`. Änderungen an Format 1 sind nur abwärtskompatibel (neue Felder); bei einem Bruch gibt es eine neue Nummer und neue Dateinamen. |
| `kalender` | `kennung` (Pfad ohne Endung) und `name` des Kalenders |
| `land` | `kuerzel` (`by`, `bb`) und `name` |
| `erzeugt` | Zeitpunkt der Erzeugung (UTC) |
| `fenster_von` | erster Tag, ab dem der Kalender Termine enthält |
| `ferien_bis` | letzter Ferientag, der für das Land eingetragen ist |
| `quelle` | Quelle der Ferien-Daten: `titel`, `fundstelle`, wenn vorhanden `adresse` |
| `lizenz` | Lizenz der Daten (`CC0-1.0`) |
| `termine` | Liste, sortiert nach `von`, dann `uid` |
| `termine[].uid` | feste Kennung des Termins, gleich in allen Kalendern und gleich der `UID` in der `.ics` |
| `termine[].art` | `feiertag` oder `ferien` (schulfreie Tage wie der Buß- und Bettag zählen als `ferien`) |
| `termine[].von`, `bis` | erster und letzter Tag (einschließlich), `JJJJ-MM-TT` |
| `termine[].bis_exklusiv` | Tag nach dem letzten Tag (so erwarten es viele Kalender-Programme) |

Aufbau der Kennungen: `ff-feiertag-<land>-<jahr>-<name>@feiertage-kalender` und
`ff-ferien-<land>-<erster Tag>@feiertage-kalender`.

### Abgleich in eine eigene Datenbank

- Über `uid` abgleichen: unbekannte `uid` → neu anlegen; bekannte `uid` mit anderem `name`, `von` oder `bis` →
  ändern; eigene Einträge, deren `uid` fehlt **und** die am oder nach `fenster_von` enden → entfernen.
- Einträge, die vor `fenster_von` enden, **nicht** löschen: Sie fallen nur aus dem Zeitraum der Datei, es gibt sie
  weiterhin.
- Einen Abruf, der fehlschlägt, kein gültiges JSON liefert, ein anderes `format` als `1` hat oder keine Termine
  enthält, verwerfen und mit dem letzten Stand weiterarbeiten.
- Ein Abruf am Tag genügt. Die Daten ändern sich nur, wenn neue Schuljahre eingetragen oder Fehler behoben werden,
  und einmal im Januar, wenn der Zeitraum weiterrückt.

## Aufbau des Repos und Pflege

| Pfad | Inhalt |
|---|---|
| `daten/<land>.json` | je Land: Feiertage (Kennungen), Ferien mit erstem und letztem Tag, Quelle, Hinweis und Verweise für die Eingangsseite |
| `belege/` | amtliche Veröffentlichungen, aus denen die Ferien übernommen sind |
| `erzeugen.py` | prüft die Daten und erzeugt alle Kalender (nur Python-Standardbibliothek) |
| `seite/` | Stil, Schriften, Bildmarke und Favicons der Eingangsseite (werden unverändert mitveröffentlicht) |
| `tests/` | Tests der Prüfung und der Erzeugung |
| `.github/workflows/kalender.yml` | prüft jeden Pull Request; veröffentlicht nach dem Merge auf GitHub Pages |

```sh
python3 erzeugen.py pruefen              # Daten prüfen
python3 -m unittest discover -s tests    # Tests
python3 erzeugen.py erzeugen             # Kalender nach ausgabe/ schreiben
python3 erzeugen.py liste bayern/alle    # Termine eines Kalenders ansehen
```

**Neue Schuljahre eintragen:** Beleg nach `belege/` legen, Ferien in `daten/<land>.json` ergänzen (`von` und `bis`
einschließlich, wie veröffentlicht), `quelle` anpassen, Pull Request stellen. Der Lauf des Pull Requests zeigt in der
Zusammenfassung, welche Termine neu sind, entfallen oder sich ändern.

Die veröffentlichten Dateien entstehen bei jedem Merge nach `main`, bei einem Start von Hand (Actions → „Kalender“ →
„Run workflow“) und am 2. Januar. Dateinamen und Kennungen bleiben stabil, weil Abos daran hängen.

## Lizenz

- Programmcode: [AGPL-3.0](LICENSE)
- Daten in `daten/`, Belege und die erzeugten Kalender: [CC0 1.0](LICENSE-DATA) – frei verwendbar, ohne Bedingungen.
- Schriften der Eingangsseite (`seite/schriften/`: Young Serif, Source Sans 3, Source Code Pro): SIL Open Font License 1.1,
  Lizenztexte liegen daneben. Die Bildmarke und die Favicons in `seite/` sind **nicht** frei verwendbar – sie gehören
  nicht zu den Daten und nicht zum freien Quelltext.

## English summary

Public holidays and school holidays for the German states of Bavaria (*Bayern*) and Brandenburg as subscribable
calendars (`.ics`) and JSON, served from GitHub Pages: <https://chodid.github.io/feiertage-kalender/>. Paths:
`bayern/feiertage`, `bayern/feiertage-ohne-mariae-himmelfahrt` (without Assumption Day, which is a public holiday
only in predominantly Catholic municipalities), `bayern/ferien`, `bayern/alle`, `bayern/alle-ohne-mariae-himmelfahrt`,
`brandenburg/feiertage`, `brandenburg/ferien`, `brandenburg/alle` – each with `.ics` and `.json`. All events are
all-day and marked as free. School holidays are taken from the official publications in `belege/`; public holidays
are computed. No warranty. Code: AGPL-3.0, data and generated calendars: CC0 1.0.
