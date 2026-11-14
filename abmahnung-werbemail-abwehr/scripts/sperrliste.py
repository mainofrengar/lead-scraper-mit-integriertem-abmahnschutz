#!/usr/bin/env python3
"""Sperrliste und Abmahnungs-Check über den Server von Agentur Consulting. Nur Python-Standardbibliothek.

Es gibt keine öffentliche Liste. Alle Daten gehen nur an den Server und werden nie ausgegeben;
zurück kommt nur das Ergebnis des Abgleichs für selbst geprüfte Einträge. Der Lizenzschlüssel wird beim ersten Aufruf automatisch angelegt (Free-Plan,
siehe scripts/lizenz.py) und nie angezeigt.

Befehle:
  check     --datei abmahnung.json [--json] [--dry-run]                                   kostenlos
            Sendet die Angaben zur Abmahnung (Format: references/06_sperrliste-server.md) und zeigt
            „So würden wir damit umgehen“. Die Abmahnung wird auf dem Server gespeichert.
  melden    --domains D [D …] --monat JJJJ-MM --melder-domain EIGENE.DE --art82 ja|nein
            [--kanzlei-domain K] [--stufe 1-6] [--forderung SPANNE] [--vorgehen CODE,CODE]
            [--status AUSGANG] [--beleg-art ART] [--einreichung NR] [--dry-run]           kostenlos
            Meldet die Domains des Abmahners. Stufe ohne Angabe: 5 mit Kanzlei, sonst 4.
  pruefen   --domain D [D …] [--kanzlei-domain K] [--json]                                 nur mit Abo
            Abgestufter Abgleich: Ist der Abmahner bekannt, mit welcher Stufe, wie oft, wann zuletzt?
  abgleich  --kontakte kontakte.csv [--spalte email|website|domain] [--out-praefix P]      nur mit Abo
            Gleicht eine Kontaktliste ab: schreibt <präfix>_gesperrt.csv und <präfix>_bereinigt.csv.

Exit-Codes: 0 ok · 1 Fehler · 2 Eingabe ungültig · 3 vom Server abgelehnt · 4 Server nicht erreichbar · 5 Free-Plan
Umgebung (Tests, Partner): LIZENZ_SCHLUESSEL, ABMAHNSCHUTZ_API_URL, ABMAHNSCHUTZ_ORDNER, SPERREN_AB, WARNEN_AB.
"""
import argparse
import csv
import json
import os
import re
import sys
from datetime import date

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import lizenz  # noqa: E402

VERSION = "skill-4.0"
CLIENT = "abmahnung-werbemail-abwehr/4.1"
NUTZUNGSBEDINGUNGEN_VERSION = "2026-11"
ABSENDER = "Agentur Consulting"

# Fixed notice of the server (server/supabase/functions/_shared/abmahnung.ts); used only if an answer lacks it
KEINE_RECHTSBERATUNG = (
    "Keine Rechtsberatung: Das ist eine allgemeine Beschreibung, wie wir mit einer solchen Abmahnung umgehen würden. "
    "Sie ersetzt keine anwaltliche Prüfung des Einzelfalls. Bei Unsicherheit eine Anwältin oder einen Anwalt beauftragen.")

STUFEN = {1: "negativ", 2: "widerspruch", 3: "drohung", 4: "abmahnung_selbst", 5: "abmahnung_anwalt", 6: "gericht"}
FORDERUNG = ["unbekannt", "0", "1-500", "500-1000", "1000-2000", "2000-5000", ">5000"]
STATUS = ["offen", "keine_reaktion", "erledigt_ohne_zahlung", "erledigt_mit_zahlung", "vergleich",
          "mahnbescheid", "klage", "unbekannt"]
VORGEHEN = ["UE_MODIFIZIERT", "UE_ORIGINAL", "UE_VERWEIGERT", "ART82_ABGELEHNT", "ART82_GEZAHLT",
            "KOSTEN_ABGELEHNT", "KOSTEN_GEZAHLT", "KOSTEN_VERGLEICH", "AUSKUNFT_ERTEILT", "WEBSITE_BLOCK",
            "ANWALT_BEAUFTRAGT"]
