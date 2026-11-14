#!/usr/bin/env python3
"""Offline tests for sperrliste.py against a local fake server. Standard library only.

    cd abmahnung-werbemail-abwehr/scripts && python3 -m unittest test_sperrliste -v
"""
import contextlib
import csv
import io
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import lizenz  # noqa: E402
import sperrliste  # noqa: E402

SCHLUESSEL = "aks_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5"   # 30 characters after the prefix
MELDUNG_NR = "6f1c2d3e-4b5a-4c6d-8e7f-9a0b1c2d3e4f"


class FakeServer:
    """Answers like the licence server. typ decides the plan; every request is recorded."""

    def __init__(self):
        self.typ = "free"
        self.anfragen = []
        self.abgleich_antwort = None
        server = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):  # keep the test output clean
                pass

            def _antwort(self, status, daten):
                text = json.dumps(daten).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(text)))
                self.end_headers()
                self.wfile.write(text)

            def _bearbeiten(self, methode):
                laenge = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(laenge).decode("utf-8")) if laenge else None
                server.anfragen.append({"methode": methode, "pfad": self.path, "body": body,
                                        "auth": self.headers.get("Authorization")})
                if self.path == "/lizenz" and methode == "POST" and (body or {}).get("aktion") == "anlegen":
                    return self._antwort(200, {"ok": True, "schluessel": SCHLUESSEL, "typ": "free"})
                if self.headers.get("Authorization") != "Bearer " + SCHLUESSEL:
                    return self._antwort(401, {"fehler": "Schlüssel ungültig"})
                if self.path == "/lizenz" and methode == "GET":
                    return self._antwort(200, {"typ": server.typ, "features": [] if server.typ == "free"
                                               else ["sperrliste_abgleich"], "hinweise": []})
                if self.path == "/abmahnung/pruefen":
                    return self._antwort(200, {
                        "ok": True, "einreichung": "0b6e1f6a-3c2d-4e5f-8a9b-0c1d2e3f4a5b", "upload": None,
                        "titel": "So würden wir damit umgehen",
                        "schritte": [{"thema": "Unterlassung", "vorgehen": "Schnell: modifizierte UE."}],
                        "fristen": [{"frist": "Unterlassungserklärung", "datum": "20.11.2026"}],
                        "hinweis": sperrliste.KEINE_RECHTSBERATUNG, "kanzlei_echtheit": "unbekannt"})
                if self.path == "/meldung":
                    return self._antwort(201, {"ok": True, "meldung": MELDUNG_NR})
                if self.path == "/sperrliste/abgleich":
                    if server.typ == "free" or server.abgleich_antwort is None:
                        return self._antwort(402, {"fehler": lizenz.FREE_PLAN_TEXT})
                    return self._antwort(200, server.abgleich_antwort(body))
                return self._antwort(404, {"fehler": "Unbekannter Pfad"})

            def do_GET(self):
                self._bearbeiten("GET")

            def do_POST(self):
                self._bearbeiten("POST")

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def pfade(self):
        return [a["pfad"] for a in self.anfragen]

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()


