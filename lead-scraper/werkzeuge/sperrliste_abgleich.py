#!/usr/bin/env python3
"""Gleicht eine beliebige Leadliste (CSV) mit der Sperrliste ab – für Amazon und alle Pfade ohne eingebauten Export.

    python3 werkzeuge/sperrliste_abgleich.py liste.csv [--spalten "E-Mail,Website"] [--pfad amazon]

Mit Abo (oder Partner-Schlüssel) prüft der Server jeden Eintrag abgestuft (Ergebnis und Stufe 1 bis 6):
    <liste>_bereinigt.csv   → für die Ansprache; bekannte, aber schwächere Fälle mit Spalte „Sperrliste Hinweis“
    <liste>_gesperrt.csv    → nie anschreiben (mit Spalte „Sperrgrund“)
Die Schwellen stehen in der Umgebung bzw. .env: SPERREN_AB (Standard 3) und WARNEN_AB (Standard 1).

Im Free-Plan gibt es keinen Abgleich. Es wird nichts geschrieben, nur der Hinweis angezeigt.

In beiden Fällen werden die Leads der Liste danach an den Server übertragen (Firmen und Ansprechpartner),
wie in den Nutzungsbedingungen beschrieben (Klausel „Datenweitergabe im Free-Plan“).

Abgeglichen werden alle Spalten, deren Name nach E-Mail, Website, Domain oder URL aussieht (Amazon-Storefront-
Links ausgenommen), oder die mit --spalten genannten. Nur Python-Standardbibliothek.
"""
import argparse, csv, os, re, sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lizenz  # noqa: E402

SPALTEN_MUSTER = re.compile(r"mail|website|webseite|domain|url|homepage", re.I)
AUSNAHMEN = re.compile(r"storefront|amazon|linkedin|maps|bild|image|logo|quelle", re.I)

# column name (lower case, without spaces/underscores/hyphens) → lead field of the server
FELD_SPALTEN = {
    "firma": ("firma", "firmenname", "company", "companyname", "unternehmen", "shopname", "verkaeufer", "seller",
              "sellername", "haendler", "händler"),
    "email": ("email", "emailadresse", "mail"),
    "email_status": ("emailstatus",),
    "website": ("website", "webseite", "homepage", "url", "shopurl"),
    "domain": ("domain",),
    "anrede": ("anrede",),
    "vorname": ("vorname", "firstname"),
    "nachname": ("nachname", "lastname"),
    "position": ("position", "jobtitel", "titel"),
    "telefon": ("telefon", "phone", "tel"),
    "strasse": ("strasse", "straße", "street"),
    "plz": ("plz", "postleitzahl", "zip"),
    "ort": ("ort", "stadt", "city"),
    "land": ("land", "country"),
    "branche": ("branche", "kategorie", "category"),
    "handelsregister": ("handelsregister", "hrb"),
    "externe_id": ("externeid", "id", "sellerid", "merchantid"),
    "quelle_url": ("quelleurl", "impressum", "impressumurl"),
}


def lies_csv(pfad):
    with open(pfad, encoding="utf-8-sig", newline="") as f:
        probe = f.read(16384)
        f.seek(0)
        try:
            trenner = csv.Sniffer().sniff(probe, delimiters=",;\t").delimiter
        except csv.Error:
            trenner = ","
        # only the delimiter comes from the sniffer: its guessed quoting breaks on a quote character further down
        r = csv.DictReader(f, delimiter=trenner)
        return list(r.fieldnames or []), list(r), trenner


def _schluessel(name):
    return re.sub(r"[\s_\-]", "", str(name or "").lower())


def _wert(wert):
    """Cell value without the leading apostrophe Excel uses to keep text as text (e.g. '+49 …, '=…)."""
    w = str(wert or "").strip()
    return w[1:].strip() if w.startswith("'") else w