BELEG_ART = ["abmahnschreiben", "anwaltsschreiben", "email_antwort", "brief", "gerichtsdokument", "sonstiges", "keiner"]
RE_DOMAIN = re.compile(r"^(?=.{4,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$")
RE_MONAT = re.compile(r"^20\d{2}-(0[1-9]|1[0-2])$")
RE_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
MAX_DOMAINS = 15
MAX_EINREICHUNG = 200_000
# Local minimum; the server checks its full protection list
GESCHUETZT_MIN = {"gmail.com", "googlemail.com", "web.de", "gmx.de", "gmx.net", "t-online.de", "outlook.com",
                  "hotmail.com", "hotmail.de", "live.de", "yahoo.com", "yahoo.de", "icloud.com", "me.com",
                  "aol.com", "freenet.de", "posteo.de", "mailbox.org", "proton.me", "protonmail.com", "gmx.at",
                  "gmx.ch", "bluewin.ch", "outlook.de", "msn.com", "co.uk", "com.au"}

# Submission format of /abmahnung/pruefen (datenbank/migrationen/0001, 0007). Everything else is dropped.
FORMAT = {
    "einwilligung": {"dokumente", "kontakt"},
    "lead": {"firma", "rechtsform", "kaufmann", "strasse", "plz", "ort", "vertreter", "domain", "website",
             "kontakt_name", "kontakt_email", "kontakt_telefon"},
    "kanzlei": {"name", "rechtsform", "strasse", "plz", "ort", "domain", "telefon", "email", "website", "iban",
                "anwalt", "fachanwaltschaften"},
    "abmahner": {"firma", "ist_person", "rechtsform", "strasse", "plz", "ort", "registergericht", "registernummer",
                 "branche", "vertreter", "website", "domains"},
    "fall": {"aktenzeichen", "abmahnung_datum", "zugang_datum", "frist_ue", "frist_zahlung", "frist_auskunft",
             "absender_domain", "beworbene_marke", "mitbewerber"},
    "forderungen": {"unterlassung", "gegenstandswert", "gebuehrensatz", "geschaeftsgebuehr", "pauschale", "ust_betrag",
                    "kosten_gesamt", "art82_gefordert", "art82_betrag", "art82_schaden_dargelegt",
                    "auskunft_gefordert", "weitere"},
    "ue_entwurf": {"liegt_bei", "zahlungspflichten", "vertragsstrafe_modell", "vertragsstrafe_betrag", "reichweite",
                   "oder_falle", "ohne_anerkennung", "aufloesende_bedingung", "erstreckung_dritte", "auffaelligkeiten"},
    "pruefung": {"einstufung", "warnzeichen"},
    "vorgehen": {"ue_vorgehen", "ue_abgegeben_am", "kostenposition", "art82_position", "auskunft_erteilt_am",
                 "website_block", "anwalt_beauftragt", "antwort_versandt_am", "gezahlter_betrag"},
}
FORMAT_LISTEN = {
    "mails": {"gesendet_am", "absender_name", "absender_adresse", "ziel_name", "ziel_adresse", "adresstyp", "betreff",
              "art", "tracking_oder_videolink", "kopie_liegt_bei", "inhalt"},
    "zitate": {"gericht", "aktenzeichen", "datum", "behauptete_aussage"},
    "dokumente": {"dateiname", "art", "sha256"},
}
FORMAT_WERTE = {"nutzungsbedingungen_version", "client", "status", "sperrliste_meldung_id"}
LEAD_KONTAKT = ("kontakt_name", "kontakt_email", "kontakt_telefon")
DATUMSFELDER = ("abmahnung_datum", "zugang_datum", "frist_ue", "frist_zahlung", "frist_auskunft")


