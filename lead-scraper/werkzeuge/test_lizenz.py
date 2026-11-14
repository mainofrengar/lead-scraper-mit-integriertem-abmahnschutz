"""Offline tests for werkzeuge/lizenz.py and werkzeuge/sperrliste_abgleich.py against a local fake server.

    cd lead-scraper/werkzeuge && python3 -m unittest test_lizenz -v

No call leaves the machine: the API URL points to a fake server on 127.0.0.1, the key folder is a temp dir.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import tempfile
import threading
import time
import unittest
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

HIER = Path(__file__).resolve().parent
TMP = tempfile.mkdtemp(prefix="lizenz-test-")
os.environ["ABMAHNSCHUTZ_ORDNER"] = str(Path(TMP) / "konfig")
os.environ.pop("LIZENZ_SCHLUESSEL", None)
sys.path.insert(0, str(HIER))

import lizenz  # noqa: E402
import sperrliste_abgleich  # noqa: E402

SCHLUESSEL = "aks_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4"


class Fake:
    """State of the fake server: answers per path, recorded requests."""
    typ = "free"
    fehler: int | None = None   # e.g. 503: every request is answered with this status
    anfragen: list[tuple[str, str, dict, dict]] = []


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # noqa: D401, ARG002
        pass

    def _antwort(self, status: int, daten: dict):
        text = json.dumps(daten).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(text)))
        self.end_headers()
        self.wfile.write(text)

    def _body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):  # noqa: N802
        Fake.anfragen.append(("GET", self.path, {}, dict(self.headers)))
        if Fake.fehler:
            return self._antwort(Fake.fehler, {"ok": False, "fehler": "Wartung"})
        pro = Fake.typ != "free"
        self._antwort(200, {"ok": True, "typ": Fake.typ,
                            "features": ["sperrliste_abgleich", "support_paket", "instantly_sync"] if pro else [],
                            "hinweise": [] if pro else [{"code": "pro_vorteile", "titel": "Mehr Schutz",
                                                         "text": "Mit dem Abo …",
                                                         "optionen": ["abo_ansehen", "kostenfrei_reicht"]}]})

    def do_POST(self):  # noqa: N802
        body = self._body()
        Fake.anfragen.append(("POST", self.path, body, dict(self.headers)))
        if Fake.fehler:
            return self._antwort(Fake.fehler, {"ok": False, "fehler": "Wartung"})
        if self.path == "/lizenz" and body.get("aktion") == "anlegen":
            return self._antwort(201, {"ok": True, "schluessel": SCHLUESSEL, "typ": "free"})
        if self.path == "/sperrliste/abgleich":
            if Fake.typ == "free":
                return self._antwort(402, {"ok": False, "fehler": lizenz.FREE_PLAN_TEXT})
            erg = []
            for i, e in enumerate(body["eintraege"], 1):
                w = e.get("domain") or e.get("email")
                if w in ("abmahner.de", "chef@abmahner.de"):
                    erg.append({"nr": i, "stufe": 5, "empfehlung": "sperren"})
                elif w == "nervig.de":
                    erg.append({"nr": i, "stufe": 1, "empfehlung": "warnen"})
                else:
                    erg.append({"nr": i, "empfehlung": "frei"})
            return self._antwort(200, {"ok": True, "ergebnisse": erg})
        if self.path == "/leads/hochladen":
            return self._antwort(200, {"ok": True})
        return self._antwort(404, {"ok": False, "fehler": "unbekannt"})


SERVER = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=SERVER.serve_forever, daemon=True).start()
os.environ["ABMAHNSCHUTZ_API_URL"] = f"http://127.0.0.1:{SERVER.server_address[1]}"


def _neu(typ: str = "free"):
    Fake.typ = typ
    Fake.fehler = None
    Fake.anfragen = []
    for name in ("lizenz", "lizenz_cache.json"):
        (Path(os.environ["ABMAHNSCHUTZ_ORDNER"]) / name).unlink(missing_ok=True)


class Schluessel(unittest.TestCase):
    def setUp(self):
        _neu()

    def test_wird_angelegt_und_privat_gespeichert(self):
        self.assertEqual(lizenz.schluessel(), SCHLUESSEL)
        datei = Path(os.environ["ABMAHNSCHUTZ_ORDNER"]) / "lizenz"
        self.assertEqual(datei.read_text().strip(), SCHLUESSEL)
        if os.name != "nt":
            self.assertEqual(datei.stat().st_mode & 0o777, 0o600)
        self.assertEqual(lizenz.schluessel(), SCHLUESSEL)
        self.assertEqual(sum(1 for a in Fake.anfragen if a[2].get("aktion") == "anlegen"), 1, "nur einmal angelegt")

    def test_bedingungen_beim_anlegen(self):
        import io
        fehlerausgabe = io.StringIO()
        with mock.patch.object(sys, "stderr", fehlerausgabe):
            lizenz.schluessel()
            lizenz.schluessel()
        anlegen = [a for a in Fake.anfragen if a[2].get("aktion") == "anlegen"]
        self.assertEqual(anlegen[0][2].get("bedingungen"), lizenz.BEDINGUNGEN_VERSION, "Version geht an den Server")
        text = fehlerausgabe.getvalue()
        self.assertEqual(text.count("Nutzungsbedingungen (Version"), 1, "Zeile nur beim Anlegen")
        self.assertIn("DATENSCHUTZ.md", text)
        for datei in lizenz.rechtstexte():
            self.assertTrue(datei.exists(), f"{datei} liegt neben dem Paket")

    def test_umgebung_hat_vorrang(self):
        with mock.patch.dict(os.environ, {"LIZENZ_SCHLUESSEL": "aks_partner_schluessel_xyz1234567"}):
            self.assertEqual(lizenz.schluessel(), "aks_partner_schluessel_xyz1234567")
        self.assertFalse(Fake.anfragen)

    def test_bearer_und_cache(self):
        lizenz.auskunft(frisch=True)
        lizenz.auskunft()
        gets = [a for a in Fake.anfragen if a[0] == "GET"]
        self.assertEqual(len(gets), 1, "zweite Auskunft aus dem Cache")
        self.assertEqual(gets[0][3].get("Authorization"), "Bearer " + SCHLUESSEL)
        self.assertFalse(lizenz.hat_feature("sperrliste_abgleich"))
        self.assertTrue(any("kostenfrei_reicht" in z for z in lizenz.hinweise_text()))


class Abgleich(unittest.TestCase):
    def test_free_plan_kein_abgleich(self):
        _neu("free")
        self.assertIsNone(lizenz.sperrabgleich_laden(["chef@abmahner.de"]))
        self.assertFalse([a for a in Fake.anfragen if a[1] == "/sperrliste/abgleich"])

    def test_abo_stufen_und_schwellen(self):
        _neu("abo")
        with mock.patch.dict(os.environ, {"SPERREN_AB": "4", "WARNEN_AB": "1"}):
            s = lizenz.sperrabgleich_laden(["chef@abmahner.de", "https://www.nervig.de/kontakt", "frei.de", "frei.de"])
        anfrage = next(a for a in Fake.anfragen if a[1] == "/sperrliste/abgleich")[2]
        self.assertEqual((anfrage["sperren_ab"], anfrage["warnen_ab"]), (4, 1))
        self.assertEqual(len(anfrage["eintraege"]), 3, "doppelte Werte nur einmal")
        self.assertIn({"domain": "nervig.de"}, anfrage["eintraege"])
        self.assertEqual(s.treffer("x@y.de", "chef@abmahner.de"), "Stufe 5 (Abmahnung über eine Kanzlei)")
        self.assertIsNone(s.treffer("nervig.de"))
        self.assertIn("Stufe 1", s.warnung("www.nervig.de"))
        self.assertIsNone(s.treffer("frei.de"))

    def test_abo_ohne_server_bricht_ab(self):
        _neu("abo")
        lizenz.auskunft(frisch=True)
        with mock.patch.dict(os.environ, {"ABMAHNSCHUTZ_API_URL": "http://127.0.0.1:9"}):
            with self.assertRaises(SystemExit):
                lizenz.sperrabgleich_laden(["a.de"], pflicht=True)
            self.assertIsNone(lizenz.sperrabgleich_laden(["a.de"], pflicht=False))


class AbgleichFailClosed(unittest.TestCase):
    """Without a reachable server the licence type decides; unknown counts as subscription. ist_pro is not mocked."""

    OFFLINE = {"ABMAHNSCHUTZ_API_URL": "http://127.0.0.1:9"}

    def _stand(self, typ: str | None, alter_sekunden: float = 0):
        _neu(typ or "abo")
        konfig = Path(os.environ["ABMAHNSCHUTZ_ORDNER"])
        konfig.mkdir(parents=True, exist_ok=True)
        (konfig / "lizenz").write_text(SCHLUESSEL + "\n", encoding="utf-8")
        if typ:
            (konfig / "lizenz_cache.json").write_text(json.dumps(
                {"typ": typ, "features": [], "_geladen": time.time() - alter_sekunden}), encoding="utf-8")

    def _bricht_ab(self, text: str = "Lizenzstatus"):
        with self.assertRaises(SystemExit) as ende:
            lizenz.sperrabgleich_laden(["a.de"], pflicht=True)
        self.assertIn(text, str(ende.exception))
        self.assertIn("Ohne Abgleich wird nicht exportiert", str(ende.exception))
        self.assertIsNone(lizenz.sperrabgleich_laden(["a.de"], pflicht=False))

    def test_a_ohne_cache_offline(self):
        self._stand(None)
        with mock.patch.dict(os.environ, self.OFFLINE):
            self._bricht_ab()

    def test_b_cache_aelter_als_eine_stunde_und_server_503(self):
        self._stand("abo", 2 * 3600)
        Fake.fehler = 503
        self.assertEqual(lizenz.auskunft().get("typ"), "abo", "5xx: Cache bis drei Tage")
        self._bricht_ab("Sperrlisten-Abgleich ist nicht möglich")
        self.assertTrue([a for a in Fake.anfragen if a[1] == "/sperrliste/abgleich"])

    def test_b_ohne_cache_server_503(self):
        self._stand(None)
        Fake.fehler = 503
        self._bricht_ab()

    def test_c_cache_aelter_als_drei_tage_offline(self):
        self._stand("abo", 4 * 86400)
        with mock.patch.dict(os.environ, self.OFFLINE):
            self._bricht_ab()

    def test_free_im_cache_offline(self):
        self._stand("free", 4 * 86400)
        with mock.patch.dict(os.environ, self.OFFLINE):
            self.assertIsNone(lizenz.sperrabgleich_laden(["a.de"], pflicht=True))

    def test_abo_im_cache_offline_abgleich_bricht_ab(self):
        self._stand("abo", 2 * 3600)
        with mock.patch.dict(os.environ, self.OFFLINE):
            self.assertEqual(lizenz.auskunft().get("typ"), "abo")
            self._bricht_ab("Sperrlisten-Abgleich ist nicht möglich")


class Hochladen(unittest.TestCase):
    def test_nur_lead_felder_und_nie_fehler(self):
        _neu()
        ok = lizenz.leads_hochladen([{"firma": "A GmbH", "email": "a@a.de", "_intern": "x", "personalisierung": "p"},
                                     {"firma": ""}], pfad="test", bezeichnung="t")
        self.assertTrue(ok)
        body = next(a for a in Fake.anfragen if a[1] == "/leads/hochladen")[2]
        self.assertEqual(body["leads"], [{"firma": "A GmbH", "email": "a@a.de"}])
        with mock.patch.dict(os.environ, {"ABMAHNSCHUTZ_API_URL": "http://127.0.0.1:9"}):
            self.assertFalse(lizenz.leads_hochladen([{"firma": "B"}], pfad="test"))


class SupportPaket(unittest.TestCase):
    def test_keine_geheimnisse_und_keine_leads(self):
        _neu("abo")
        wurzel = Path(tempfile.mkdtemp(dir=TMP))
        (wurzel / "CHANGELOG.md").write_text("# x\n\n## 2026-11-03\n", encoding="utf-8")
        pfad = wurzel / "pfade" / "google-maps"
        (pfad / "data").mkdir(parents=True)
        (pfad / "exports").mkdir()
        (pfad / ".env").write_text(
            "OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz123456\nSKAEL_API_KEY=eak_geheim1234567890\n"
            "MAX_CONCURRENCY=4\nLIZENZ_SCHLUESSEL=aks_abcdefghijklmnopqrstuvwx\nABSENDER=max@firma.de\n"
            "SPERRLISTE_PFLICHT=true\nLEER=\n", encoding="utf-8")
        (pfad / "data" / "leads.db").write_text("geheime leads", encoding="utf-8")
        (pfad / "exports" / "1_zielgruppe.csv").write_text("Firma;E-Mail\nA;a@a.de\n", encoding="utf-8")
        (pfad / "README.md").write_text("Kontakt: chef@kunde.de, Token AbCdEf1234567890GhIjKl1234\n", encoding="utf-8")
        datei = lizenz.support_paket(wurzel, Path(TMP) / "ziel", "Export bricht ab, Kontakt max@firma.de")
        with zipfile.ZipFile(datei) as z:
            namen = z.namelist()
            inhalt = "\n".join(z.read(n).decode() for n in namen)
        self.assertEqual(sorted(namen), ["beschreibung.txt", "dateien.txt", "einstellungen.txt", "system.txt"])
        for verboten in ("sk-proj", "eak_geheim", "aks_abcdef", SCHLUESSEL, "max@firma.de", "chef@kunde.de",
                         "geheime leads", "leads.db", "1_zielgruppe", "a@a.de", "AbCdEf1234567890"):
            self.assertNotIn(verboten, inhalt, verboten)
        self.assertIn("OPENAI_API_KEY = (gesetzt)", inhalt)
        self.assertIn("MAX_CONCURRENCY = 4", inhalt)
        self.assertIn("SPERRLISTE_PFLICHT = true", inhalt)
        self.assertIn("ABSENDER = (gesetzt)", inhalt)
        self.assertIn("Stand laut CHANGELOG: 2026-11-03", inhalt)
        self.assertIn("aks_", inhalt.split("Lizenz: ")[1][:20], "nur der Präfix des Schlüssels")

    def _support(self, typ: str, **kw) -> tuple[int, str]:
        _neu(typ)
        args = mock.Mock(beschreibung=kw.get("beschreibung", ""), ziel=str(Path(TMP) / f"ziel-{typ}"),
                         thema=kw.get("thema"), anliegen=kw.get("anliegen"), ohne_browser=True)
        with mock.patch("builtins.print") as p:
            code = lizenz.cmd_support(args, Path(tempfile.mkdtemp(dir=TMP)))
        return code, "\n".join(str(c.args[0]) if c.args else "" for c in p.call_args_list)

    def test_free_plan_paket_mit_abo_hinweis(self):
        code, text = self._support("free", thema="export_sperrliste", anliegen="fehler",
                                   beschreibung="Export bricht ab, Kontakt max@firma.de")
        self.assertEqual(code, 0)
        self.assertLess(text.index("Premium-Support"), text.index("Support-Paket erstellt"), "Hinweis zuerst")
        self.assertIn("abo", text)
        self.assertTrue(list((Path(TMP) / "ziel-free").glob("support-paket_*.zip")))

    def test_formularangaben_geordnet(self):
        code, text = self._support("abo", thema="scraper_google_maps", anliegen="fehler",
                                   beschreibung="Export bricht ab, Kontakt max@firma.de")
        self.assertEqual(code, 0)
        self.assertNotIn("Premium-Support", text)
        reihenfolge = [text.index(f"  {n}. ") for n in range(1, 8)]
        self.assertEqual(reihenfolge, sorted(reihenfolge))
        self.assertIn(lizenz.SUPPORT_URL, text)
        self.assertIn("Lead-Scraper: Google Maps", text)
        self.assertIn("Fehlermeldung oder Abbruch", text)
        self.assertIn(SCHLUESSEL[:12], text)
        self.assertNotIn(SCHLUESSEL, text, "nie der ganze Schlüssel")
        self.assertNotIn("max@firma.de", text, "E-Mail-Adressen werden entfernt")

    def test_rechnungsfrage_ohne_paket_und_ohne_hinweis(self):
        code, text = self._support("free", thema="abo_rechnung", anliegen="rechnung")
        self.assertEqual(code, 0)
        self.assertNotIn("Premium-Support", text)
        self.assertIn("nicht nötig", text)


class Verbindung(unittest.TestCase):
    def test_ipv4_zuerst(self):
        versucht = []

        class Sock:
            def __init__(self, familie, *_):
                self.familie = familie

            def settimeout(self, _):
                pass

            def connect(self, ziel):
                versucht.append(self.familie)
                if self.familie == lizenz.socket.AF_INET6:
                    raise OSError("kein IPv6")

            def close(self):
                pass

        infos = [(lizenz.socket.AF_INET6, 1, 6, "", ("2a01::2", 443, 0, 0)),
                 (lizenz.socket.AF_INET, 1, 6, "", ("203.0.113.10", 443))]
        with mock.patch.object(lizenz.socket, "getaddrinfo", return_value=infos), \
             mock.patch.object(lizenz.socket, "socket", Sock):
            s = lizenz._verbinden(("leads-db.example", 443), 30)
        self.assertEqual(s.familie, lizenz.socket.AF_INET)
        self.assertEqual(versucht, [lizenz.socket.AF_INET])


class Werkzeug(unittest.TestCase):
    def _liste(self) -> Path:
        d = Path(tempfile.mkdtemp(dir=TMP))
        datei = d / "amazon.csv"
        with datei.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Firmenname", "E-Mail", "Website", "Amazon Storefront"])
            w.writerow(["Abmahner GmbH", "chef@abmahner.de", "", "https://amazon.de/sp?abmahner"])
            w.writerow(["Nervig AG", "", "https://nervig.de", ""])
            w.writerow(["Frei KG", "info@frei.de", "frei.de", ""])
        return datei

    def test_free_plan_nur_hinweis_aber_upload(self):
        _neu("free")
        datei = self._liste()
        with mock.patch("builtins.print") as p:
            sperrliste_abgleich.main([str(datei)])
        self.assertIn(lizenz.FREE_PLAN_TEXT, " ".join(str(c.args[0]) for c in p.call_args_list))
        self.assertFalse(list(datei.parent.glob("*_gesperrt.csv")))
        body = next(a for a in Fake.anfragen if a[1] == "/leads/hochladen")[2]
        self.assertEqual([l["firma"] for l in body["leads"]], ["Abmahner GmbH", "Nervig AG", "Frei KG"])
        self.assertEqual(body["leads"][1]["domain"], "nervig.de")
        self.assertEqual(body["pfad"], "amazon")

    def test_abo_listen(self):
        _neu("abo")
        datei = self._liste()
        with mock.patch("builtins.print"):
            sperrliste_abgleich.main([str(datei)])
        basis = str(datei)[:-4]
        with open(basis + "_gesperrt.csv", encoding="utf-8-sig") as f:
            gesperrt = list(csv.DictReader(f, delimiter=";"))
        with open(basis + "_bereinigt.csv", encoding="utf-8-sig") as f:
            frei = list(csv.DictReader(f, delimiter=";"))
        self.assertEqual([z["Firmenname"] for z in gesperrt], ["Abmahner GmbH"])
        self.assertTrue(gesperrt[0]["Sperrgrund"].startswith("Sperrliste: Stufe 5"))
        self.assertEqual([z["Firmenname"] for z in frei], ["Nervig AG", "Frei KG"])
        self.assertIn("Stufe 1", frei[0]["Sperrliste Hinweis"])
        self.assertEqual(frei[1]["Sperrliste Hinweis"], "")


if __name__ == "__main__":
    unittest.main()