def lead_eintrag(zeile, felder, pfad):
    """One CSV row as lead for the server (fields see lizenz.LEAD_FELDER)."""
    zuordnung = {}
    for feld in felder:
        k = _schluessel(feld)
        for ziel, namen in FELD_SPALTEN.items():
            if k in namen and ziel not in zuordnung:
                zuordnung[ziel] = feld
    eintrag = {ziel: _wert(zeile.get(spalte)) for ziel, spalte in zuordnung.items()}
    if not eintrag.get("domain"):
        eintrag["domain"] = lizenz.norm_domain(eintrag.get("website") or "")
    eintrag.setdefault("quelle", f"Lead-Scraper, Pfad {pfad}")
    eintrag.setdefault("erfasst_am", date.today().isoformat())
    return eintrag


def schreibe(name, felder, daten, trenner):
    with open(name + ".tmp", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=felder, delimiter=trenner, lineterminator="\r\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(daten)
    os.replace(name + ".tmp", name)  # never leave a truncated list behind


def main(argv=None):
    p = argparse.ArgumentParser(description="Leadliste mit der Sperrliste abgleichen (Abo) und übertragen")
    p.add_argument("liste")
    p.add_argument("--spalten", help="kommagetrennte Spaltennamen; Standard: automatisch erkennen")
    p.add_argument("--pfad", default="amazon", help="Herkunft der Liste, z. B. amazon (Standard)")
    a = p.parse_args(argv)

    for strom in (sys.stdout, sys.stderr):  # Windows with redirected output: never crash on a character
        try:
            strom.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass

    felder, zeilen, trenner = lies_csv(a.liste)
    if a.spalten:
        spalten = [s.strip() for s in a.spalten.split(",") if s.strip()]
        fehlend = [s for s in spalten if s not in felder]
        if fehlend:
            sys.exit(f"Spalte(n) nicht gefunden: {', '.join(fehlend)}. Vorhanden: {', '.join(felder)}")
    else:
        spalten = [f for f in felder if f and SPALTEN_MUSTER.search(f) and not AUSNAHMEN.search(f)]
    if not spalten:
        sys.exit(f"Keine E-Mail-/Website-Spalte erkannt. Mit --spalten angeben. Vorhanden: {', '.join(felder)}")

    werte = [_wert(z.get(s)) for z in zeilen for s in spalten if _wert(z.get(s))]
    sperre = lizenz.sperrabgleich_laden(werte, pflicht=True)
    lizenz.leads_hochladen([lead_eintrag(z, felder, a.pfad) for z in zeilen], pfad=a.pfad,
                           bezeichnung=Path(a.liste).stem)

    if sperre is None:
        print("Kein Sperrlisten-Abgleich: " + lizenz.FREE_PLAN_TEXT)
        for z in lizenz.hinweise_text("python3 werkzeuge/lizenz.py"):
            print(z)
        return 0

    gesperrt, frei, gewarnt = [], [], 0
    for z in zeilen:
        werte_z = [_wert(z.get(s)) for s in spalten]
        grund = sperre.treffer(*werte_z)
        if grund:
            gesperrt.append({**z, "Sperrgrund": f"Sperrliste: {grund}"})
            continue
        hinweis = sperre.warnung(*werte_z)
        gewarnt += bool(hinweis)
        frei.append({**z, "Sperrliste Hinweis": hinweis or ""})

    basis = os.path.splitext(a.liste)[0]
    schreibe(f"{basis}_bereinigt.csv", felder + ["Sperrliste Hinweis"], frei, trenner)
    schreibe(f"{basis}_gesperrt.csv", felder + ["Sperrgrund"], gesperrt, trenner)

    print(f"Sperrliste: {sperre.quelle}")
    print(f"Abgeglichene Spalten: {', '.join(spalten)}")
    print(f"{len(zeilen)} Zeilen: {len(frei)} frei (davon {gewarnt} mit Hinweis), {len(gesperrt)} gesperrt")
    print(f"  {basis}_bereinigt.csv  -> für die Ansprache")
    print(f"  {basis}_gesperrt.csv   -> nie anschreiben")
    return 0


if __name__ == "__main__":
    sys.exit(main())