# ---------------------------------------------------------------- basics

def norm_domain(d):
    d = str(d or "").strip().lower()
    if "@" in d:
        d = d.rsplit("@", 1)[1]
    d = re.sub(r"^[a-z]+://", "", d)
    d = d.split("/")[0].split("?")[0].split("#")[0].split(":")[0].rstrip(".")
    d = re.sub(r"^www\d?\.", "", d)
    try:
        d = d.encode("idna").decode("ascii") if d and not d.isascii() else d
    except UnicodeError:
        pass
    return d


def eltern(d):
    """d itself and all parent domains (a.b.example.de -> a.b.example.de, b.example.de, example.de, de)."""
    teile = d.split(".")
    return [".".join(teile[i:]) for i in range(len(teile))]


def geschuetzt(d):
    return any(e in GESCHUETZT_MIN for e in eltern(d)[:-1])


def verwandt(a, b):
    """True if a is b or one is a subdomain of the other."""
    return a in eltern(b) or b in eltern(a)


def server_fehler(e: lizenz.ServerFehler, *, was: str) -> int:
    """Prints a server error in plain words and returns the exit code."""
    if e.status == 0:
        print(f"Der Server von {ABSENDER} ist nicht erreichbar ({e.text}). {was} hat nicht stattgefunden.\n"
              "Bitte später erneut versuchen. Die Internetverbindung bzw. die Netzwerkfreigabe prüfen.")
        return 4
    if e.status == 402:
        free_plan()
        return 5
    if e.status in (400, 403, 409, 422, 429):
        print(f"Der Server hat abgelehnt: {e.text}")
        return 3
    print(f"Fehler vom Server (HTTP {e.status}): {e.text}")
    return 1


def free_plan():
    print(lizenz.FREE_PLAN_TEXT)
    print("Der abgestufte Abgleich gehört zum Abo. Kostenlos bleiben der Abmahnungs-Check "
          "(python3 scripts/sperrliste.py check --datei abmahnung.json) und die Meldung (melden).")
    print("Abo ansehen: python3 scripts/lizenz.py abo")


def abo_vorhanden():
    """None if the graded check may run, else the exit code (message already printed)."""
    try:
        a = lizenz.auskunft()
        if a.get("typ") not in lizenz.PRO_TYPEN:
            a = lizenz.auskunft(frisch=True)   # a subscription bought within the last hour
    except lizenz.ServerFehler as e:
        return server_fehler(e, was="Der Abgleich")
    if a.get("typ") not in lizenz.PRO_TYPEN:
        free_plan()
        return 5
    return None


# ---------------------------------------------------------------- check (free)

def _gueltiges_datum(wert):
    try:
        return bool(re.match(r"^20\d{2}-\d{2}-\d{2}$", str(wert))) and bool(date.fromisoformat(str(wert)))
    except ValueError:
        return False


