# Sperrliste und Abmahnungs-Check (Server von Agentur Consulting)

Es gibt **keine öffentliche Liste**. Abmahnungen, Meldungen und die Sperrliste liegen nur auf dem Server von Agentur Consulting. Sie werden nie ausgegeben: Nutzer und Partner erhalten nur das Ergebnis des Abgleichs für selbst geprüfte Einträge. Kein Download der Liste, kein GitHub, kein Relay, kein Formular-Link.

| Was | Befehl | Kosten | Phase |
|---|---|---|---|
| Abmahnungs-Check „So würden wir damit umgehen“ | `sperrliste.py check --datei abmahnung.json` | kostenlos | 1b |
| Meldung des Abmahners | `sperrliste.py melden …` | kostenlos | 9, 10 |
| Abgestufter Abgleich der Abmahner-Domains | `sperrliste.py pruefen --domain …` | nur mit Abo | 1b |
| Kontaktliste vor einer Kampagne abgleichen | `sperrliste.py abgleich --kontakte …` | nur mit Abo | Hinweise für künftige Kampagnen |

Im Free-Plan antworten `pruefen` und `abgleich` mit „Kostenpflichtige Features können im Free-Plan nicht verwendet werden“ (Exit-Code 5). Dann wird nichts übermittelt und keine Datei geschrieben. `check` und `melden` funktionieren weiter.

## Technik

- Skript: `scripts/sperrliste.py`, nutzt `scripts/lizenz.py` (gleiche Datei wie im Lead-Scraper). Nur Python-Standardbibliothek.
- Server: `https://leads-db.akconsulting.cloud/functions/v1`. Die Umgebung muss diesen Host erreichen dürfen.
- **Lizenzschlüssel:** Beim ersten Aufruf legt `lizenz.py` automatisch einen kostenlosen Schlüssel an und speichert ihn nur für den Benutzer lesbar unter `~/.config/akquise-und-abmahnschutz/lizenz` (Windows: `%APPDATA%\akquise-und-abmahnschutz\lizenz`). Die Umgebungsvariable `LIZENZ_SCHLUESSEL` hat Vorrang (z. B. für einen Abo- oder Partner-Schlüssel). Der Schlüssel wird nie angezeigt, nie in Dateien des Falls geschrieben und nie in den Chat kopiert.
- Abo ansehen oder verwalten: `python3 scripts/lizenz.py abo`. Status: `python3 scripts/lizenz.py status`.
- Ohne Code-Ausführung gibt es keinen Weg zum Server. Check, Abgleich und Meldung entfallen dann; kurz sagen und normal weitermachen.

Exit-Codes: 0 ok · 1 Fehler · 2 Eingabe ungültig (nichts gesendet) · 3 vom Server abgelehnt · 4 Server nicht erreichbar (später erneut versuchen) · 5 Free-Plan.

## Abmahnungs-Check (kostenlos)

```bash
python3 scripts/sperrliste.py check --datei arbeit/abmahnung.json            # Antwort lesbar
python3 scripts/sperrliste.py check --datei arbeit/abmahnung.json --dry-run  # nur zeigen, was gesendet würde
```

- **Vor dem Senden** dem Nutzer sagen: Die Angaben zur Abmahnung gehen an den Server von Agentur Consulting und werden dort gespeichert. Widerspricht er, nicht senden.
- Der Server speichert jede Abmahnung und antwortet mit „So würden wir damit umgehen“: Fristen, Schritte, Echtheit der Kanzlei (soweit bekannt) und immer dem festen Hinweis „Keine Rechtsberatung: …“. Diesen Hinweis dem Nutzer unverändert mitgeben.
- Die Antwort ist eine allgemeine Beschreibung, keine Empfehlung für den Einzelfall. Die Prüfung in Phase 2 bis 7 ersetzt sie nicht.
- Die Ausgabe nennt die Nummer der Einreichung. Sie kann der Meldung mit `--einreichung` mitgegeben werden.

### Format der Datei

JSON-Objekt. Pflicht sind `lead.firma`, `lead.domain`, `abmahner.firma` und `abmahner.domains`. Felder, die hier nicht stehen, sendet das Skript nicht. `nutzungsbedingungen_version` (Standard `2026-11`), `client` und `einwilligung` (Standard: beides `false`) setzt das Skript selbst, wenn sie fehlen. Datumsangaben `JJJJ-MM-TT`, Beträge als Zahl in Euro.

