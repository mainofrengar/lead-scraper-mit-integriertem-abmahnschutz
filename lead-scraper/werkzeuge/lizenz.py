#!/usr/bin/env python3
"""Lizenz und Server-Dienste von Akquise & Abmahnschutz. Nur Python-Standardbibliothek.

Jede Installation hat einen Lizenzschlüssel. Beim ersten Aufruf wird automatisch ein kostenloser Schlüssel
(Free-Plan) angelegt und im Benutzerordner gespeichert, für alle Pfade und den Skill gemeinsam:

    macOS/Linux:  ~/.config/akquise-und-abmahnschutz/lizenz
    Windows:      %APPDATA%\\akquise-und-abmahnschutz\\lizenz

LIZENZ_SCHLUESSEL in der Umgebung oder in der .env eines Pfads hat Vorrang (z. B. für Partner-Schlüssel).
Auf dem Server liegt nur ein Hash des Schlüssels.

Was der Server kostenlos macht und was nur mit Abo (Stand siehe wissen/09_sperrliste.md):
  * Free:  Abmahnungs-Check, Meldungen, Adresssperren, Pro-Hinweise.
  * Abo:   Sperrlisten-Abgleich mit Stufen, Abmahner-Frühwarnung, Premium-Support, Instantly-Anbindung.
  * Immer: Nach jedem Export werden die exportierten Leads (Firmen und Ansprechpartner) an den Server
           übertragen, auch im Free-Plan. Das steht in den Nutzungsbedingungen (Klausel „Datenweitergabe im
           Free-Plan“) und in der Datenschutzerklärung.

Befehle (auch über `scraper …` bzw. `ecom …`):
    python3 werkzeuge/lizenz.py status
    python3 werkzeuge/lizenz.py abo                       Checkout (Free) bzw. Kundenportal (Abo) im Browser
    python3 werkzeuge/lizenz.py hinweis CODE kostenfrei_reicht
    python3 werkzeuge/lizenz.py instantly verbinden [--ab-stufe 3]
    python3 werkzeuge/lizenz.py instantly trennen
    python3 werkzeuge/lizenz.py support [--thema …] [--anliegen …] [--beschreibung "…"]
                                                          Support-Paket und Angaben für ak.consulting/support

Diese Datei gibt es zweimal, identisch: lead-scraper/werkzeuge/lizenz.py und
abmahnung-werbemail-abwehr/scripts/lizenz.py (Test: werkzeuge/test_lizenz.py).
"""
from __future__ import annotations

import argparse
import getpass
import http.client
import json
import os
import platform
import re
import socket
import sys
import tempfile
import time
import urllib.error
import urllib.request
import webbrowser
import zipfile
from datetime import datetime
from pathlib import Path

API_URL = "https://leads-db.akconsulting.cloud/functions/v1"
SUPPORT_EMAIL = "support@ak.consulting"
SUPPORT_URL = "https://ak.consulting/support"
FREE_PLAN_TEXT = "Kostenpflichtige Features können im Free-Plan nicht verwendet werden"
VERSION = "2026-11-10"
BEDINGUNGEN_VERSION = "2026-11"   # version of NUTZUNGSBEDINGUNGEN.md and DATENSCHUTZ.md, stored with a new key
CACHE_SEKUNDEN = 3600          # licence info is reloaded after one hour
CACHE_OFFLINE_TAGE = 3         # without connection the last info counts for three days
JE_AUFRUF = 2000               # entries per request (server limit)
SCHLUESSEL_MUSTER = re.compile(r"^aks_[A-Za-z0-9_-]{20,}$")
PRO_TYPEN = ("abo", "partner", "intern")

# lead fields the server accepts (leadpool), see datenbank/migrationen/0004_leads_einreichen.sql
LEAD_FELDER = ("externe_id", "firma", "rechtsform", "domain", "website", "strasse", "plz", "ort", "land", "telefon",
               "branche", "mitarbeiter", "handelsregister", "anrede", "vorname", "nachname", "position", "email",
               "email_typ", "email_status", "kontakt_telefon", "linkedin_url", "quelle", "quelle_url", "erfasst_am")


class ServerFehler(Exception):
    """Answer of the server with an error (status 0 = not reachable)."""

    def __init__(self, status: int, text: str):
        super().__init__(text)
        self.status = status
        self.text = text


# ---------------------------------------------------------------- key and cache