def einreichung_bauen(roh):
    """Keeps only the fields of the format and checks it like the server. Returns (data, dropped, errors)."""
    fehler, entfernt = [], []
    if not isinstance(roh, dict):
        return {}, [], ["Die Datei muss ein JSON-Objekt enthalten"]
    e = {}
    for k, v in roh.items():
        if k in FORMAT:
            if not isinstance(v, dict):
                fehler.append(f"{k} muss ein Objekt sein")
                continue
            e[k] = {f: w for f, w in v.items() if f in FORMAT[k]}
            entfernt += [f"{k}.{f}" for f in v if f not in FORMAT[k]]
        elif k in FORMAT_LISTEN:
            if not isinstance(v, list):
                fehler.append(f"{k} muss eine Liste sein")
                continue
            e[k] = []
            for i, x in enumerate(v):
                if not isinstance(x, dict):
                    fehler.append(f"{k}[{i}] muss ein Objekt sein")
                    continue
                e[k].append({f: w for f, w in x.items() if f in FORMAT_LISTEN[k]})
                entfernt += [f"{k}[{i}].{f}" for f in x if f not in FORMAT_LISTEN[k]]
        elif k in FORMAT_WERTE:
            e[k] = v
        else:
            entfernt.append(k)

    e.setdefault("nutzungsbedingungen_version", NUTZUNGSBEDINGUNGEN_VERSION)
    e.setdefault("client", CLIENT)
    ein = e.setdefault("einwilligung", {})
    ein.setdefault("dokumente", False)   # documents are not uploaded by this script
    ein.setdefault("kontakt", False)
    if not isinstance(ein["dokumente"], bool) or not isinstance(ein["kontakt"], bool):
        fehler.append("einwilligung.dokumente und einwilligung.kontakt müssen true oder false sein")
    lead = e.get("lead") or {}
    if ein.get("kontakt") is not True:   # contact data only with consent
        for f in LEAD_KONTAKT:
            if f in lead:
                del lead[f]
                entfernt.append(f"lead.{f} (ohne einwilligung.kontakt)")

    if not str(lead.get("firma") or "").strip():
        fehler.append("lead.firma fehlt (Firma des abgemahnten Unternehmens)")
    eigen = norm_domain(lead.get("domain"))
    if not RE_DOMAIN.match(eigen):
        fehler.append("lead.domain fehlt oder ist ungültig (Domain des abgemahnten Unternehmens)")
    abm = e.get("abmahner") or {}
    if not str(abm.get("firma") or "").strip():
        fehler.append("abmahner.firma fehlt")
    domains = abm.get("domains")
    if not isinstance(domains, list):
        fehler.append("abmahner.domains muss eine Liste sein")
        domains = []
    eindeutig = []
    for roh_d in domains:
        d = norm_domain(roh_d)
        if not RE_DOMAIN.match(d):
            fehler.append(f"abmahner.domains: ungültige Domain {roh_d}")
        elif eigen and d == eigen:
            fehler.append("Die eigene Domain kann nicht als Domain des Abmahners angegeben werden")
        elif d not in eindeutig:
            eindeutig.append(d)
    if len(eindeutig) > MAX_DOMAINS:
        fehler.append(f"höchstens {MAX_DOMAINS} Domains des Abmahners")
    kanzlei = norm_domain((e.get("kanzlei") or {}).get("domain"))
    if kanzlei and not RE_DOMAIN.match(kanzlei):
        fehler.append("kanzlei.domain ist ungültig")
    for f in DATUMSFELDER:
        w = (e.get("fall") or {}).get(f)
        if w is not None and not _gueltiges_datum(w):
            fehler.append(f"fall.{f} muss ein Datum im Format JJJJ-MM-TT sein")
    if len(json.dumps(e, ensure_ascii=False).encode("utf-8")) > MAX_EINREICHUNG:
        fehler.append("Die Angaben sind zu groß (höchstens 200 KB)")
    return e, entfernt, fehler


def antwort_ausgeben(r):
    hinweis = r.get("hinweis") or KEINE_RECHTSBERATUNG
    print(r.get("titel") or "So würden wir damit umgehen")
    print("=" * len(r.get("titel") or "So würden wir damit umgehen"))
    print(hinweis)
    fristen = r.get("fristen") or []
    if fristen:
        print("\nFristen laut Abmahnung:")
        for f in fristen:
            print(f"  {f.get('frist')}: {f.get('datum')}")
    print()
    for i, s in enumerate(r.get("schritte") or [], 1):
        print(f"{i}. {s.get('thema')}: {s.get('vorgehen')}")
    if r.get("einreichung"):
        print(f"\nGespeichert als Einreichung {r['einreichung']} (für die Meldung: --einreichung {r['einreichung']}).")
    print("\n" + hinweis)