```json
{
  "lead":        {"firma": "Muster Vertrieb GmbH", "rechtsform": "GmbH", "kaufmann": true,
                  "domain": "muster-vertrieb.example"},
  "abmahner":    {"firma": "Beispiel Immobilien GmbH", "rechtsform": "GmbH", "branche": "Immobilien",
                  "ort": "Musterstadt", "website": "https://beispiel-immobilien.example",
                  "domains": ["beispiel-immobilien.example", "beispiel-immo.example"]},
  "kanzlei":     {"name": "Kanzlei Exempel", "ort": "Musterstadt", "domain": "kanzlei-exempel.example",
                  "telefon": "+49 000 000000", "website": "https://kanzlei-exempel.example"},
  "fall":        {"aktenzeichen": "123/26", "abmahnung_datum": "2026-09-28", "zugang_datum": "2026-09-30",
                  "frist_ue": "2026-10-07", "frist_zahlung": "2026-10-14", "frist_auskunft": null,
                  "absender_domain": "muster-vertrieb.example", "mitbewerber": false},
  "mails":       [{"gesendet_am": "2026-09-15T09:12:00+02:00", "adresstyp": "funktion", "art": "angebot",
                   "tracking_oder_videolink": false, "kopie_liegt_bei": true}],
  "forderungen": {"unterlassung": true, "gegenstandswert": 6000, "gebuehrensatz": 1.3, "geschaeftsgebuehr": 538.2,
                  "pauschale": 20, "ust_betrag": 106.06, "kosten_gesamt": 664.26, "art82_gefordert": true, "art82_betrag": 500,
                  "art82_schaden_dargelegt": false, "auskunft_gefordert": true},
  "ue_entwurf":  {"liegt_bei": true, "zahlungspflichten": true, "vertragsstrafe_modell": "fest",
                  "vertragsstrafe_betrag": 5100, "reichweite": "alle_adressen", "oder_falle": true},
  "zitate":      [{"gericht": "BGH", "aktenzeichen": "VI ZR 109/23", "datum": "2025-01-28"}],
  "pruefung":    {"einstufung": "B", "warnzeichen": ["ART82_PAUSCHAL", "UE_ZAHLUNGSPFLICHT"]},
  "einwilligung": {"dokumente": false, "kontakt": false}
}
```

| Bereich | Felder |
|---|---|
| `lead` (abgemahntes Unternehmen) | firma*, domain*, rechtsform, kaufmann, strasse, plz, ort, website; kontakt_name, kontakt_email, kontakt_telefon nur mit `einwilligung.kontakt: true` (sonst entfernt das Skript sie) |
| `abmahner` | firma*, domains* (Liste, höchstens 15, nicht die eigene Domain), ist_person, rechtsform, strasse, plz, ort, registergericht, registernummer, branche, website |
| `kanzlei` | name, domain, rechtsform, strasse, plz, ort, telefon, website, iban |
| `fall` | aktenzeichen, abmahnung_datum, zugang_datum, frist_ue, frist_zahlung, frist_auskunft, absender_domain, beworbene_marke, mitbewerber |
| `mails` (Liste) | gesendet_am, adresstyp (persoenlich · funktion · unbekannt), art (angebot · kooperation · newsletter · sonstige), betreff, tracking_oder_videolink, kopie_liegt_bei |
| `forderungen` | unterlassung, gegenstandswert, gebuehrensatz, geschaeftsgebuehr, pauschale, ust_betrag, kosten_gesamt, art82_gefordert, art82_betrag, art82_schaden_dargelegt, auskunft_gefordert |
| `ue_entwurf` | liegt_bei, zahlungspflichten, vertragsstrafe_modell (hamburger_brauch · fest · keine), vertragsstrafe_betrag, reichweite (eine_adresse · alle_adressen), oder_falle, ohne_anerkennung, aufloesende_bedingung, erstreckung_dritte |
| `zitate` (Liste) | gericht, aktenzeichen, datum |
| `pruefung` | einstufung (A · B · C · D), warnzeichen (Codes wie KANZLEI_NICHT_VERIFIZIERBAR, BRIEFKOPF_ABWEICHUNG, ART82_PAUSCHAL, UE_ZAHLUNGSPFLICHT, GEGENSTANDSWERT_UEBERHOEHT, RECHENFEHLER, MAILKOPIE_FEHLT, FEHLZITAT) |
| `vorgehen` (später, Phase 10) | ue_vorgehen (modifiziert · original · verweigert), ue_abgegeben_am, kostenposition (voll · teil · nachweis · abgelehnt · vergleich), art82_position (abgelehnt · gezahlt), auskunft_erteilt_am, website_block, anwalt_beauftragt, antwort_versandt_am, gezahlter_betrag |
| oben | einwilligung.dokumente, einwilligung.kontakt (true/false), nutzungsbedingungen_version, client, status |

