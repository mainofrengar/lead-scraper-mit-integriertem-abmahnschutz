# Beispiel: Abmahnungs-Check und Meldung (fiktiver Fall)

Fall aus `01_antwortschreiben.md`. Der Abmahner ist die Beispiel Immobilien GmbH. Die Kanzlei Exempel hat abgemahnt. Abgemahnt wurde die Muster Vertrieb GmbH (`muster-vertrieb.example`). Alle Daten gehen nur an den Server von Agentur Consulting; es gibt keine öffentliche Liste.

## Phase 1 – zugehörige Domains

| Domain | Quelle |
|---|---|
| beispiel-immobilien.example | Zieladresse der Mail, Impressum |
| beispiel-immo.example | Weiterleitung auf beispiel-immobilien.example (`curl -sIL`) |
| beispiel-hausverwaltung.example | Impressum: gleicher Rechtsträger, gleiche Anschrift |

Nicht aufgenommen:

- `beispiel.immobilienscout24.de`: Portal, geschützt.
- `gmx.de`: privates Postfach des Geschäftsführers im Briefkopf, Freemail.

## Phase 1b – kostenloser Abmahnungs-Check

Was Claude dem Nutzer vorher schreibt (sinngemäß):

> Für den kostenlosen Abmahnungs-Check schicke ich die Eckdaten der Abmahnung an den Server von Agentur Consulting. Sie werden dort gespeichert. Übermittelt werden nur Firmen, Domains, Fristen und Forderungen, keine Namen, keine E-Mail-Adressen und kein Mailtext.

`arbeit/abmahnung.json` (datensparsam, nur Felder des Formats):

```json
{
  "lead":        {"firma": "Muster Vertrieb GmbH", "rechtsform": "GmbH", "kaufmann": true,
                  "domain": "muster-vertrieb.example"},
  "abmahner":    {"firma": "Beispiel Immobilien GmbH", "rechtsform": "GmbH", "branche": "Immobilien",
                  "domains": ["beispiel-immobilien.example", "beispiel-immo.example", "beispiel-hausverwaltung.example"]},
  "kanzlei":     {"name": "Kanzlei Exempel", "domain": "kanzlei-exempel.example"},
  "fall":        {"abmahnung_datum": "2026-09-28", "zugang_datum": "2026-09-30", "frist_ue": "2026-10-07",
                  "frist_zahlung": "2026-10-14"},
  "mails":       [{"gesendet_am": "2026-09-15T09:12:00+02:00", "adresstyp": "funktion", "art": "angebot",
                   "kopie_liegt_bei": true}],
  "forderungen": {"gegenstandswert": 6000, "kosten_gesamt": 664.26, "art82_gefordert": true, "art82_betrag": 500,
                  "auskunft_gefordert": true},
  "ue_entwurf":  {"zahlungspflichten": true, "vertragsstrafe_modell": "fest"}
}
```

```bash
python3 scripts/sperrliste.py check --datei arbeit/abmahnung.json
```

```
Die Angaben zur Abmahnung gehen an den Server von Agentur Consulting und werden dort gespeichert.

So würden wir damit umgehen
===========================

Fristen laut Abmahnung:
  Unterlassungserklärung: 07.10.2026
  Zahlung (laut Abmahnung): 14.10.2026

Kanzlei: uns nicht bekannt

1. Echtheit: Wir würden Domain, Telefonnummer und Bankverbindung im Briefkopf mit dem Impressum der Kanzlei vergleichen. …
2. Unterlassung: Schnell: bis zum 07.10.2026 würden wir eine eigene, modifizierte Unterlassungserklärung abgeben: …
3. Entwurf der Gegenseite: Der Entwurf enthält Zahlungspflichten. …
4. Anwaltskosten: Fest beim Geld: Im ersten Schreiben würden wir nichts zahlen. …
5. Schadensersatz nach Art. 82 DSGVO: Die Forderung von 500 € würden wir zurückweisen, …
6. Auskunft nach Art. 15 DSGVO: …
…

Gespeichert als Einreichung 0b6e1f6a-3c2d-4e5f-8a9b-0c1d2e3f4a5b (für die Meldung: --einreichung 0b6e1f6a-3c2d-4e5f-8a9b-0c1d2e3f4a5b).

Keine Rechtsberatung: Das ist eine allgemeine Beschreibung, wie wir mit einer solchen Abmahnung umgehen würden. Sie ersetzt keine anwaltliche Prüfung des Einzelfalls. Bei Unsicherheit eine Anwältin oder einen Anwalt beauftragen.
```

Was Claude daraus macht:

