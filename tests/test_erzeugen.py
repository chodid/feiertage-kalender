"""Prüfung der Daten und der Erzeugung: python3 -m unittest discover -s tests"""
import copy
import datetime as dt
import os
import re
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
import erzeugen as e  # noqa: E402

TAG = dt.date(2026, 11, 23)


def land(ordner):
    laender, fehler = e.laender_lesen(os.path.join(REPO, "daten"))
    assert not fehler, fehler
    return copy.deepcopy(next(x for x in laender if x["ordner"] == ordner))


def kalender(ordner, tag=TAG):
    return {k["kalender"]["kennung"]: k for k in e.kalender_des_landes(land(ordner), tag)}


class Daten(unittest.TestCase):
    def test_echte_daten_ohne_fehler(self):
        _, fehler = e.pruefe_alles(os.path.join(REPO, "daten"), REPO)
        self.assertEqual(fehler, [])

    def fehler(self, aendern):
        by = land("bayern")
        aendern(by)
        return " | ".join(e.pruefe_land(by, REPO))

    def test_bis_vor_von(self):
        self.assertIn("bis liegt vor von", self.fehler(lambda l: l["ferien"][0].update(bis="2025-07-01")))

    def test_ueberschneidung(self):
        self.assertIn("überschneiden sich", self.fehler(lambda l: l["ferien"][1].update(von="2025-09-10")))

    def test_gleicher_beginn(self):
        self.assertIn("beginnen am", self.fehler(lambda l: l["ferien"].append(dict(l["ferien"][0], bis="2025-08-05"))))

    def test_fehlender_beleg(self):
        self.assertIn("Beleg-Datei", self.fehler(lambda l: l["quelle"].update(beleg="belege/gibt-es-nicht.pdf")))

    def test_beleg_ausserhalb(self):
        self.assertIn("muss eine Datei in belege/", self.fehler(lambda l: l["quelle"].update(beleg="../LICENSE")))

    def test_quelle_fehlt(self):
        self.assertIn("quelle.fundstelle fehlt", self.fehler(lambda l: l["quelle"].pop("fundstelle")))

    def test_unbekannte_kennung(self):
        self.assertIn("unbekannt", self.fehler(lambda l: l["feiertage"].append("tag-des-bieres")))

    def test_kennung_doppelt(self):
        self.assertIn("mehrfach", self.fehler(lambda l: l["schulfrei"].append("neujahr")))

    def test_kein_datum(self):
        self.assertIn("Datumsangaben", self.fehler(lambda l: l["ferien"][0].update(von="2025-02-30")))

    def test_name_ungueltig(self):
        self.assertIn("Name höchstens", self.fehler(lambda l: l["ferien"][0].update(name="Ferien <b>")))

    def test_zu_lang(self):
        self.assertIn("länger als 70 Tage", self.fehler(lambda l: l["ferien"][0].update(bis="2025-10-31")))

    def test_verweis_ohne_https(self):
        self.assertIn("verweise Nr. 1", self.fehler(lambda l: l["verweise"][0].update(adresse="http://example.org/")))

    def test_feld_zu_viel(self):
        self.assertIn("erwartet genau", self.fehler(lambda l: l["ferien"][0].update(notiz="x")))


class Berechnung(unittest.TestCase):
    def test_pruefliste(self):
        self.assertEqual(e.pruefe_berechnung(), [])

    def test_feste_tage_2026(self):
        soll = {"karfreitag": "2026-04-03", "ostermontag": "2026-04-06", "christi-himmelfahrt": "2026-05-14",
                "pfingstmontag": "2026-05-25", "fronleichnam": "2026-06-04", "buss-und-bettag": "2026-11-18"}
        for kennung, datum in soll.items():
            self.assertEqual(e.TAGE[kennung][1](2026).isoformat(), datum, kennung)


