#!/usr/bin/env python3
"""Erzeugte Kalender mit einem unabhängigen Parser (icalendar) lesen und gegen die JSON-Dateien halten.

  python3 tests/ics_pruefen.py ausgabe
"""
import datetime as dt
import json
import os
import sys

import icalendar

ERWARTET = ["bayern/alle", "bayern/alle-ohne-mariae-himmelfahrt", "bayern/feiertage",
            "bayern/feiertage-ohne-mariae-himmelfahrt", "bayern/ferien",
            "brandenburg/alle", "brandenburg/feiertage", "brandenburg/ferien"]


def main(ordner):
    fehler = []
    for kennung in ERWARTET:
        pfad = os.path.join(ordner, *kennung.split("/"))
        if not (os.path.isfile(pfad + ".ics") and os.path.isfile(pfad + ".json")):
            fehler.append(f"{kennung}: .ics oder .json fehlt")
            continue
        with open(pfad + ".json", encoding="utf-8") as f:
            daten = json.load(f)
        with open(pfad + ".ics", "rb") as f:
            kal = icalendar.Calendar.from_ical(f.read())
        soll = {t["uid"]: t for t in daten["termine"]}
        ist = {}
        for ev in kal.walk("VEVENT"):
            von, bis = ev.decoded("DTSTART"), ev.decoded("DTEND")
            uid = str(ev["UID"])
            if isinstance(von, dt.datetime) or isinstance(bis, dt.datetime):
                fehler.append(f"{kennung} {uid}: nicht ganztägig")
            if str(ev.get("TRANSP")) != "TRANSPARENT" or list(ev.walk("VALARM")):
                fehler.append(f"{kennung} {uid}: nicht als frei markiert oder mit Erinnerung")
            ist[uid] = (str(ev["SUMMARY"]), von.isoformat(), bis.isoformat())
        if ist != {u: (t["name"], t["von"], t["bis_exklusiv"]) for u, t in soll.items()}:
            fehler.append(f"{kennung}: Termine in .ics und .json unterscheiden sich")
        if daten.get("format") != 1 or daten["kalender"]["kennung"] != kennung or not daten["termine"]:
            fehler.append(f"{kennung}: JSON-Kopf stimmt nicht")
        if str(kal.get("PRODID")) != "-//feiertage-kalender//DE" or str(kal.get("X-WR-CALNAME")) != daten["kalender"]["name"]:
            fehler.append(f"{kennung}: PRODID oder Kalendername stimmt nicht")
        print(f"{kennung}: {len(ist)} Termine, ab {daten['fenster_von']}, Ferien bis {daten['ferien_bis']}")
    if not os.path.isfile(os.path.join(ordner, "index.html")):
        fehler.append("index.html fehlt")
    for x in fehler:
        print(f"FEHLER {x}")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "ausgabe"))