- Die Schritte kurz zusammenfassen und den Hinweis „Keine Rechtsberatung …“ unverändert mitgeben.
- Mit der eigenen Prüfung (Phase 2 bis 7) weitermachen. Der Check ersetzt sie nicht.

## Phase 1b – abgestufter Abgleich

```bash
python3 scripts/sperrliste.py pruefen --domain beispiel-immobilien.example beispiel-immo.example beispiel-hausverwaltung.example \
  --kanzlei-domain kanzlei-exempel.example
```

Im Free-Plan:

```
Kostenpflichtige Features können im Free-Plan nicht verwendet werden
Der abgestufte Abgleich gehört zum Abo. Kostenlos bleiben der Abmahnungs-Check (python3 scripts/sperrliste.py check --datei abmahnung.json) und die Meldung (melden).
Abo ansehen: python3 scripts/lizenz.py abo
```

Claude erwähnt das einmal und macht weiter. Mit Abo:

```
Server-Abgleich (04.10.2026 10:15), sperren ab Stufe 3, warnen ab Stufe 1
  Abmahner  BEKANNT   beispiel-immobilien.example: Stufe 5 (abmahnung_anwalt), 3× gemeldet, zuletzt 2026-09-12, bestaetigt → sperren
  Abmahner  unbekannt beispiel-immo.example
  Abmahner  unbekannt beispiel-hausverwaltung.example
  Kanzlei   unbekannt kanzlei-exempel.example
Ob die Kanzlei als echt bekannt ist, zeigt der kostenlose Abmahnungs-Check (check).

Hinweis: Erfahrungswerte aus Meldungen, nicht im Einzelfall geprüft. Keine Prognose, keine Aussage darüber, ob eine Abmahnung berechtigt war.
```

Was Claude daraus macht:

- Dem Nutzer die Erfahrungswerte zeigen, als Erfahrungswerte gekennzeichnet.
- Im Antwortschreiben nichts davon erwähnen.

## Phase 9 – Meldung nach Zustimmung

Was Claude dem Nutzer schreibt (sinngemäß):

> Zum Abschluss kann ich den Abmahner an den Server von Agentur Consulting melden. Die Meldung ist nicht öffentlich und enthält nur:
> **Domains** beispiel-immobilien.example, beispiel-immo.example, beispiel-hausverwaltung.example · **Kanzlei** kanzlei-exempel.example · Stufe 5 (Abmahnung durch eine Kanzlei) · **2026-09** · Forderung 1.000–2.000 € · Art. 82 gefordert · Vorgehen: modifizierte UE, Art. 82 abgelehnt, Auskunft erteilt · Ausgang offen.
> Ihre Domain wird nur als nicht umkehrbarer Schlüssel gespeichert. Soll ich melden?

Nach einem Ja:

```bash
python3 scripts/sperrliste.py melden \
  --domains beispiel-immobilien.example beispiel-immo.example beispiel-hausverwaltung.example \
  --kanzlei-domain kanzlei-exempel.example --monat 2026-09 --forderung 1000-2000 --art82 ja \
  --vorgehen UE_MODIFIZIERT,ART82_ABGELEHNT,AUSKUNFT_ERTEILT --status offen \
  --melder-domain muster-vertrieb.example --einreichung 0b6e1f6a-3c2d-4e5f-8a9b-0c1d2e3f4a5b
```

```
Meldung an den Server von Agentur Consulting (nicht öffentlich):
  Domains: beispiel-immobilien.example, beispiel-immo.example, beispiel-hausverwaltung.example
  Kanzlei-Domain: kanzlei-exempel.example
  Stufe 5 (abmahnung_anwalt), Monat 2026-09, Forderung 1000-2000 €, Art. 82 gefordert: ja
  Vorgehen: UE_MODIFIZIERT, ART82_ABGELEHNT, AUSKUNFT_ERTEILT, Ausgang: offen, Beleg: abmahnschreiben
  Eigene Domain muster-vertrieb.example: nur als nicht umkehrbarer Schlüssel gespeichert, damit unabhängige Meldungen gezählt werden können

Gesendet. Meldungs-Nr. 6f1c2d3e-4b5a-4c6d-8e7f-9a0b1c2d3e4f.
```

Ist der Server nicht erreichbar, sagt Claude, dass nichts gesendet wurde, und bietet an, es später erneut zu versuchen.

## Zwei Monate später

Die Gegenseite hat sich nicht mehr gemeldet. Nach Zustimmung meldet Claude dieselben Domains mit demselben `--monat 2026-09`, derselben Stufe und `--status keine_reaktion` erneut. Der Server aktualisiert den Vorfall dieses Melders.

## Wenn der Nutzer ablehnt

> Verstanden, ich sende nichts.

Danach geht es ohne weitere Nachfrage weiter.