def ordner() -> Path:
    eigen = os.environ.get("ABMAHNSCHUTZ_ORDNER")
    if eigen:
        return Path(eigen)
    if os.name == "nt" and os.environ.get("APPDATA"):
        return Path(os.environ["APPDATA"]) / "akquise-und-abmahnschutz"
    return Path.home() / ".config" / "akquise-und-abmahnschutz"


def _api_url() -> str:
    return (os.environ.get("ABMAHNSCHUTZ_API_URL") or API_URL).rstrip("/")


def _schreibe_privat(pfad: Path, text: str) -> None:
    """Writes a file only the user can read (mode 600), atomically."""
    pfad.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(pfad.parent, 0o700)
    except OSError:
        pass
    fd, tmp = tempfile.mkstemp(dir=pfad.parent, prefix=".tmp-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.chmod(tmp, 0o600)
        os.replace(tmp, pfad)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def schluessel(*, anlegen: bool = True) -> str | None:
    """The licence key: LIZENZ_SCHLUESSEL, else the file in the user folder, else a new free key."""
    wert = (os.environ.get("LIZENZ_SCHLUESSEL") or "").strip()
    if wert:
        return wert
    datei = ordner() / "lizenz"
    if datei.exists():
        wert = datei.read_text(encoding="utf-8").strip()
        if SCHLUESSEL_MUSTER.match(wert):
            return wert
    if not anlegen:
        return None
    r = _aufruf("POST", "/lizenz", {"aktion": "anlegen", "bedingungen": BEDINGUNGEN_VERSION}, mit_schluessel=False)
    wert = str(r.get("schluessel") or "")
    if not SCHLUESSEL_MUSTER.match(wert):
        raise ServerFehler(500, "Der Server hat keinen gültigen Schlüssel geliefert")
    _schreibe_privat(datei, wert + "\n")
    print(bedingungen_text(), file=sys.stderr)
    return wert


def rechtstexte() -> tuple[Path, Path]:
    """NUTZUNGSBEDINGUNGEN.md and DATENSCHUTZ.md next to this package (lead-scraper/ or the skill folder)."""
    basis = Path(__file__).resolve().parent.parent
    return basis / "NUTZUNGSBEDINGUNGEN.md", basis / "DATENSCHUTZ.md"


def bedingungen_text() -> str:
    """The one line shown when a key is created: which terms apply and where they are."""
    nb, ds = rechtstexte()
    return (f"Lizenzschlüssel angelegt (Free-Plan). Es gelten die Nutzungsbedingungen (Version {BEDINGUNGEN_VERSION}) "
            f"und die Datenschutzerklärung: {nb} · {ds}")


def praefix() -> str:
    s = schluessel(anlegen=False) or ""
    return s[:12] + "…" if s else "(noch keiner)"


# ---------------------------------------------------------------- HTTP

def _verbinden(adresse, timeout=None, source_address=None) -> socket.socket:
    """Like socket.create_connection, but IPv4 first and at most 8 seconds per address.

    Some networks announce IPv6 without routing it; Python would then wait the full timeout on the IPv6 address
    before it tries IPv4."""
    host, port = adresse
    gesamt = timeout if isinstance(timeout, (int, float)) else None
    letzter: OSError | None = None
    infos = sorted(socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM), key=lambda i: i[0] != socket.AF_INET)
    for familie, typ, proto, _, ziel in infos:
        s = socket.socket(familie, typ, proto)
        try:
            s.settimeout(min(gesamt, 8) if gesamt else 8)
            if source_address:
                s.bind(source_address)
            s.connect(ziel)
            s.settimeout(gesamt)
            return s
        except OSError as e:
            letzter = e
            s.close()
    raise letzter or OSError(f"keine Adresse für {host}")


class _Http(http.client.HTTPConnection):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._create_connection = _verbinden


class _Https(http.client.HTTPSConnection):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._create_connection = _verbinden


class _HttpHandler(urllib.request.HTTPHandler):
    def http_open(self, req):
        return self.do_open(_Http, req)