def cmd_check(a):
    try:
        with open(a.datei, encoding="utf-8-sig") as f:
            roh = json.load(f)
    except (OSError, ValueError) as e:
        print(f"Datei nicht lesbar: {e}")
        return 2
    e, entfernt, fehler = einreichung_bauen(roh)
    if fehler:
        print("Abmahnungs-Check nicht möglich:\n  - " + "\n  - ".join(fehler))
        return 2
    if entfernt:
        # with --json stdout carries only the JSON answer
        print("Nicht übermittelt (nicht Teil des Formats oder ohne Einwilligung): " + ", ".join(entfernt),
              file=sys.stderr if a.json and not a.dry_run else sys.stdout)
    if a.dry_run:
        print("Trockenlauf, nichts gesendet. Diese Angaben würden an den Server von "
              f"{ABSENDER} gehen und dort gespeichert:\n" + json.dumps(e, ensure_ascii=False, indent=1))
        return 0
    if not a.json:
        print(f"Die Angaben zur Abmahnung gehen an den Server von {ABSENDER} und werden dort gespeichert.\n")
    try:
        r = lizenz.abmahnung_pruefen(e)
    except lizenz.ServerFehler as err:
        return server_fehler(err, was="Der Abmahnungs-Check")
    r.setdefault("hinweis", KEINE_RECHTSBERATUNG)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
    else:
        antwort_ausgeben(r)
    return 0


# ---------------------------------------------------------------- melden (free)

def baue_meldung(a):
    fehler, domains = [], []
    for roh in a.domains:
        for teil in re.split(r"[\s,;]+", roh):
            if not teil:
                continue
            if "@" in teil:
                fehler.append(f"„{teil}“ ist eine E-Mail-Adresse, nur Domains melden (z. B. {norm_domain(teil)})")
                continue
            d = norm_domain(teil)
            if not RE_DOMAIN.match(d):
                fehler.append(f"ungültige Domain: {teil}")
            elif geschuetzt(d):
                fehler.append(f"{d} ist geschützt (Freemail/Plattform/Behörde), nie melden")
            elif d not in domains:
                domains.append(d)
    if not domains:
        fehler.append("keine meldefähige Domain")
    if len(domains) > MAX_DOMAINS:
        fehler.append(f"höchstens {MAX_DOMAINS} Domains je Meldung")

    kanzlei = ""
    if a.kanzlei_domain:
        if "@" in a.kanzlei_domain:
            fehler.append("Kanzlei: nur die Domain, keine E-Mail-Adresse")
        kanzlei = norm_domain(a.kanzlei_domain)
        if not RE_DOMAIN.match(kanzlei):
            fehler.append("Kanzlei-Domain ungültig")
        elif geschuetzt(kanzlei):
            kanzlei = ""   # law firm with a freemail address: leave it out
        elif kanzlei in domains:
            fehler.append("Die Kanzlei gehört nur in --kanzlei-domain, nicht zu den Domains des Abmahners")
    melder = norm_domain(a.melder_domain)
    if "@" in (a.melder_domain or "") or not RE_DOMAIN.match(melder):
        fehler.append("--melder-domain (Domain des eigenen Unternehmens) fehlt oder ungültig")
    elif any(verwandt(melder, d) for d in domains):
        fehler.append("Die eigene Domain kann nicht gemeldet werden")
    monat = a.monat or ""
    if not RE_MONAT.match(monat):
        fehler.append("--monat muss JJJJ-MM sein")
    elif not ("2015-01" <= monat <= date.today().strftime("%Y-%m")):
        fehler.append("--monat liegt in der Zukunft oder vor 2015")
    vorgehen = [v.strip().upper() for v in (a.vorgehen or "").split(",") if v.strip()]
    for v in vorgehen:
        if v not in VORGEHEN:
            fehler.append(f"unbekannter Vorgehen-Code {v} (erlaubt: {', '.join(VORGEHEN)})")
    einreichung = (a.einreichung or "").strip().lower()
    if einreichung and not RE_UUID.match(einreichung):
        fehler.append("--einreichung muss die Nummer aus dem Abmahnungs-Check sein")

    stufe = a.stufe or (5 if kanzlei or a.kanzlei_domain else 4)
    beleg = a.beleg_art or ("gerichtsdokument" if stufe == 6 else "abmahnschreiben" if stufe >= 4 else "keiner")
    m = {"domains": domains, "stufe": stufe, "monat": monat, "melder_domain": melder, "forderung": a.forderung,
         "art82": a.art82 == "ja", "ausgang": a.status, "vorgehen": vorgehen, "beleg_art": beleg}
    if kanzlei:
        m["kanzlei_domain"] = kanzlei
    if einreichung:
        m["einreichung"] = einreichung
    return m, fehler