\* Pflicht

### Datensparsamkeit

Nur ausfüllen, was der Server für „So würden wir damit umgehen“ und für die Einordnung der Abmahnung braucht. Standard ist die Beispieldatei oben.

- **Weglassen**, auch wenn das Format sie kennt: Namen natürlicher Personen (Ansprechpartner, Geschäftsführer, Anwälte: `vertreter`, `anwalt`, `kontakt_name`, `absender_name`, `ziel_name`), E-Mail-Adressen (`absender_adresse`, `ziel_adresse`, `kanzlei.email`), Mail-Inhalte (`inhalt`), Freitexte (`weitere`, `auffaelligkeiten`, `behauptete_aussage`), Telefonnummern von Personen.
- Ist der Abmahner eine natürliche Person (Einzelunternehmer), `abmahner.firma` so angeben, wie es im Briefkopf steht, `ist_person: true`, und keine Privatanschrift.
- `einwilligung.kontakt: true` nur, wenn der Nutzer ausdrücklich zustimmt, dass Agentur Consulting ihn zu dem Fall kontaktieren darf. Dann und nur dann die Kontaktfelder des Leads ausfüllen.
- `einwilligung.dokumente` bleibt `false`: Das Skript lädt keine Dokumente hoch.
- Die Datei im Arbeitsordner des Falls ablegen, nicht im Skill-Ordner.

## Abgestufter Abgleich (nur mit Abo)

```bash
python3 scripts/sperrliste.py pruefen --domain abmahner.de abmahner-shop.de --kanzlei-domain kanzlei.de
```

- Je Domain: bekannt oder unbekannt, die höchste Stufe und das Ergebnis `sperren` (ab Stufe 3, `SPERREN_AB`) oder `warnen`. Mehr gibt der Server nicht heraus: keine Anzahl, kein Datum, kein Status, keine Melder. Die Kanzlei-Domain wird mitgeprüft. Ob die Kanzlei als echt bekannt ist, zeigt der kostenlose Check.
- Ergebnisse immer als **Erfahrungswerte aus Meldungen** kennzeichnen, nicht im Einzelfall geprüft, keine Prognose.
- Die Erkenntnisse nie im Antwortschreiben erwähnen (siehe `05_fallstricke.md`).
- Im Free-Plan: den Hinweis zeigen, nicht drängen, normal weitermachen.

**Stufen:** 1 negativ (starke Ablehnung) · 2 widerspruch (förmlicher Widerspruch) · 3 drohung (Drohung mit rechtlichen Schritten) · 4 abmahnung_selbst (Abmahnung durch die Firma selbst) · 5 abmahnung_anwalt (Abmahnung durch eine Kanzlei) · 6 gericht (Mahnbescheid, einstweilige Verfügung, Klage).

## Kontaktliste abgleichen (nur mit Abo)

```bash
python3 scripts/sperrliste.py abgleich --kontakte kontakte.csv --spalte email
```

- Schreibt `<präfix>_gesperrt.csv` (Spalte „Sperrgrund“, z. B. „Stufe 5 (abmahnung_anwalt), 2× gemeldet, zuletzt 2026-09-01“) und `<präfix>_bereinigt.csv` (Spalte „Sperrliste Hinweis“ für bekannte, schwächere Fälle). Weitere Dateien entstehen nicht.
- An den Server gehen nur die Werte der gewählten Spalte (E-Mail-Adressen bleiben Adressen, alles andere wird zur Domain), nur mit Abo und nur zum Abgleich. Im Free-Plan verlässt keine Zeile den Rechner.

## Meldung (kostenlos, nach Zustimmung)

```bash
python3 scripts/sperrliste.py melden --domains abmahner.de abmahner-shop.de --kanzlei-domain kanzlei.de \
  --monat 2026-09 --forderung 1000-2000 --art82 ja --vorgehen UE_MODIFIZIERT,ART82_ABGELEHNT \
  --status offen --melder-domain eigene-firma.de [--stufe 5] [--einreichung NR] [--dry-run]
```