class Kalender(unittest.TestCase):
    def test_acht_kalender(self):
        self.assertEqual(sorted(list(kalender("bayern")) + list(kalender("brandenburg"))), [
            "bayern/alle", "bayern/alle-ohne-mariae-himmelfahrt", "bayern/feiertage",
            "bayern/feiertage-ohne-mariae-himmelfahrt", "bayern/ferien",
            "brandenburg/alle", "brandenburg/feiertage", "brandenburg/ferien"])

    def namen(self, kennung):
        return {t["name"] for t in kalender(kennung.split("/")[0])[kennung]["termine"]}

    def test_mariae_himmelfahrt_nur_mit(self):
        for k, drin in (("bayern/feiertage", True), ("bayern/alle", True), ("bayern/ferien", False),
                        ("bayern/feiertage-ohne-mariae-himmelfahrt", False),
                        ("bayern/alle-ohne-mariae-himmelfahrt", False), ("brandenburg/alle", False)):
            self.assertEqual("Mariä Himmelfahrt" in self.namen(k), drin, k)

    def test_buss_und_bettag_bei_den_ferien(self):
        name = "Buß- und Bettag (schulfrei)"
        for k, drin in (("bayern/ferien", True), ("bayern/alle", True), ("bayern/alle-ohne-mariae-himmelfahrt", True),
                        ("bayern/feiertage", False), ("bayern/feiertage-ohne-mariae-himmelfahrt", False),
                        ("brandenburg/alle", False)):
            self.assertEqual(name in self.namen(k), drin, k)
        t = next(t for t in kalender("bayern")["bayern/alle"]["termine"] if t["name"] == name and t["von"] > "2026")
        self.assertEqual((t["uid"], t["art"], t["bis"]), ("ff-ferien-by-2026-11-18@feiertage-kalender", "ferien", "2026-11-18"))

    def test_fenster(self):
        for jahr, von in ((2026, "2025-01-01"), (2028, "2025-01-01"), (2029, "2026-01-01"), (2031, "2028-01-01")):
            k = kalender("bayern", dt.date(jahr, 1, 2))["bayern/alle"]
            self.assertEqual(k["fenster_von"], von)
            self.assertTrue(all(t["bis"] >= von for t in k["termine"]))
            letztes = max(t["von"] for t in k["termine"] if t["art"] == "feiertag")[:4]
            self.assertEqual(int(letztes), max(2030, jahr + 2))

    def test_aufbau(self):
        muster = re.compile(r"ff-(feiertag-(by|bb)-\d{4}-[a-z0-9-]+|ferien-(by|bb)-\d{4}-\d{2}-\d{2})@feiertage-kalender")
        for ordner in ("bayern", "brandenburg"):
            for k in kalender(ordner).values():
                self.assertEqual(k["format"], 1)
                self.assertEqual(set(k), {"format", "kalender", "land", "erzeugt", "fenster_von", "ferien_bis", "quelle",
                                          "lizenz", "termine"})
                uids = [t["uid"] for t in k["termine"]]
                self.assertEqual(len(uids), len(set(uids)))
                self.assertEqual(k["termine"], sorted(k["termine"], key=lambda t: (t["von"], t["uid"])))
                for t in k["termine"]:
                    self.assertRegex(t["uid"], muster)
                    self.assertIn(f"-{k['land']['kuerzel']}-", t["uid"])
                    self.assertLessEqual(t["von"], t["bis"])
                    self.assertEqual(dt.date.fromisoformat(t["bis"]) + e.EIN_TAG, dt.date.fromisoformat(t["bis_exklusiv"]))
                    if t["art"] == "feiertag":
                        self.assertEqual(t["von"], t["bis"])

    def test_gleiche_uid_in_allen_kalendern(self):
        k = kalender("bayern")
        alle = {t["uid"]: t for t in k["bayern/alle"]["termine"]}
        for kennung, kal in k.items():
            for t in kal["termine"]:
                self.assertEqual(t, alle[t["uid"]], kennung)

    def test_ics(self):
        for k in kalender("bayern").values():
            text = e.ics(k)
            self.assertTrue(text.endswith("END:VCALENDAR\r\n"))
            self.assertNotIn("\n", text.replace("\r\n", ""))
            for zeile in text.split("\r\n"):
                self.assertLessEqual(len(zeile.encode("utf-8")), 75)
            self.assertEqual(text.count("BEGIN:VEVENT"), len(k["termine"]))
            self.assertIn("PRODID:-//feiertage-kalender//DE", text)
            self.assertNotIn("VALARM", text)

    def test_json_ohne_interne_felder(self):
        self.assertNotIn("_text", e.als_json(kalender("bayern")["bayern/alle"]))


if __name__ == "__main__":
    unittest.main()
