"""Offline tests for the provenance columns and `export --lead-format`.

Run from pfade/google-maps:  python3 -m unittest discover -s tests -v
No network: the blocklist check, the own blocklist and the licence server are stubbed.
"""
from __future__ import annotations

import csv
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# safety net: the licence server (werkzeuge/lizenz.py) is never reached, the key folder is temporary
os.environ["ABMAHNSCHUTZ_API_URL"] = "http://127.0.0.1:9"
os.environ["ABMAHNSCHUTZ_ORDNER"] = tempfile.mkdtemp()

from scraper import db, export, sperrliste  # noqa: E402
from scraper.blockliste import Blockliste  # noqa: E402
from scraper.sperrliste import Sperrliste, lizenz  # noqa: E402

# The contract for the landing pages — spelled out here on purpose, not imported
FELDER = [
    "externe_id", "firma", "rechtsform", "domain", "website", "strasse", "plz", "ort", "land",
    "telefon", "branche", "mitarbeiter", "handelsregister", "anrede", "vorname", "nachname",
    "position", "email", "email_typ", "email_status", "kontakt_telefon", "linkedin_url",
    "quelle", "quelle_url", "erfasst_am", "personalisierung", "video_titel",
]

LEADS = [
    {   # list 1: managing director address
        "business_id": "biz-alpha", "place_id": "ChIJalpha",
        "firmenname": "Alpha Ingenieure", "firmenname_final": "Alpha Ingenieure GmbH",
        "website_final": "https://www.alpha-ing.de/kontakt", "zip": "80331",
        "address": "Maps-Weg 9, 80331 München", "adresse_impressum": "Alpha GmbH, Hauptstr. 1, 80331 München",
        "telefon_impressum": "+49 89 123", "phone_imported": "+49 89 999", "category": "Ingenieurbüro",
        "query_keyword": "Ingenieurbüro", "query_city": "München", "query_country": "DE",
        "impressum_raw": json.dumps({"impressum_url": "https://www.alpha-ing.de/impressum",
                                     "handelsregister_court": "Amtsgericht München",
                                     "handelsregister_number": "HRB 12345"}),
        "email_final": "max.muster@alpha-ing.de", "email_final_type": "GF",
        "email_final_status": "Safe to Send", "anrede": "Herr", "first_name": "Max",
        "last_name": "Muster", "linkedin_url": "https://www.linkedin.com/in/max-muster",
        "personalisierung": "Ihr Brückenprojekt in Freising ist mir aufgefallen.",
        "video_title": "Max, kurz zu Alpha", "created_at": "2026-10-17 11:22:23",
        "updated_at": "2026-10-20 08:15:00",
    },
    {   # list 2: info@ address, no Maps ids -> fallback ds-<id>
        "business_id": None, "place_id": None,
        "firmenname": "Beta Planung", "firmenname_final": "Beta Planung OG",
        "website_final": "http://beta-planung.at", "zip": "1010", "address": "",
        "adresse_impressum": "", "telefon_impressum": "", "phone_imported": "+43 1 555",
        "category": "Planungsbüro", "query_keyword": "Planungsbüro", "query_city": "Wien",
        "query_country": "AT", "impressum_raw": "{}", "email_final": "info@beta-planung.at",
        "email_final_type": "Info@", "email_final_status": "Risky", "anrede": "",
        "first_name": "", "last_name": "", "linkedin_url": None, "personalisierung": "",
        "video_title": "Kurz zu Beta", "created_at": "2026-10-18 09:00:00", "updated_at": None,
    },
    {   # list 1 candidate, but blocked by the subscription check -> list 5 only
        "business_id": "biz-gesperrt", "place_id": "ChIJgesperrt",
        "firmenname": "Gesperrt", "firmenname_final": "Gesperrt GmbH",
        "website_final": "https://gesperrt.de", "zip": "10115", "query_keyword": "Ingenieurbüro",
        "query_city": "Berlin", "query_country": "DE", "email_final": "chef@gesperrt.de",
        "email_final_type": "GF", "email_final_status": "Safe to Send", "anrede": "Frau",
        "first_name": "Erika", "last_name": "Beispiel", "created_at": "2026-10-17 10:00:00",
    },
]