def zusammenfassung(m):
    teile = [f"Domains: {', '.join(m['domains'])}"]
    if m.get("kanzlei_domain"):
        teile.append(f"Kanzlei-Domain: {m['kanzlei_domain']}")
    teile.append(f"Stufe {m['stufe']} ({STUFEN[m['stufe']]}), Monat {m['monat']}, Forderung {m['forderung']} €, "
                 f"Art. 82 gefordert: {'ja' if m['art82'] else 'nein'}")
    teile.append(f"Vorgehen: {', '.join(m['vorgehen']) or '–'}, Ausgang: {m['ausgang']}, Beleg: {m['beleg_art']}")
    teile.append(f"Eigene Domain {m['melder_domain']}: nur als nicht umkehrbarer Schlüssel gespeichert, "
                 "damit unabhängige Meldungen gezählt werden können")
    return "\n  ".join(teile)


def cmd_melden(a):
    m, fehler = baue_meldung(a)
    if fehler:
        print("Meldung nicht möglich:\n  - " + "\n  - ".join(fehler))
        return 2
    print(f"Meldung an den Server von {ABSENDER} (nicht öffentlich):\n  " + zusammenfassung(m))
    if a.dry_run:
        print("\nTrockenlauf, nichts gesendet. Nutzlast:\n"
              + json.dumps({**m, "quelle": "abmahnungs_check"}, ensure_ascii=False, indent=1))
        return 0
    try:
        r = lizenz.melden(m, quelle="abmahnungs_check")
    except lizenz.ServerFehler as e:
        return server_fehler(e, was="Die Meldung")
    print(f"\nGesendet. Meldungs-Nr. {r.get('meldung', '?')}.")
    return 0


# ---------------------------------------------------------------- pruefen (subscription)

def cmd_pruefen(a):
    domains = []
    for roh in a.domain:
        d = norm_domain(roh)
        if not RE_DOMAIN.match(d):
            print(f"Ungültige Domain: {roh}")
            return 2
        if d not in domains:
            domains.append(d)
    kanzlei = norm_domain(a.kanzlei_domain) if a.kanzlei_domain else ""
    if a.kanzlei_domain and not RE_DOMAIN.match(kanzlei):
        print(f"Ungültige Kanzlei-Domain: {a.kanzlei_domain}")
        return 2
    code = abo_vorhanden()
    if code is not None:
        return code
    try:
        s = lizenz.abgleichen(domains + ([kanzlei] if kanzlei else []), warnen_ab=1)
    except lizenz.ServerFehler as e:
        return server_fehler(e, was="Der Abgleich")

    def eintrag(d):
        e = s.ergebnisse.get(d)
        return {"bekannt": bool(e), "empfehlung": (e or {}).get("empfehlung", "frei"),
                "beschreibung": lizenz._beschreibung(e) if e else None,
                **({"stufe": e["stufe"]} if e and e.get("stufe") else {})}

    ergebnis = {"domains": {d: eintrag(d) for d in domains}, "kanzlei": {kanzlei: eintrag(kanzlei)} if kanzlei else {},
                "quelle": s.quelle}
    if a.json:
        print(json.dumps(ergebnis, ensure_ascii=False, indent=1))
        return 0
    print(s.quelle)
    for titel, teil in (("Abmahner", ergebnis["domains"]), ("Kanzlei", ergebnis["kanzlei"])):
        for d, info in teil.items():
            if info["bekannt"]:
                print(f"  {titel:<9} BEKANNT   {d}: {info['beschreibung']} → {info['empfehlung']}")
            else:
                print(f"  {titel:<9} unbekannt {d}")
    if kanzlei:
        print("Ob die Kanzlei als echt bekannt ist, zeigt der kostenlose Abmahnungs-Check (check).")
    print("\nHinweis: Erfahrungswerte aus Meldungen, nicht im Einzelfall geprüft. Keine Prognose, "
          "keine Aussage darüber, ob eine Abmahnung berechtigt war.")
    return 0