class _HttpsHandler(urllib.request.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(_Https, req, context=self._context)


_OPENER = urllib.request.build_opener(_HttpHandler, _HttpsHandler)


def _aufruf(methode: str, pfad: str, body: dict | None = None, *, mit_schluessel: bool = True,
            timeout: int = 60) -> dict:
    kopf = {"User-Agent": f"akquise-und-abmahnschutz/{VERSION}", "Accept": "application/json"}
    if mit_schluessel:
        kopf["Authorization"] = "Bearer " + (schluessel() or "")
    daten = None
    if body is not None:
        daten = json.dumps(body, ensure_ascii=False).encode("utf-8")
        kopf["Content-Type"] = "application/json"
    req = urllib.request.Request(_api_url() + pfad, data=daten, headers=kopf, method=methode)
    try:
        with _OPENER.open(req, timeout=timeout) as r:
            text = r.read().decode("utf-8")
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as e:
        try:
            antwort = json.loads(e.read().decode("utf-8"))
            text = str(antwort.get("fehler") or antwort.get("hinweis") or e.reason)
        except (ValueError, UnicodeDecodeError, AttributeError):
            text = str(e.reason)
        raise ServerFehler(e.code, text) from None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
        raise ServerFehler(0, f"Server nicht erreichbar ({getattr(e, 'reason', e)})") from None


# ---------------------------------------------------------------- licence info

def auskunft(*, frisch: bool = False) -> dict:
    """Type, features, missing features and notices of this key. Cached for one hour; offline or on a server error
    (5xx) up to three days."""
    cache = ordner() / "lizenz_cache.json"
    alt: dict = {}
    try:
        alt = json.loads(cache.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    alter = time.time() - float(alt.get("_geladen", 0))
    if not frisch and alt and alter < CACHE_SEKUNDEN:
        return alt
    try:
        r = _aufruf("GET", "/lizenz")
    except ServerFehler as e:
        if (e.status == 0 or e.status >= 500) and alt and alter < CACHE_OFFLINE_TAGE * 86400:
            return alt
        raise
    r["_geladen"] = time.time()
    try:
        _schreibe_privat(cache, json.dumps(r, ensure_ascii=False))
    except OSError:
        pass
    return r


def hat_feature(code: str) -> bool:
    try:
        return code in (auskunft().get("features") or [])
    except ServerFehler:
        return False


def ist_pro() -> bool:
    try:
        return auskunft().get("typ") in PRO_TYPEN
    except ServerFehler:
        return False


def hinweise_text(befehl: str = "python3 werkzeuge/lizenz.py") -> list[str]:
    """The notices from the server, ready to print. The server decides which ones are shown.
    befehl is how the user calls the licence commands here, e.g. "python3 -m scraper"."""
    try:
        a = auskunft()
    except ServerFehler:
        return []
    zeilen = []
    for h in a.get("hinweise") or []:
        zeilen.append(f"{h.get('titel', 'Hinweis')}: {h.get('text', '')}")
        optionen = h.get("optionen") or []
        if "abo_ansehen" in optionen:
            zeilen.append(f"  Abo ansehen:  {befehl} abo")
        if "kostenfrei_reicht" in optionen:
            zeilen.append(f"  Ausblenden:   {befehl} hinweis {h.get('code')} kostenfrei_reicht")
    return zeilen


def hinweis_beantworten(code: str, antwort: str) -> None:
    _aufruf("POST", "/lizenz", {"aktion": "hinweis", "code": code, "antwort": antwort})
    auskunft(frisch=True)


# ---------------------------------------------------------------- leads

def _lead(eintrag: dict) -> dict:
    return {f: str(eintrag[f]).strip() for f in LEAD_FELDER if eintrag.get(f) not in (None, "")}


def leads_hochladen(leads: list[dict], *, pfad: str, bezeichnung: str | None = None) -> bool:
    """Hands in the exported leads (see the module text). Never stops the export: errors only return False."""
    daten = [d for d in (_lead(l) for l in leads) if d.get("firma") or d.get("email") or d.get("domain") or d.get("website")]
    if not daten:
        return True
    try:
        for i in range(0, len(daten), JE_AUFRUF):
            _aufruf("POST", "/leads/hochladen",
                    {"leads": daten[i:i + JE_AUFRUF], "pfad": pfad[:40], "bezeichnung": (bezeichnung or "")[:200]})
        return True
    except (ServerFehler, OSError):
        return False


# ---------------------------------------------------------------- blocklist check (subscription)

def _schwelle(name: str, standard: int) -> int:
    try:
        return min(max(int(os.environ.get(name, "") or standard), 1), 6)
    except ValueError:
        return standard


def schwellen() -> tuple[int, int]:
    """(sperren_ab, warnen_ab) from SPERREN_AB (default 3) and WARNEN_AB (default 1); warnen_ab never above sperren_ab."""
    sperren_ab = _schwelle("SPERREN_AB", 3)
    return sperren_ab, min(_schwelle("WARNEN_AB", 1), sperren_ab)


def norm_domain(wert) -> str:
    d = str(wert or "").strip().lower()
    if not d or " " in d:
        return ""
    if "@" in d:
        d = d.rsplit("@", 1)[1]
    d = re.sub(r"^[a-z]+://", "", d)
    d = d.split("/")[0].split("?")[0].split("#")[0].split(":")[0].rstrip(".")
    d = re.sub(r"^www\d?\.", "", d)
    return d if "." in d else ""


def _schluessel_wert(wert) -> str:
    """E-mail addresses stay addresses (an address can be blocked alone), everything else becomes a domain."""
    w = str(wert or "").strip().lower()
    if "@" in w and " " not in w:
        return w
    return norm_domain(w)


STUFEN = {1: "Beschwerde", 2: "Widerspruch", 3: "Drohung", 4: "Abmahnung", 5: "Abmahnung über eine Kanzlei",
          6: "Gerichtsverfahren"}


def _beschreibung(e: dict) -> str:
    """The server answers per hit only "empfehlung" and the severity "stufe"; without a severity the address is blocked."""
    stufe = e.get("stufe")
    if not stufe:
        return "Adresse gesperrt (Austragung oder Widerspruch)"
    return f"Stufe {stufe} ({STUFEN.get(int(stufe), 'Vorfall')})"


class Sperrabgleich:
    """Result of the graded check for a set of values (e-mail addresses, websites, domains)."""

    def __init__(self, ergebnisse: dict[str, dict], sperren_ab: int, warnen_ab: int):
        self.ergebnisse = ergebnisse
        self.sperren_ab = sperren_ab
        self.warnen_ab = warnen_ab
        self.quelle = (f"Server-Abgleich ({datetime.now():%d.%m.%Y %H:%M}), sperren ab Stufe {sperren_ab}, "
                       f"warnen ab Stufe {warnen_ab}")

    def _erste(self, empfehlung: str, werte) -> str | None:
        for w in werte:
            e = self.ergebnisse.get(_schluessel_wert(w))
            if e and e.get("empfehlung") == empfehlung:
                return _beschreibung(e)
        return None

    def treffer(self, *werte) -> str | None:
        """Reason why the lead must not be contacted, or None."""
        return self._erste("sperren", werte)

    def warnung(self, *werte) -> str | None:
        """Below the block threshold, but known: a reason to look closer."""
        return self._erste("warnen", werte)

    def __len__(self) -> int:
        return len(self.ergebnisse)


def abgleichen(werte, *, sperren_ab: int | None = None, warnen_ab: int | None = None) -> Sperrabgleich:
    """Checks all values in batches. Raises ServerFehler (402 without subscription, 0 without connection)."""
    standard = schwellen()
    sperren_ab = sperren_ab or standard[0]
    warnen_ab = min(warnen_ab or standard[1], sperren_ab)
    eindeutig = sorted({s for s in (_schluessel_wert(w) for w in werte) if s})
    ergebnisse: dict[str, dict] = {}
    for i in range(0, len(eindeutig), JE_AUFRUF):
        teil = eindeutig[i:i + JE_AUFRUF]
        r = _aufruf("POST", "/sperrliste/abgleich", {
            "eintraege": [{"email": w} if "@" in w else {"domain": w} for w in teil],
            "sperren_ab": sperren_ab, "warnen_ab": warnen_ab})
        for e in r.get("ergebnisse") or []:
            nr = int(e.get("nr", 0)) - 1
            if 0 <= nr < len(teil) and e.get("empfehlung") in ("sperren", "warnen"):
                ergebnisse[teil[nr]] = e
    return Sperrabgleich(ergebnisse, sperren_ab, warnen_ab)


def _letzter_typ() -> str | None:
    """Type from the last stored licence info, whatever its age; None if there is none."""
    try:
        typ = json.loads((ordner() / "lizenz_cache.json").read_text(encoding="utf-8")).get("typ")
    except (OSError, ValueError, AttributeError):
        return None
    return str(typ) if typ else None


def _ohne_abgleich(grund: str, fehler: str) -> SystemExit:
    return SystemExit(
        f"{grund}: {fehler}.\n"
        "Ohne Abgleich wird nicht exportiert. Internetverbindung prüfen und erneut exportieren.\n"
        "Im Scraper nur wenn bewusst ohne Abgleich exportiert werden soll: SPERRLISTE_PFLICHT=false setzen.")


def sperrabgleich_laden(werte, *, pflicht: bool = True) -> Sperrabgleich | None:
    """For the export. None in the free plan (the caller shows the notice). Fails closed: with a subscription, or
    when the licence type cannot be determined, and no connection the export stops, unless pflicht is False."""
    try:
        pro = auskunft().get("typ") in PRO_TYPEN
    except ServerFehler as e:
        letzter = _letzter_typ()
        if letzter is not None and letzter not in PRO_TYPEN:
            return None
        if pflicht:
            raise _ohne_abgleich("Der Lizenzstatus lässt sich nicht prüfen", e.text) from None
        return None
    if not pro:
        return None
    try:
        return abgleichen(werte)
    except ServerFehler as e:
        if e.status == 402:
            return None
        if pflicht:
            raise _ohne_abgleich("Der Sperrlisten-Abgleich ist nicht möglich", e.text) from None
        return None


# ---------------------------------------------------------------- reports

def melden(meldung: dict, *, quelle: str = "scraper") -> dict:
    return _aufruf("POST", "/meldung", {**meldung, "quelle": quelle})


def adresse_sperren(email: str, grund: str = "austragung") -> dict:
    return _aufruf("POST", "/meldung", {"aktion": "adresse_sperren", "email": email, "grund": grund})


def abmahnung_pruefen(abmahnung: dict) -> dict:
    return _aufruf("POST", "/abmahnung/pruefen", {"abmahnung": abmahnung}, timeout=120)


# ---------------------------------------------------------------- support package

GEHEIM_NAME = re.compile(r"KEY|TOKEN|SECRET|PASS|SCHLUESSEL|GEHEIM|AUTH|COOKIE|WEBHOOK|URL", re.I)
HARMLOS_WERT = re.compile(r"^(true|false|ja|nein|on|off|\d{1,6}(\.\d+)?|[a-z0-9_.:-]{1,40})$", re.I)
VERTRAULICH = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"                     # e-mail addresses
    r"|\b(?:sk|rk|pk)_(?:test|live)_[A-Za-z0-9]{8,}|\bwhsec_[A-Za-z0-9]{8,}"  # Stripe
    r"|\bsk-ant-[A-Za-z0-9_-]{8,}|\bsk-[A-Za-z0-9_-]{16,}"                   # Anthropic, OpenAI
    r"|\baks_[A-Za-z0-9_-]{9,}|\beak_[A-Za-z0-9_-]{8,}"                      # licence (the 12-character prefix stays), Skael
    r"|\b(?=[A-Za-z0-9_-]*[A-Z])(?=[A-Za-z0-9_-]*[a-z])(?=[A-Za-z0-9_-]*\d)[A-Za-z0-9_-]{24,}\b")  # other tokens
AUSGESCHLOSSEN_ORDNER = {"data", "exports", "auftraege", "arbeit", "__pycache__", ".git", "faelle", "node_modules"}


def _schwaerzen(text: str) -> str:
    return VERTRAULICH.sub("[entfernt]", text)


def _einstellungen(datei: Path) -> list[str]:
    """Names of all settings; the value only when it is harmless (numbers, switches, model names)."""
    zeilen = []
    for z in datei.read_text(encoding="utf-8", errors="replace").splitlines():
        z = z.strip()
        if not z or z.startswith("#") or "=" not in z:
            continue
        name, wert = (t.strip() for t in z.split("=", 1))
        wert = wert.strip("\"'")
        if not wert:
            zeilen.append(f"{name} = (leer)")
        elif GEHEIM_NAME.search(name) or not HARMLOS_WERT.match(wert):
            zeilen.append(f"{name} = (gesetzt)")
        else:
            zeilen.append(f"{name} = {wert}")
    return zeilen


def support_paket(wurzel: Path, ziel: Path | None = None, beschreibung: str = "") -> Path:
    """ZIP with system, version and settings for support. Never .env values, keys or lead data."""
    wurzel = wurzel.resolve()
    ziel = ziel or (Path.home() / "Desktop" if (Path.home() / "Desktop").is_dir() else Path.cwd())
    datei = ziel / f"support-paket_{datetime.now():%Y%m%d_%H%M%S}.zip"
    teile: dict[str, str] = {}

    a: dict = {}
    try:
        a = auskunft(frisch=True)
    except ServerFehler as e:
        a = {"fehler": e.text}
    teile["system.txt"] = "\n".join([
        f"Erstellt: {datetime.now():%Y-%m-%d %H:%M}",
        f"Betriebssystem: {platform.platform()}",
        f"Python: {sys.version.split()[0]}",
        f"Werkzeug-Version: {VERSION}",
        f"Lizenz: {praefix()} · Typ {a.get('typ', '?')} · Features {', '.join(a.get('features') or []) or '-'}",
        f"Ordner: {wurzel.name}",
    ]) + "\n"

    changelog = wurzel / "CHANGELOG.md"
    if changelog.exists():
        stand = re.findall(r"^## (\S+)", changelog.read_text(encoding="utf-8"), re.M)
        teile["system.txt"] += f"Stand laut CHANGELOG: {stand[0] if stand else '?'}\n"

    einstellungen, dateien = [], []
    for p in sorted(wurzel.rglob("*")):
        rel = p.relative_to(wurzel)
        if set(rel.parts) & AUSGESCHLOSSEN_ORDNER:
            continue
        if p.is_file() and (p.name == ".env" or p.name.endswith(".env")):
            einstellungen.append(f"[{rel}]")
            einstellungen.extend(_einstellungen(p))
            einstellungen.append("")
        elif p.is_file() and p.suffix in {".py", ".mjs", ".md", ".txt", ".json", ".sh"}:
            dateien.append(f"{rel}  {p.stat().st_size} B  {datetime.fromtimestamp(p.stat().st_mtime):%Y-%m-%d}")
    teile["einstellungen.txt"] = "\n".join(einstellungen) + "\n"
    teile["dateien.txt"] = "\n".join(dateien) + "\n"
    if beschreibung.strip():
        teile["beschreibung.txt"] = beschreibung.strip() + "\n"

    ziel.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(datei, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in teile.items():
            z.writestr(name, _schwaerzen(text))
    return datei


# topics and "wobei" of the form on ak.consulting/support (betreiber/supportseite.md, server _shared/support.ts)
SUPPORT_THEMEN = {
    "scraper_google_maps": "Lead-Scraper: Google Maps",
    "scraper_ecommerce": "Lead-Scraper: E-Commerce und Amazon",
    "scraper_stellensuche": "Lead-Scraper: Stellensuche und Recruiting",
    "scraper_videoseiten": "Lead-Scraper: Videoseiten",
    "anreicherung": "Anreicherung: Geschäftsführer, E-Mail, Ansprache",
    "export_sperrliste": "Export und Sperrlisten-Abgleich",
    "instantly": "Instantly-Anbindung",
    "abmahnung": "Abmahnung prüfen (Werbemail-Abwehr)",
    "einrichtung_lizenz": "Installation, Einrichtung und Lizenz",
    "abo_rechnung": "Abo, Rechnung und Kündigung",
    "datenschutz": "Datenschutz und Widerspruch",
    "sonstiges": "Sonstiges",
}
SUPPORT_ANLIEGEN = {
    "fehler": "Fehlermeldung oder Abbruch",
    "ergebnis": "Ergebnis falsch oder unvollständig",
    "einrichtung": "Einrichtung oder Zugang klappt nicht",
    "bedienung": "Frage zur Bedienung",
    "vorschlag": "Verbesserungsvorschlag",
    "zahlung": "Zahlung",
    "rechnung": "Rechnung",
    "kuendigung": "Kündigung",
    "auskunft": "Auskunft",
    "widerspruch": "Widerspruch",
    "loeschung": "Löschung",
    "frage": "Sonstige Frage",
}
OHNE_ABO_THEMEN = ("abo_rechnung", "datenschutz")


def support_angaben(datei: Path | None, thema: str | None = None, anliegen: str | None = None,
                    beschreibung: str = "") -> list[str]:
    """The form fields of ak.consulting/support in the order of the page, ready to print."""
    s = schluessel(anlegen=False) or ""
    offen = "(bitte im Formular wählen)"
    zeilen = [f"Support-Anfrage – Formular: {SUPPORT_URL}", ""]
    zeilen.append(f"  1. Thema:             {SUPPORT_THEMEN.get(thema or '', offen)}")
    zeilen.append(f"  2. Wobei:             {SUPPORT_ANLIEGEN.get(anliegen or '', offen)}")
    zeilen.append(f"  3. Lizenz-Kennung:    {s[:12] if s else '(noch keiner, Feld leer lassen)'}"
                  + ("  (nur diese 12 Zeichen, nie den ganzen Schlüssel)" if s else ""))
    zeilen.append(f"  4. Support-Paket:     {datei}  (hochladen)" if datei else "  4. Support-Paket:     (bei diesem Thema nicht nötig)")
    if beschreibung.strip():
        text = _schwaerzen(beschreibung.strip()).splitlines()
        zeilen.append(f"  5. Beschreibung:      {text[0]}")
        zeilen.extend(f"                       {z}" for z in text[1:])
    else:
        zeilen.append("  5. Beschreibung:      Was wolltest du tun, was ist passiert, Fehlermeldung wörtlich, seit wann?")
    zeilen.append("  6. Video (optional):  Link zu einer Bildschirmaufnahme (Loom, YouTube nicht gelistet, Google Drive)")
    zeilen.append("  7. Kontakt:           Name, Firma und E-Mail für die Antwort")
    return zeilen


# ---------------------------------------------------------------- commands

def _fehler(e: ServerFehler) -> int:
    print(f"Fehler: {e.text}", file=sys.stderr)
    return 1


def cmd_status(args) -> int:  # noqa: ARG001
    try:
        a = auskunft(frisch=True)
    except ServerFehler as e:
        return _fehler(e)
    print(f"Lizenz: {praefix()} · Typ: {a.get('typ')}")
    print(f"Features: {', '.join(a.get('features') or []) or 'keine (Free-Plan)'}")
    if a.get("abo"):
        print(f"Abo: {a['abo'].get('status')} bis {a['abo'].get('laeuft_bis')}"
              + (f", gekündigt zum {a['abo']['kuendigung_zum']}" if a['abo'].get('kuendigung_zum') else ""))
    for z in hinweise_text(BEFEHL):
        print(z)
    return 0


def cmd_abo(args) -> int:  # noqa: ARG001
    try:
        a = auskunft(frisch=True)
        if a.get("typ") in ("partner", "intern"):
            print("Dieser Schlüssel braucht kein Abo.")
            return 0
        aktion = "portal" if a.get("typ") == "abo" else "checkout"
        url = _aufruf("POST", "/lizenz", {"aktion": aktion})["url"]
    except ServerFehler as e:
        return _fehler(e)
    print("Abo verwalten (Stripe):" if aktion == "portal" else "Abo abschließen (Stripe):")
    print(url)
    try:
        webbrowser.open(url)
    except webbrowser.Error:
        pass
    return 0


def cmd_hinweis(args) -> int:
    try:
        hinweis_beantworten(args.code, args.antwort)
    except ServerFehler as e:
        return _fehler(e)
    print("Gespeichert.")
    return 0


def cmd_instantly(args) -> int:
    try:
        if args.aktion == "trennen":
            _aufruf("POST", "/instantly/trennen", {})
            print("Instantly getrennt. Der Webhook in Instantly ist gelöscht.")
            return 0
        if not hat_feature("instantly_sync"):
            print(FREE_PLAN_TEXT if not ist_pro() else "Dieses Feature ist in deinem Abo nicht enthalten")
            return 1
        api_key = os.environ.get("INSTANTLY_API_KEY") or getpass.getpass(
            "Instantly API-Schlüssel (Eingabe unsichtbar; Scopes: Webhooks, Leads lesen, Blockliste): ").strip()
        if not api_key:
            print("Abgebrochen: kein Schlüssel eingegeben.")
            return 1
        _aufruf("POST", "/instantly/verbinden", {"instantly_api_key": api_key, "sync_ab_stufe": args.ab_stufe})
    except ServerFehler as e:
        return _fehler(e)
    print("Instantly verbunden.")
    print("  Antworten werden eingeordnet; höfliche Absagen bleiben ohne Folgen, Austragungen sperren nur die Adresse.")
    print(f"  Nachts werden bekannte Abmahner unter deinen Instantly-Leads gesperrt (ab Stufe {args.ab_stufe}).")
    return 0


def cmd_support(args, wurzel: Path | None = None) -> int:
    """Support package for everyone, then the fields of the support form. Without a subscription a notice comes
    first: technical support (premium support) is part of the subscription."""
    thema = getattr(args, "thema", None)
    premium: bool | None
    try:
        a = auskunft(frisch=True)
        premium = "support_paket" in (a.get("features") or []) or a.get("typ") in ("partner", "intern")
    except ServerFehler:
        premium = None
    if premium is False and thema not in OHNE_ABO_THEMEN:
        print("Hinweis: Technischer Support (Premium-Support) ist Teil des Abos. Für deine Lizenz läuft kein Abo.")
        print("  Du kannst die Anfrage senden, sie wird aber erst mit Abo bearbeitet.")
        print(f"  Abo abschließen: {BEFEHL} abo")
        print("  Fragen zu Abo, Rechnung und Datenschutz beantworten wir auch ohne Abo.")
        print()
    elif premium is None:
        print("Hinweis: Der Server war nicht erreichbar, der Abo-Status wird beim Absenden geprüft.")
        print()

    datei = None
    if thema not in OHNE_ABO_THEMEN:
        wurzel = wurzel or Path(__file__).resolve().parent.parent
        datei = support_paket(wurzel, Path(args.ziel) if getattr(args, "ziel", None) else None,
                              getattr(args, "beschreibung", "") or "")
        print(f"Support-Paket erstellt: {datei}")
        print("  Enthält System, Version, Namen der Einstellungen und Dateiliste.")
        print("  Keine Werte aus .env, keine Schlüssel, keine Leads.")
        print()
    for z in support_angaben(datei, thema, getattr(args, "anliegen", None), getattr(args, "beschreibung", "") or ""):
        print(z)
    if not getattr(args, "ohne_browser", False):
        try:
            webbrowser.open(SUPPORT_URL)
        except webbrowser.Error:
            pass
    return 0


BEFEHL = "python3 werkzeuge/lizenz.py"


def befehle_einhaengen(sub, wurzel: Path | None = None, befehl: str | None = None) -> None:
    """Adds the licence commands to another argparse CLI (scraper, ecom). befehl: how the user calls that CLI."""
    global BEFEHL
    if befehl:
        BEFEHL = befehl
    p = sub.add_parser("lizenz", help="Lizenz, Abo und Hinweise anzeigen")
    p.set_defaults(func=cmd_status)
    p = sub.add_parser("abo", help="Abo abschließen bzw. verwalten (Stripe, öffnet den Browser)")
    p.set_defaults(func=cmd_abo)
    p = sub.add_parser("hinweis", help="Pro-Hinweis beantworten, z. B. kostenfrei_reicht")
    p.add_argument("code")
    p.add_argument("antwort", choices=["kostenfrei_reicht", "abo_ansehen", "gelesen"])
    p.set_defaults(func=cmd_hinweis)
    p = sub.add_parser("instantly", help="Instantly verbinden oder trennen (Abo)")
    p.add_argument("aktion", choices=["verbinden", "trennen"])
    p.add_argument("--ab-stufe", type=int, default=3, choices=range(1, 7),
                   help="Leads nachts sperren ab dieser Stufe (Standard 3)")
    p.set_defaults(func=cmd_instantly)
    for name in ("support", "support-paket"):
        p = sub.add_parser(name, help="Support: ZIP ohne Schlüssel und Leads, dazu die Angaben für ak.consulting/support"
                           if name == "support" else "wie support")
        p.add_argument("--thema", choices=sorted(SUPPORT_THEMEN), help="Thema des Formulars")
        p.add_argument("--anliegen", choices=sorted(SUPPORT_ANLIEGEN), help="wobei Hilfe gebraucht wird")
        p.add_argument("--beschreibung", help="kurz, was nicht funktioniert")
        p.add_argument("--ziel", help="Ordner für die ZIP-Datei (Standard: Schreibtisch)")
        p.add_argument("--ohne-browser", action="store_true", help="die Supportseite nicht öffnen")
        p.set_defaults(func=lambda a: cmd_support(a, wurzel))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lizenz und Server-Dienste von Akquise & Abmahnschutz")
    sub = parser.add_subparsers(dest="befehl", required=True)
    befehle_einhaengen(sub)
    p = sub.add_parser("status", help="wie lizenz")
    p.set_defaults(func=cmd_status)
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    sys.exit(main())