class SperrlisteTest(unittest.TestCase):
    def setUp(self):
        self.fake = FakeServer()
        self.ordner = tempfile.mkdtemp(prefix="sperrliste-test-")
        self.env_alt = dict(os.environ)
        os.environ.pop("LIZENZ_SCHLUESSEL", None)
        os.environ.update({"ABMAHNSCHUTZ_API_URL": self.fake.url, "ABMAHNSCHUTZ_ORDNER": self.ordner,
                           "NO_PROXY": "127.0.0.1,localhost", "no_proxy": "127.0.0.1,localhost"})

    def tearDown(self):
        self.fake.stop()
        os.environ.clear()
        os.environ.update(self.env_alt)
        shutil.rmtree(self.ordner, ignore_errors=True)

    def lauf(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = sperrliste.main(list(argv))
        return code, out.getvalue()

    def datei(self, name, text):
        pfad = Path(self.ordner) / name
        pfad.write_text(text, encoding="utf-8")
        return str(pfad)

    def abmahnung(self, **extra):
        daten = {"lead": {"firma": "Muster Vertrieb GmbH", "domain": "muster-vertrieb.example"},
                 "abmahner": {"firma": "Beispiel Immobilien GmbH", "domains": ["beispiel-immobilien.example"]},
                 "kanzlei": {"name": "Kanzlei Exempel", "domain": "kanzlei-exempel.example"},
                 "fall": {"frist_ue": "2026-11-20"},
                 "forderungen": {"gegenstandswert": 6000, "art82_gefordert": True, "art82_betrag": 500}}
        daten.update(extra)
        return self.datei("abmahnung.json", json.dumps(daten))

    # ------------------------------------------------------------ key

    def test_schluessel_wird_automatisch_angelegt(self):
        code, out = self.lauf("check", "--datei", self.abmahnung())
        self.assertEqual(code, 0, out)
        datei = Path(self.ordner) / "lizenz"
        self.assertEqual(datei.read_text(encoding="utf-8").strip(), SCHLUESSEL)
        if os.name != "nt":
            self.assertEqual(datei.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.fake.anfragen[0]["body"], {"aktion": "anlegen", "bedingungen": lizenz.BEDINGUNGEN_VERSION})
        self.assertIsNone(self.fake.anfragen[0]["auth"])
        self.assertNotIn(SCHLUESSEL, out)

    # ------------------------------------------------------------ check

    def test_check_zeigt_umgang_und_hinweis(self):
        code, out = self.lauf("check", "--datei", self.abmahnung())
        self.assertEqual(code, 0, out)
        self.assertIn("So würden wir damit umgehen", out)
        self.assertTrue(out.rstrip().endswith(sperrliste.KEINE_RECHTSBERATUNG), out)
        titel = out.index("So würden wir damit umgehen")
        self.assertLess(out.index(sperrliste.KEINE_RECHTSBERATUNG, titel), out.index("1. ", titel), out)
        self.assertIn("Agentur Consulting", out)
        anfrage = [a for a in self.fake.anfragen if a["pfad"] == "/abmahnung/pruefen"][0]
        self.assertEqual(anfrage["auth"], "Bearer " + SCHLUESSEL)
        e = anfrage["body"]["abmahnung"]
        self.assertEqual(e["einwilligung"], {"dokumente": False, "kontakt": False})
        self.assertEqual(e["nutzungsbedingungen_version"], sperrliste.NUTZUNGSBEDINGUNGEN_VERSION)

    def test_check_json_enthaelt_hinweis(self):
        code, out = self.lauf("check", "--datei", self.abmahnung(), "--json")
        self.assertEqual(code, 0, out)
        self.assertTrue(json.loads(out)["hinweis"].startswith("Keine Rechtsberatung"))

    def test_check_json_bleibt_json_wenn_felder_entfernt_werden(self):
        pfad = self.abmahnung(lead={"firma": "Muster Vertrieb GmbH", "domain": "muster-vertrieb.example",
                                    "kontakt_name": "Erika Muster"})
        with contextlib.redirect_stderr(io.StringIO()) as err:
            code, out = self.lauf("check", "--datei", pfad, "--json")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out)["titel"], "So würden wir damit umgehen")
        self.assertIn("lead.kontakt_name", err.getvalue())

    def test_check_sendet_nur_felder_des_formats(self):
        pfad = self.abmahnung(notizen="intern", lead={"firma": "Muster Vertrieb GmbH", "domain": "muster-vertrieb.example",
                                                      "kontakt_name": "Erika Muster", "lieblingsfarbe": "blau"})
        code, out = self.lauf("check", "--datei", pfad)
        self.assertEqual(code, 0, out)
        e = [a for a in self.fake.anfragen if a["pfad"] == "/abmahnung/pruefen"][0]["body"]["abmahnung"]
        self.assertNotIn("notizen", e)
        self.assertNotIn("kontakt_name", e["lead"])   # no consent to be contacted
        self.assertNotIn("lieblingsfarbe", e["lead"])

    def test_check_dry_run_und_pflichtfelder(self):
        code, out = self.lauf("check", "--datei", self.abmahnung(), "--dry-run")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.fake.anfragen, [])
        code, out = self.lauf("check", "--datei", self.datei("leer.json", json.dumps({"lead": {}})))
        self.assertEqual(code, 2)
        self.assertIn("lead.firma fehlt", out)
        self.assertEqual(self.fake.anfragen, [])

    # ------------------------------------------------------------ melden

    def test_melden_sendet_erwartete_nutzlast(self):
        code, out = self.lauf("melden", "--domains", "https://www.beispiel-immobilien.example/kontakt",
                              "beispiel-immo.example", "--kanzlei-domain", "kanzlei-exempel.example",
                              "--monat", "2026-09", "--forderung", "1000-2000", "--art82", "ja",
                              "--vorgehen", "ue_modifiziert,ART82_ABGELEHNT", "--melder-domain", "muster-vertrieb.example")
        self.assertEqual(code, 0, out)
        self.assertIn(MELDUNG_NR, out)
        anfrage = [a for a in self.fake.anfragen if a["pfad"] == "/meldung"][0]
        self.assertEqual(anfrage["auth"], "Bearer " + SCHLUESSEL)
        self.assertEqual(anfrage["body"], {
            "domains": ["beispiel-immobilien.example", "beispiel-immo.example"], "stufe": 5, "monat": "2026-09",
            "melder_domain": "muster-vertrieb.example", "forderung": "1000-2000", "art82": True, "ausgang": "offen",
            "vorgehen": ["UE_MODIFIZIERT", "ART82_ABGELEHNT"], "beleg_art": "abmahnschreiben",
            "kanzlei_domain": "kanzlei-exempel.example", "quelle": "abmahnungs_check"})
        self.assertNotIn(SCHLUESSEL, out)

    def test_melden_ohne_kanzlei_stufe_4_und_dry_run(self):
        code, out = self.lauf("melden", "--domains", "beispiel-immobilien.example", "--monat", "2026-09",
                              "--art82", "nein", "--melder-domain", "muster-vertrieb.example", "--dry-run")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.fake.anfragen, [])
        nutzlast = json.loads(out.split("Nutzlast:\n", 1)[1])
        self.assertEqual(nutzlast["stufe"], 4)
        self.assertEqual(nutzlast["quelle"], "abmahnungs_check")

    def test_melden_prueft_lokal(self):
        code, out = self.lauf("melden", "--domains", "gmail.com", "info@abmahner.example", "--monat", "26-09",
                              "--art82", "ja", "--melder-domain", "muster-vertrieb.example")
        self.assertEqual(code, 2)
        self.assertIn("geschützt", out)
        self.assertIn("E-Mail-Adresse", out)
        self.assertIn("--monat", out)
        self.assertEqual(self.fake.anfragen, [])

    def test_melden_server_nicht_erreichbar(self):
        os.environ["ABMAHNSCHUTZ_API_URL"] = "http://127.0.0.1:9"
        os.environ["LIZENZ_SCHLUESSEL"] = SCHLUESSEL
        code, out = self.lauf("melden", "--domains", "beispiel-immobilien.example", "--monat", "2026-09",
                              "--art82", "ja", "--melder-domain", "muster-vertrieb.example")
        self.assertEqual(code, 4)
        self.assertIn("später erneut", out)
        self.assertNotIn("github", out.lower())

    # ------------------------------------------------------------ free plan

    def test_pruefen_im_free_plan(self):
        code, out = self.lauf("pruefen", "--domain", "beispiel-immobilien.example")
        self.assertEqual(code, 5)
        self.assertIn(lizenz.FREE_PLAN_TEXT, out)
        self.assertIn("check", out)
        self.assertNotIn("/sperrliste/abgleich", self.fake.pfade())

    def test_abgleich_im_free_plan_sendet_keine_kontakte(self):
        kontakte = self.datei("kontakte.csv", "firma,email\nA GmbH,info@a.example\n")
        code, out = self.lauf("abgleich", "--kontakte", kontakte)
        self.assertEqual(code, 5)
        self.assertIn(lizenz.FREE_PLAN_TEXT, out)
        self.assertNotIn("/sperrliste/abgleich", self.fake.pfade())
        self.assertFalse((Path(self.ordner) / "kontakte_gesperrt.csv").exists())
        self.assertFalse((Path(self.ordner) / "kontakte_bereinigt.csv").exists())

    def test_abgleich_server_antwortet_402(self):
        self.fake.typ = "abo"   # licence info says subscription, the server still refuses (e.g. just expired)
        kontakte = self.datei("kontakte.csv", "firma,email\nA GmbH,info@a.example\n")
        code, out = self.lauf("abgleich", "--kontakte", kontakte)
        self.assertEqual(code, 5)
        self.assertIn(lizenz.FREE_PLAN_TEXT, out)
        code, out = self.lauf("pruefen", "--domain", "a.example")
        self.assertEqual(code, 5)
        self.assertIn(lizenz.FREE_PLAN_TEXT, out)

    # ------------------------------------------------------------ subscription

    def test_abgleich_mit_abo_schreibt_beide_listen(self):
        self.fake.typ = "abo"

        def antwort(body):
            ergebnisse = []
            for nr, e in enumerate(body["eintraege"], 1):
                wert = e.get("email") or e.get("domain")
                if wert.endswith("@abmahner.example"):
                    ergebnisse.append({"nr": nr, "stufe": 5, "empfehlung": "sperren"})
                elif wert.endswith("@widerspruch.example"):
                    ergebnisse.append({"nr": nr, "stufe": 2, "empfehlung": "warnen"})
                else:
                    ergebnisse.append({"nr": nr, "empfehlung": "frei"})
            return {"ok": True, "ergebnisse": ergebnisse}

        self.fake.abgleich_antwort = antwort
        kontakte = self.datei("kontakte.csv", "firma;email\nAbmahner AG;info@abmahner.example\n"
                                              "W GmbH;office@widerspruch.example\nFrei KG;hallo@frei.example\n")
        code, out = self.lauf("abgleich", "--kontakte", kontakte)
        self.assertEqual(code, 0, out)
        with open(Path(self.ordner) / "kontakte_gesperrt.csv", encoding="utf-8") as f:
            gesperrt = list(csv.DictReader(f, delimiter=";"))
        with open(Path(self.ordner) / "kontakte_bereinigt.csv", encoding="utf-8") as f:
            frei = list(csv.DictReader(f, delimiter=";"))
        self.assertEqual([z["email"] for z in gesperrt], ["info@abmahner.example"])
        self.assertIn("Stufe 5 (Abmahnung über eine Kanzlei)", gesperrt[0]["Sperrgrund"])
        self.assertEqual([z["email"] for z in frei], ["office@widerspruch.example", "hallo@frei.example"])
        self.assertIn("Stufe 2", frei[0]["Sperrliste Hinweis"])
        self.assertEqual(frei[1]["Sperrliste Hinweis"], "")
        body = [a for a in self.fake.anfragen if a["pfad"] == "/sperrliste/abgleich"][0]["body"]
        self.assertEqual(len(body["eintraege"]), 3)
        self.assertNotIn("/leads/hochladen", self.fake.pfade())   # contacts are never handed in
        self.assertEqual(sorted(p.name for p in Path(self.ordner).glob("*.csv")),
                         ["kontakte.csv", "kontakte_bereinigt.csv", "kontakte_gesperrt.csv"])

    def test_pruefen_mit_abo(self):
        self.fake.typ = "abo"
        self.fake.abgleich_antwort = lambda body: {"ok": True, "ergebnisse": [
            {"nr": 1, "stufe": 5, "empfehlung": "sperren"},
            {"nr": 2, "empfehlung": "frei"}]}
        code, out = self.lauf("pruefen", "--domain", "beispiel-immobilien.example", "neu.example", "--json")
        self.assertEqual(code, 0, out)
        r = json.loads(out)["domains"]
        self.assertTrue(r["beispiel-immobilien.example"]["bekannt"])
        self.assertEqual(r["beispiel-immobilien.example"]["stufe"], 5)
        self.assertEqual(set(r["beispiel-immobilien.example"]), {"bekannt", "empfehlung", "beschreibung", "stufe"})
        self.assertFalse(r["neu.example"]["bekannt"])

    # ------------------------------------------------------------ copies

    @unittest.skipUnless((HIER.parent.parent / "lead-scraper" / "werkzeuge" / "lizenz.py").exists(),
                         "lead-scraper not present (skill ZIP alone)")
    def test_lizenz_kopien_identisch(self):
        self.assertEqual((HIER / "lizenz.py").read_bytes(),
                         (HIER.parent.parent / "lead-scraper" / "werkzeuge" / "lizenz.py").read_bytes())


if __name__ == "__main__":
    unittest.main()