def _lies_csv(pfad: Path) -> list[dict[str, str]]:
    with pfad.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


class ExportFixture(unittest.TestCase):
    """Three leads in a temporary database; blocklist check, own blocklist and licence server stubbed."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        tmp = Path(self.tmp.name)
        self.export_dir = tmp / "exports"
        self.conn = sqlite3.connect(tmp / "leads.db")
        self.conn.row_factory = sqlite3.Row
        db.init(self.conn)
        self.ds_ids = []
        for lead in LEADS:
            cur = self.conn.execute(
                "INSERT INTO datensaetze (business_id, place_id, firmenname) VALUES (?, ?, ?)",
                (lead.get("business_id"), lead.get("place_id"), lead["firmenname"]))
            self.ds_ids.append(cur.lastrowid)
            daten = {**lead, "datensatz_id": cur.lastrowid, "ready_to_send": 1, "bereits_exportiert": 0}
            spalten = ",".join(daten)
            self.conn.execute(f"INSERT INTO anreicherung ({spalten}) VALUES ({','.join('?' * len(daten))})",
                              list(daten.values()))
        self.conn.commit()

        self.sperre = Sperrliste({"gesperrt.de"}, "Test-Stub")
        self.eigene = Blockliste(set(), set())
        self.server: list[tuple[str, str, dict]] = []   # requests that would have reached the licence server
        self.patches = [
            mock.patch.object(export, "EXPORT_DIR", self.export_dir),
            mock.patch.object(export, "KAMPAGNE", "testkampagne"),
            mock.patch.object(export.sperrliste_mod, "laden", side_effect=lambda *a, **k: self.sperre),
            mock.patch.object(export.blockliste_mod, "laden", side_effect=lambda: self.eigene),
            mock.patch.object(lizenz, "ist_pro", side_effect=lambda: self.sperre is not None),
            mock.patch.object(lizenz, "hinweise_text", return_value=[]),
            mock.patch.object(lizenz, "_aufruf", side_effect=lambda m, pfad, body=None, **k:
                              self.server.append((m, pfad, body)) or {}),
        ]
        # export calls the real upload (lizenz._lead filters the fields), only the HTTP call is stubbed
        self.patches.append(mock.patch.object(sperrliste, "hochladen", wraps=sperrliste.hochladen))
        for p in self.patches:
            p.start()
        self.hochladen = sperrliste.hochladen

    def tearDown(self) -> None:
        for p in self.patches:
            p.stop()
        self.conn.close()
        self.tmp.cleanup()

    def _export(self, **kwargs) -> dict[str, tuple[Path, int]]:
        ergebnis = export.export_listen(self.conn, **kwargs)
        return {bezeichnung: (pfad, anzahl) for bezeichnung, pfad, anzahl in ergebnis}

    def _datei(self, muster: str) -> Path:
        treffer = sorted(self.export_dir.glob(muster))
        self.assertEqual(len(treffer), 1, f"{muster}: {treffer}")
        return treffer[0]


class LeadFormatTest(ExportFixture):
    def test_csv_listen_haben_herkunftsspalten(self) -> None:
        self._export()
        liste1 = _lies_csv(self._datei("1_zielgruppe_geschaeftsfuehrer_*.csv"))
        liste2 = _lies_csv(self._datei("2_zielgruppe_info_*.csv"))
        for spalte in ("Externe ID", "Quelle URL", "Erfasst am"):
            self.assertIn(spalte, liste1[0])
            self.assertIn(spalte, liste2[0])

        self.assertEqual([r["Firmenname"] for r in liste1], ["Alpha Ingenieure GmbH"])
        alpha = liste1[0]
        self.assertEqual(alpha["Externe ID"], "biz-alpha")
        self.assertEqual(alpha["Quelle URL"], "https://www.alpha-ing.de/impressum")
        self.assertEqual(alpha["Erfasst am"], "2026-10-20")

        beta = liste2[0]
        self.assertEqual(beta["Externe ID"], f"ds-{self.ds_ids[1]}")
        self.assertEqual(beta["Quelle URL"], "")
        self.assertEqual(beta["Erfasst am"], "2026-10-18")   # fallback created_at

        gesperrt = _lies_csv(self._datei("5_gesperrt_sperrliste_*.csv"))
        self.assertEqual([r["Firmenname"] for r in gesperrt], ["Gesperrt"])

    def test_ohne_schalter_kein_lead_format(self) -> None:
        self._export()
        self.assertEqual(list(self.export_dir.glob("leads_testkampagne_*.json")), [])

    def test_lead_format_json(self) -> None:
        ergebnis = self._export(lead_format=True)
        pfad = self._datei("leads_testkampagne_*.json")
        self.assertEqual(ergebnis["Lead-Format (JSON, Listen 1 + 2)"], (pfad, 2))

        leads = json.loads(pfad.read_text(encoding="utf-8"))
        self.assertIsInstance(leads, list)
        self.assertEqual(len(leads), 2)
        for lead in leads:
            self.assertEqual(list(lead), FELDER)
            self.assertTrue(all(isinstance(v, str) for v in lead.values()), lead)

        ids = [l["externe_id"] for l in leads]
        self.assertNotIn("biz-gesperrt", ids)
        self.assertFalse(any("gesperrt" in l["email"] or "gesperrt" in l["domain"] for l in leads))

        alpha, beta = leads
        self.assertEqual(alpha, {
            "externe_id": "biz-alpha",
            "firma": "Alpha Ingenieure GmbH",
            "rechtsform": "",
            "domain": "alpha-ing.de",
            "website": "https://www.alpha-ing.de/kontakt",
            "strasse": "Hauptstr. 1",
            "plz": "80331",
            "ort": "München",
            "land": "DE",
            "telefon": "+49 89 123",
            "branche": "Ingenieurbüro",
            "mitarbeiter": "",
            "handelsregister": "Amtsgericht München HRB 12345",
            "anrede": "Herr",
            "vorname": "Max",
            "nachname": "Muster",
            "position": "Geschäftsführung",
            "email": "max.muster@alpha-ing.de",
            "email_typ": "persoenlich",
            "email_status": "Safe to Send",
            "kontakt_telefon": "",
            "linkedin_url": "https://www.linkedin.com/in/max-muster",
            "quelle": "Google-Maps-Suche nach „Ingenieurbüro“ in München; Kontaktdaten aus dem Impressum",
            "quelle_url": "https://www.alpha-ing.de/impressum",
            "erfasst_am": "2026-10-20",
            "personalisierung": "Ihr Brückenprojekt in Freising ist mir aufgefallen.",
            "video_titel": "Max, kurz zu Alpha",
        })

        self.assertEqual(beta["externe_id"], f"ds-{self.ds_ids[1]}")
        self.assertEqual(beta["domain"], "beta-planung.at")
        self.assertEqual(beta["telefon"], "+43 1 555")      # fallback phone_imported
        self.assertEqual(beta["position"], "")
        self.assertEqual(beta["email_typ"], "funktion")
        self.assertEqual(beta["quelle_url"], "")
        self.assertEqual(beta["strasse"], "")
        self.assertEqual(beta["handelsregister"], "")
        self.assertEqual(beta["linkedin_url"], "")
        self.assertEqual(beta["erfasst_am"], "2026-10-18")
        self.assertEqual(beta["quelle"], "Google-Maps-Suche nach „Planungsbüro“ in Wien")


class GestuftStub:
    """Subscription check as lizenz.Sperrabgleich answers it: blocked, warned or unknown."""

    quelle = "Server-Abgleich (Test), sperren ab Stufe 3, warnen ab Stufe 1"

    def __init__(self, sperren: dict[str, str], warnen: dict[str, str]):
        self.sperren, self.warnen = sperren, warnen

    def _erste(self, tabelle: dict[str, str], werte) -> str | None:
        return next((tabelle[w] for w in werte if w in tabelle), None)

    def treffer(self, *werte):
        return self._erste(self.sperren, werte)

    def warnung(self, *werte):
        return self._erste(self.warnen, werte)

    def __len__(self) -> int:
        return len(self.sperren) + len(self.warnen)


class SperrabgleichTest(ExportFixture):
    """Free plan vs. subscription check, notice column and the silent upload after the export."""

    def _bezeichnung(self, ergebnis: dict) -> str:
        return next(b for b in ergebnis if b.startswith("Gesperrt"))

    def test_free_plan_ohne_abgleich_mit_upload(self) -> None:
        self.sperre = None   # free plan: lizenz.sperrabgleich_laden returns None
        self.eigene = Blockliste({"beta-planung.at"}, set())
        ergebnis = self._export(lead_format=True)

        liste1 = _lies_csv(self._datei("1_zielgruppe_geschaeftsfuehrer_*.csv"))
        self.assertEqual([r["Firmenname"] for r in liste1], ["Alpha Ingenieure GmbH", "Gesperrt GmbH"],
                         "without a subscription nothing is checked against the server")
        self.assertEqual({r["Sperrliste Hinweis"] for r in liste1}, {""})
        gesperrt = _lies_csv(self._datei("5_gesperrt_sperrliste_*.csv"))
        self.assertEqual([(r["Firmenname"], r["Einstufung"]) for r in gesperrt],
                         [("Beta Planung", "Eigene Blockliste – bereits kontaktiert (beta-planung.at)")])
        self.assertEqual(self._bezeichnung(ergebnis),
                         "Gesperrt · eigene Blockliste, 1 Einträge; kein Sperrlisten-Abgleich (Free-Plan)")

        self.hochladen.assert_called_once()
        hochgeladen = self.hochladen.call_args.args[0]
        self.assertEqual(self.hochladen.call_args.kwargs, {"pfad": "google-maps", "bezeichnung": "testkampagne"})
        lead_format = json.loads(self._datei("leads_testkampagne_*.json").read_text(encoding="utf-8"))
        for lead in lead_format:   # lists 1 + 2, exactly as in the lead format
            self.assertIn(lead, hochgeladen)
        blockiert = next(l for l in hochgeladen if l["email"] == "info@beta-planung.at")
        self.assertEqual(blockiert["firma"], "Beta Planung OG")
        # the companies of list 4 (not checkable) are handed in too, with the same ids as their leads
        self.assertEqual({l["externe_id"] for l in hochgeladen if not l["email"]},
                         {"biz-alpha", "biz-gesperrt", f"ds-{self.ds_ids[1]}"})
        self.assertEqual([(m, pfad) for m, pfad, _ in self.server], [("POST", "/leads/hochladen")])

    def test_abo_sperrt_und_warnt(self) -> None:
        geladen = []
        self.sperre = GestuftStub(
            sperren={"chef@gesperrt.de": "Stufe 5 (abmahnung_anwalt), 2× gemeldet, zuletzt 2026-10-20, bestaetigt"},
            warnen={"http://beta-planung.at": "Stufe 1 (beschwerde), 1× gemeldet"})
        with mock.patch.object(export.sperrliste_mod, "laden",
                               side_effect=lambda werte=(), **k: geladen.append(list(werte)) or self.sperre):
            ergebnis = self._export()

        self.assertIn("chef@gesperrt.de", geladen[0])
        self.assertIn("https://www.alpha-ing.de/kontakt", geladen[0])
        liste1 = _lies_csv(self._datei("1_zielgruppe_geschaeftsfuehrer_*.csv"))
        liste2 = _lies_csv(self._datei("2_zielgruppe_info_*.csv"))
        self.assertEqual([(r["Firmenname"], r["Sperrliste Hinweis"]) for r in liste1], [("Alpha Ingenieure GmbH", "")])
        self.assertEqual([(r["Firmenname"], r["Sperrliste Hinweis"]) for r in liste2],
                         [("Beta Planung OG", "Stufe 1 (beschwerde), 1× gemeldet")])
        self.assertEqual(list(liste2[0])[-1], "Sperrliste Hinweis")

        gesperrt = _lies_csv(self._datei("5_gesperrt_sperrliste_*.csv"))
        self.assertEqual([(r["Firmenname"], r["Einstufung"]) for r in gesperrt], [
            ("Gesperrt", "Sperrliste: Stufe 5 (abmahnung_anwalt), 2× gemeldet, zuletzt 2026-10-20, bestaetigt")])
        self.assertEqual(self._bezeichnung(ergebnis),
                         f"Gesperrt · Sperrliste ({GestuftStub.quelle}); eigene Blockliste, 0 Einträge")

    def test_upload_nur_lead_felder(self) -> None:
        self._export()
        self.assertEqual(len(self.server), 1)
        _, pfad, body = self.server[0]
        self.assertEqual((pfad, body["pfad"], body["bezeichnung"]), ("/leads/hochladen", "google-maps", "testkampagne"))
        self.assertTrue(body["leads"])
        for lead in body["leads"]:
            self.assertLessEqual(set(lead), set(lizenz.LEAD_FELDER), lead)
            self.assertTrue(all(isinstance(v, str) and v for v in lead.values()), lead)
        alpha = next(l for l in body["leads"] if l.get("email") == "max.muster@alpha-ing.de")
        self.assertNotIn("personalisierung", alpha)
        self.assertNotIn("video_titel", alpha)
        self.assertEqual(alpha["handelsregister"], "Amtsgericht München HRB 12345")

    def test_upload_fehler_stoppt_export_nicht(self) -> None:
        with mock.patch.object(lizenz, "_aufruf", side_effect=lizenz.ServerFehler(0, "offline")):
            ergebnis = self._export()
        self.assertIn("Zielgruppe · Geschäftsführer-Adresse", ergebnis)


class QuelleTest(unittest.TestCase):
    """quelle_url / quelle: imprint URL first, Google Maps entry as fallback."""

    BASIS = {"place_id": "ChIJmaps", "query_keyword": "Statiker", "query_city": "Graz"}

    def test_mit_impressum_url(self) -> None:
        row = {**self.BASIS, "impressum_raw": json.dumps({"impressum_url": "https://statik.at/impressum"})}
        self.assertEqual(export.quelle_url(row), "https://statik.at/impressum")
        self.assertEqual(export.quelle(row),
                         "Google-Maps-Suche nach „Statiker“ in Graz; Kontaktdaten aus dem Impressum")
        self.assertEqual(export.lead_format_eintrag(row)["quelle_url"], "https://statik.at/impressum")

    def test_ohne_impressum_url(self) -> None:
        for raw in (None, "{}", json.dumps({"impressum_url": ""}), "kein json"):
            row = {**self.BASIS, "impressum_raw": raw}
            self.assertEqual(export.quelle_url(row), "https://www.google.com/maps/place/?q=place_id:ChIJmaps")
            self.assertEqual(export.quelle(row), "Google-Maps-Suche nach „Statiker“ in Graz")


class UpdatedAtTest(unittest.TestCase):
    """db.update stamps anreicherung.updated_at; erfasst_am follows it."""

    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        db.init(self.conn)
        ds = self.conn.execute("INSERT INTO datensaetze (business_id) VALUES ('biz-1')").lastrowid
        self.ds = ds
        self.an = self.conn.execute(
            "INSERT INTO anreicherung (datensatz_id, created_at, updated_at) "
            "VALUES (?, '2020-01-01 00:00:00', '2020-01-01 00:00:00')", (ds,)).lastrowid
        self.conn.commit()

    def tearDown(self) -> None:
        self.conn.close()

    def _row(self):
        return self.conn.execute("SELECT * FROM anreicherung WHERE id=?", (self.an,)).fetchone()

    def test_update_setzt_updated_at(self) -> None:
        heute = self.conn.execute("SELECT date('now')").fetchone()[0]
        self.assertEqual(export.erfasst_am(self._row()), "2020-01-01")
        db.update(self.conn, "anreicherung", self.an, {"telefon_impressum": "+49 1"})
        row = self._row()
        self.assertEqual(row["telefon_impressum"], "+49 1")
        self.assertEqual(row["created_at"], "2020-01-01 00:00:00")
        self.assertEqual(row["updated_at"][:10], heute)
        self.assertEqual(export.erfasst_am(row), heute)

    def test_explizites_updated_at_bleibt(self) -> None:
        db.update(self.conn, "anreicherung", self.an, {"updated_at": "2021-05-05 10:00:00"})
        self.assertEqual(self._row()["updated_at"], "2021-05-05 10:00:00")

    def test_andere_tabellen_unveraendert(self) -> None:
        # datensaetze has no updated_at column — update must still work
        db.update(self.conn, "datensaetze", self.ds, {"firmenname": "Neu"})
        name = self.conn.execute("SELECT firmenname FROM datensaetze WHERE id=?", (self.ds,)).fetchone()[0]
        self.assertEqual(name, "Neu")


if __name__ == "__main__":
    unittest.main()