| Option | Feld | Werte |
|---|---|---|
| `--domains` | domains | alle belegbar zugehörigen Domains des Abmahners, höchstens 15; jede muss im DNS existieren |
| `--kanzlei-domain` | kanzlei_domain | Domain der Kanzlei; bei Freemail entfällt sie |
| `--stufe` | stufe | 1–6 (siehe oben). Standard: 5 mit Kanzlei, sonst 4 |
| `--monat` | monat | Monat der Abmahnung, `JJJJ-MM`, nicht in der Zukunft |
| `--forderung` | forderung | 0 · 1-500 · 500-1000 · 1000-2000 · 2000-5000 · >5000 · unbekannt |
| `--art82` | art82 | ja / nein |
| `--vorgehen` | vorgehen | UE_MODIFIZIERT · UE_ORIGINAL · UE_VERWEIGERT · ART82_ABGELEHNT · ART82_GEZAHLT · KOSTEN_ABGELEHNT · KOSTEN_GEZAHLT · KOSTEN_VERGLEICH · AUSKUNFT_ERTEILT · WEBSITE_BLOCK · ANWALT_BEAUFTRAGT |
| `--status` (oder `--ausgang`) | ausgang | offen · keine_reaktion · erledigt_ohne_zahlung · erledigt_mit_zahlung · vergleich · mahnbescheid · klage · unbekannt |
| `--beleg-art` | beleg_art | abmahnschreiben (Standard bei Stufe 4/5) · anwaltsschreiben · email_antwort · brief · gerichtsdokument (Standard bei Stufe 6) · sonstiges · keiner |
| `--einreichung` | einreichung | Nummer aus dem Abmahnungs-Check |
| `--melder-domain` | melder_domain | eigene Domain; gespeichert wird nur ein nicht umkehrbarer Schlüssel daraus, um unabhängige Meldungen zu zählen |

Das Skript sendet mit `quelle: abmahnungs_check`. Es prüft vorher lokal: Domainformat, keine „@“, keine Freemail- oder Plattformdomain, nicht die eigene Domain, Kanzlei nicht als Abmahner, bekannte Codes, Monat. Der Server prüft zusätzlich DNS, seine vollständige Schutzliste, Widersprüche und Höchstgrenzen je Stunde.

- **Nie in der Meldung:** E-Mail-Adressen, Namen, Aktenzeichen, Anschriften, exakte Beträge, Freitexte, Wertungen.
- **Server nicht erreichbar** (Exit-Code 4): dem Nutzer sagen, dass die Meldung nicht gesendet wurde, und später erneut versuchen. Es gibt keinen Ersatzweg.
- **Ausgang nachmelden** (Phase 10): dieselben Domains mit demselben `--monat` und derselben `--stufe` und neuem `--status` erneut melden. Der Server aktualisiert den Vorfall dieses Melders. Kommt es zum Mahnbescheid oder zur Klage, zusätzlich mit `--stufe 6` melden.

## Zugehörige Domains ermitteln (Phase 1)

| Quelle | Vorgehen |
|---|---|
| Zieladresse der beanstandeten Mail | Domain hinter dem „@“ (außer Freemail) |
| Abmahnschreiben | Domains im Briefkopf, in der Signatur und in der Mail-Kopie |
| Website des Abmahners | Impressum (weitere Marken, Shops, Landingpages), Footer-Links, `curl -sIL https://domain` für Weiterleitungen |
| Handelsregister / Northdata | weitere Firmen derselben Person. Nur aufnehmen, wenn dieselbe Anschrift **und** dasselbe Geschäft vorliegen. |

Nur aufnehmen, was belegbar demselben Abmahner gehört. Im Zweifel weglassen: Eine falsche Domain sperrt ein unbeteiligtes Unternehmen.

**Nie melden:**

- Freemail-Anbieter (gmail.com, web.de, gmx.de, t-online.de …)
- Hosting- und Shop-Plattformen (myshopify.com, wixsite.com, jimdosite.com, github.io …)
- Portale (immobilienscout24.de …)
- Behörden
- die Kanzlei als Abmahner
- die eigene Domain

## Datenschutz und Haftung

- Alles liegt nur auf dem Server von Agentur Consulting. Es gibt keine öffentliche Liste und keinen Download.
- Domains von Unternehmen sind meist keine personenbezogenen Daten. Ausnahme: Einzelunternehmer mit Namensdomain (z. B. `max-mustermann.de`).
- Ein Eintrag sagt nichts darüber aus, ob eine Abmahnung berechtigt war.
- Der Meldende ist für die Richtigkeit verantwortlich. Bewusst falsche Meldungen, etwa über Wettbewerber, sind unzulässig.
- Keine Rechtsberatung: Check und Abgleich liefern allgemeine Beschreibungen und Erfahrungswerte. Sie ersetzen keine anwaltliche Prüfung des Einzelfalls.