# ---------------------------------------------------------------- abgleich (subscription)

def lies_csv(pfad):
    with open(pfad, encoding="utf-8-sig", newline="") as f:
        probe = f.read(16384)
        f.seek(0)
        try:
            trenner = csv.Sniffer().sniff(probe, delimiters=",;\t").delimiter
        except csv.Error:
            trenner = ","
        r = csv.DictReader(f, delimiter=trenner)
        return list(r.fieldnames or []), list(r), trenner


def schreibe(name, felder, daten, trenner):
    with open(name + ".tmp", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=felder, delimiter=trenner, extrasaction="ignore")
        w.writeheader()
        w.writerows(daten)
    os.replace(name + ".tmp", name)   # never leave a truncated list behind


def cmd_abgleich(a):
    try:
        felder, zeilen, trenner = lies_csv(a.kontakte)
    except OSError as e:
        print(f"Datei nicht lesbar: {e}")
        return 2
    spalte = a.spalte
    if spalte not in felder:
        kandidaten = [f for f in felder if f and f.strip().lower() in
                      ("email", "e-mail", "mail", "website", "domain", "url", "webseite")]
        if not kandidaten:
            print(f"Spalte „{spalte}“ nicht gefunden. Vorhanden: {', '.join(felder)}")
            return 2
        spalte = kandidaten[0]
        print(f"Verwende Spalte „{spalte}“.")
    code = abo_vorhanden()   # in the free plan no contact leaves the computer
    if code is not None:
        return code
    try:
        s = lizenz.abgleichen([z.get(spalte) for z in zeilen if z.get(spalte)])
    except lizenz.ServerFehler as e:
        return server_fehler(e, was="Der Abgleich")

    gesperrt, frei, gewarnt = [], [], 0
    for z in zeilen:
        grund = s.treffer(z.get(spalte))
        if grund:
            gesperrt.append({**z, "Sperrgrund": grund})
            continue
        hinweis = s.warnung(z.get(spalte))
        gewarnt += bool(hinweis)
        frei.append({**z, "Sperrliste Hinweis": hinweis or ""})
    praefix = a.out_praefix or os.path.splitext(a.kontakte)[0]
    schreibe(f"{praefix}_gesperrt.csv", felder + ["Sperrgrund"], gesperrt, trenner)
    schreibe(f"{praefix}_bereinigt.csv", felder + ["Sperrliste Hinweis"], frei, trenner)
    print(s.quelle)
    print(f"{len(zeilen)} Kontakte geprüft: {len(gesperrt)} gesperrt, {len(frei)} frei (davon {gewarnt} mit Hinweis).")
    print(f"  {praefix}_bereinigt.csv  → für den Versand verwenden")
    print(f"  {praefix}_gesperrt.csv   → nicht anschreiben")
    return 0


# ---------------------------------------------------------------- CLI

FORMAT_HILFE = """Format der JSON-Datei (Pflicht: lead.firma, lead.domain, abmahner.firma, abmahner.domains):
  {"lead":        {"firma": "Muster Vertrieb GmbH", "domain": "muster-vertrieb.example", "rechtsform": "GmbH"},
   "abmahner":    {"firma": "Beispiel Immobilien GmbH", "domains": ["beispiel-immobilien.example"]},
   "kanzlei":     {"name": "Kanzlei Exempel", "domain": "kanzlei-exempel.example"},
   "fall":        {"abmahnung_datum": "2026-09-28", "zugang_datum": "2026-09-30", "frist_ue": "2026-10-07",
                   "frist_zahlung": "2026-10-14", "frist_auskunft": null},
   "forderungen": {"gegenstandswert": 6000, "kosten_gesamt": 664.26, "art82_gefordert": true,
                   "art82_betrag": 500, "auskunft_gefordert": true},
   "ue_entwurf":  {"zahlungspflichten": true, "vertragsstrafe_modell": "fest"},
   "mails":       [{"gesendet_am": "2026-09-15T09:12:00+02:00", "adresstyp": "funktion", "art": "angebot"}],
   "einwilligung": {"dokumente": false, "kontakt": false}}
Datumsangaben JJJJ-MM-TT. Felder außerhalb des Formats werden nicht übermittelt, Kontaktdaten (lead.kontakt_*)
nur mit "einwilligung": {"kontakt": true}. Vollständig: references/06_sperrliste-server.md."""


def main(argv=None):
    for strom in (sys.stdout, sys.stderr):   # Windows with redirected output: never crash on a character
        try:
            strom.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    p = argparse.ArgumentParser(description=f"Abmahnungs-Check und Sperrliste über den Server von {ABSENDER}",
                                epilog=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("check", help="kostenlos: So würden wir damit umgehen (speichert die Abmahnung)",
                       epilog=FORMAT_HILFE, formatter_class=argparse.RawDescriptionHelpFormatter)
    s.add_argument("--datei", required=True, help="JSON-Datei mit den Angaben zur Abmahnung")
    s.add_argument("--json", action="store_true", help="Antwort als JSON ausgeben")
    s.add_argument("--dry-run", action="store_true", help="nur zeigen, was gesendet würde")

    s = sub.add_parser("melden", help="kostenlos: Domains des Abmahners melden")
    s.add_argument("--domains", nargs="+", required=True)
    s.add_argument("--kanzlei-domain", default="")
    s.add_argument("--monat", required=True, help="Monat der Abmahnung, JJJJ-MM")
    s.add_argument("--stufe", type=int, choices=sorted(STUFEN),
                   help="1 negativ · 2 widerspruch · 3 drohung · 4 abmahnung_selbst · 5 abmahnung_anwalt · "
                        "6 gericht (Standard: 5 mit Kanzlei, sonst 4)")
    s.add_argument("--forderung", choices=FORDERUNG, default="unbekannt")
    s.add_argument("--art82", choices=["ja", "nein"], required=True)
    s.add_argument("--vorgehen", default="", help="Codes mit Komma: " + ", ".join(VORGEHEN))
    s.add_argument("--status", "--ausgang", dest="status", choices=STATUS, default="offen")
    s.add_argument("--beleg-art", choices=BELEG_ART, help="Standard: abmahnschreiben (Stufe 4/5)")
    s.add_argument("--einreichung", help="Nummer aus dem Abmahnungs-Check (verknüpft Meldung und Abmahnung)")
    s.add_argument("--melder-domain", required=True, help="Domain des eigenen Unternehmens")
    s.add_argument("--dry-run", action="store_true", help="nur die Nutzlast zeigen, nichts senden")

    s = sub.add_parser("pruefen", help="Abo: abgestufter Abgleich der Domains des Abmahners")
    s.add_argument("--domain", nargs="+", required=True)
    s.add_argument("--kanzlei-domain")
    s.add_argument("--json", action="store_true")

    s = sub.add_parser("abgleich", help="Abo: Kontaktliste abgleichen (_gesperrt.csv, _bereinigt.csv)")
    s.add_argument("--kontakte", required=True)
    s.add_argument("--spalte", default="email")
    s.add_argument("--out-praefix")

    a = p.parse_args(argv)
    return {"check": cmd_check, "melden": cmd_melden, "pruefen": cmd_pruefen, "abgleich": cmd_abgleich}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
