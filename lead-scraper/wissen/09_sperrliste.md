# Sperrliste, Lizenz und Datenweitergabe

**Zweck:** wie der Sperrlisten-Abgleich funktioniert, was kostenlos ist und was nur mit Abo, welche Daten an den Server gehen, wie gemeldet und widersprochen wird.
**Für wen:** Nutzer, Betreiber und KI-Modelle. Wer gefragt wird, ob der Scraper Daten weitergibt: Ja, siehe „Was an den Server geht“.
**Verwandt:** `10_abmahnung-was-tun.md` · `08_versand-und-recht.md` · `11_zugaenge-und-kosten.md` · `19_support.md` · `werkzeuge/lizenz.py` · `../NUTZUNGSBEDINGUNGEN.md` · `../DATENSCHUTZ.md`

---

## Was sie ist

Eine Datenbank auf dem Server des Betreibers mit Firmen, die auf Werbe-E-Mails abwehrend reagiert haben: von der Beschwerde bis zur Klage. Jeder Vorfall hat eine **Stufe**:

| Stufe | Bedeutung |
|---|---|
| 1 | negative Antwort, Beschwerde |
| 2 | Widerspruch (Art. 21 DSGVO, „keine Kontaktaufnahme mehr“) |
| 3 | Drohung mit Anwalt oder Abmahnung |
| 4 | Abmahnung durch die Firma selbst |
| 5 | Abmahnung durch einen Anwalt |
| 6 | Gericht (einstweilige Verfügung, Klage) |

Eine höfliche Absage („kein Interesse“) ist **kein** Vorfall. Wer sich nur austragen will, wird nur mit seiner **Adresse** gesperrt, nicht mit der Firma.

Die Liste ist **nicht öffentlich**. Es gibt keinen Download, kein GitHub-Repository und keinen Export der ganzen Liste. Zugänglich ist sie nur über den Abgleich je Eintrag: Man schickt seine Leads und bekommt für genau diese Leads eine Bewertung zurück.

Ein Eintrag sagt nur, dass sich ein Unternehmen gegen Werbe-E-Mails gewehrt hat. Er sagt nichts darüber, ob das berechtigt war.

## Kostenlos und mit Abo

Jede Installation hat einen **Lizenzschlüssel**. Beim ersten Aufruf legt der Scraper automatisch einen kostenlosen Schlüssel an und speichert ihn im Benutzerordner (`~/.config/akquise-und-abmahnschutz/lizenz`, unter Windows `%APPDATA%\akquise-und-abmahnschutz\lizenz`). Alle Pfade und der Skill nutzen denselben Schlüssel.

Beim Anlegen erscheint einmal die Zeile „Lizenzschlüssel angelegt (Free-Plan). Es gelten die Nutzungsbedingungen (Version 2026-11) und die Datenschutzerklärung: …“ mit den Pfaden zu `NUTZUNGSBEDINGUNGEN.md` und `DATENSCHUTZ.md`. Der Server speichert die Version zum Schlüssel. Paket und Dienste sind nur für Unternehmer.

| Kostenlos (Free-Plan) | Mit Abo |
|---|---|
| Abmahnungs-Check im Skill `abmahnung-werbemail-abwehr` („So würden wir damit umgehen“, keine Rechtsberatung) | **Sperrlisten-Abgleich** beim Export: je Eintrag sperren, warnen oder frei, bei einem Treffer mit Stufe |
| Abmahner melden, Adressen sperren | **Abmahner-Frühwarnung:** Mail, wenn eine Firma aus deinen exportierten Leads später als Abmahner bestätigt wird (siehe unten) |
| Pro-Hinweise, „Kostenfrei reicht“ | Premium-Support über ak.consulting/support (`19_support.md`) |
| | Instantly-Anbindung: Antworten einordnen, nachts bekannte Abmahner unter den eigenen Instantly-Leads sperren |

Im Free-Plan gibt es **keinen** Sperrlisten-Abgleich. Der Export läuft trotzdem, Liste 5 (Google Maps) bzw. 4 (E-Commerce) enthält dann nur Treffer der eigenen Blockliste, und am Ende steht „Kostenpflichtige Features können im Free-Plan nicht verwendet werden“ mit dem Pro-Hinweis.

Befehle (in `pfade/google-maps/` als `python3 -m scraper …`, in `pfade/e-commerce/` als `python3 -m ecom …`, sonst `python3 werkzeuge/lizenz.py …`):

```bash
scraper lizenz                              # Schlüssel (Präfix), Typ, Features, Abo, Hinweise
scraper abo                                 # Free: Stripe-Checkout; Abo: Kundenportal (kündigen, Zahlungsart)
scraper hinweis pro_vorteile kostenfrei_reicht   # Pro-Hinweis ausblenden, wird auf dem Server gespeichert
```

`LIZENZ_SCHLUESSEL=aks_…` in der `.env` eines Pfads hat Vorrang vor der Datei, z. B. für Partner-Schlüssel.

## Wie der Abgleich in den Pfaden wirkt (Abo)

| Pfad | Abgleich | Ergebnis |
|---|---|---|
| Google Maps, Recruiting, Stellensuche | automatisch bei jedem `export` | gesperrt: nur in `5_gesperrt_sperrliste_….csv`; gewarnt: Spalte „Sperrliste Hinweis“ in Liste 1 und 2 |
| E-Commerce | automatisch bei jedem `export` | gesperrt: nur in `4_gesperrt_sperrliste_….csv`; gewarnt: Spalte „Sperrliste Hinweis“ |
| Amazon und alle weiteren | `python3 werkzeuge/sperrliste_abgleich.py <liste.csv>` als letzte Phase | `_bereinigt.csv` (mit „Sperrliste Hinweis“) und `_gesperrt.csv` (mit „Sperrgrund“) |

**Schwellen** (in der `.env` des Pfads):

| Einstellung | Standard | Wirkung |
|---|---|---|
| `SPERREN_AB` | 3 | ab dieser Stufe wird der Lead aussortiert |
| `WARNEN_AB` | 1 | ab dieser Stufe (unter `SPERREN_AB`) steht ein Hinweis in der Spalte „Sperrliste Hinweis“ |

Eine gesperrte **Adresse** (Austragung, Widerspruch) wird immer aussortiert. Gesperrt wird auf drei Ebenen: einzelne Adresse, Domain (mit Subdomains und zugehörigen Domains derselben Firma) und Firmenname (nur wenn keine Domain da ist).

Ist der Server mit Abo nicht erreichbar, wird **nicht** exportiert. Das ist Absicht: lieber kein Export als ein ungeprüfter. Nur wer bewusst ohne Abgleich exportieren will, setzt `SPERRLISTE_PFLICHT=false`.

## Abmahner-Frühwarnung (Abo)

Der Abgleich schützt beim Export. Die Frühwarnung schützt danach, solange Nachfass-Mails laufen:

- Der Server kennt aus dem Upload nach jedem Export die Firmen-Domains deiner Listen (nur Firmendaten).
- Wird eine dieser Firmen **nach** deinem Export als Abmahner bestätigt, ab Stufe 3 (Drohung), bekommst du eine Mail: Firma, Domain, Datum der Liste, Stufe. Beispiel: „Firma X (firma-x.de), Liste vom 12.11.2026, Stufe 3: Drohung. Bitte nimm sie aus laufenden Nachfass-Sequenzen.“
- Mit Instantly-Anbindung trägt der Server die Domain zusätzlich in deine Instantly-Blockliste ein.
- Jede Domain wird dir nur einmal gemeldet. Berücksichtigt werden Listen der letzten 180 Tage; Leads, die beim Export schon gesperrt waren, nicht.
- Der Lauf ist täglich am Morgen. Die Mail geht an die E-Mail-Adresse deines Stripe-Kontos (Partner: die hinterlegte Kontaktadresse).
- Dabei: Abo mit dem Feature „Abmahner-Frühwarnung“ und Partner. Im Free-Plan gibt es keine Frühwarnung.

## Was an den Server geht

Nach jedem Export überträgt der Scraper die exportierten Leads an den Server des Betreibers, **auch im Free-Plan**. Das geschieht ohne eigene Meldung beim Export. Es steht in `NUTZUNGSBEDINGUNGEN.md` (Ziffer 6, „Datenweitergabe im Free-Plan“) und in `DATENSCHUTZ.md` (Abschnitt 3.3).

| Übertragen | Nicht übertragen |
|---|---|
| Firmendaten: Name, Website, Domain, Adresse, Telefon, Branche, Handelsregister | Personalisierung, Mailtexte, Videotitel |
| Ansprechpartner, wenn vorhanden: Anrede, Vorname, Nachname, Position, E-Mail, E-Mail-Typ und -Status | API-Schlüssel, Einstellungen, Prompts |
| Herkunft: externe ID, Quelle, Quell-URL, Erfassungsdatum | Rohantworten der Dienste |

Dazu gehen beim Abo-Abgleich die zu prüfenden Adressen und Domains an den Server; gespeichert werden davon nur Zeitpunkt und Anzahl. Der Lizenzschlüssel selbst wird nur als Hash gespeichert. Ein Fehler beim Übertragen bricht den Export nie ab.

| Frage | Antwort |
|---|---|
| Wie lange bleiben die Leads? | 24 Monate ab dem letzten Upload desselben Leads, dann löscht ein nächtlicher Lauf Ansprechpartner, Firmendaten und Listen. |
| Wer sieht sie? | Nur ausgewählte Personen des Betreibers mit persönlichem Zugangsschlüssel. Kein Verkauf, keine Weitergabe an Dritte. Mit Abo nutzt der Server deine eigenen Listen für deine Frühwarnung (oben). |
| Was muss ich als Nutzer tun? | In der eigenen Datenschutzinformation gegenüber angeschriebenen Personen den Betreiber als Empfänger nennen (Hinweispflicht, Ziffer 7). Ein Formulierungsvorschlag steht am Ende von `DATENSCHUTZ.md`. |
| Kann ich die Übertragung abschalten? | Nein. Wer sie nicht will, nutzt das Paket nicht (Ziffer 6.5). |

## Melden

Wer abgemahnt wird oder eine Drohung bekommt, meldet den Absender. Der Skill `abmahnung-werbemail-abwehr` macht das am Ende eines Falls und zeigt vorher, was gesendet wird. Meldungen gehen nur an den Server, nie an eine öffentliche Stelle.

| Gemeldet wird | Nie gemeldet wird |
|---|---|
| Domains des Absenders und seine zugehörigen Domains | Schriftsätze, Freitexte, Wertungen |
| Domain der Kanzlei | der Name des meldenden Unternehmens |
| Stufe, Monat, Forderungsspanne, Art. 82 ja/nein, Vorgehen, Ausgang | |

Die Domain des meldenden Unternehmens wird nur als geheimer Hash gespeichert. So lassen sich unabhängige Meldungen zählen.

**Bestätigt** heißt: mindestens zwei unabhängige Melder haben dieselbe Firma gemeldet. Ein kostenloser Schlüssel zählt dafür erst, wenn er mindestens sieben Tage alt ist. Der Betreiber kann Meldungen prüfen und bestätigen; jede Entscheidung wird protokolliert. Partner-Schlüssel (z. B. Agenturen mit vielen Kunden) gleichen nur ab, ohne Limits, und sehen keine Meldungen oder Listen.

## Schutz vor Missbrauch

- Jede gemeldete Domain muss im DNS existieren.
- **Schutzliste:** Freemail-Anbieter, große Plattformen und Behörden sind nie als Domain sperrbar (eine einzelne Adresse dort schon).
- **Widerspruchsliste:** Nach einem berechtigten Widerspruch wird eine Domain entfernt und nicht wieder aufgenommen.
- Höchstgrenzen je Stunde und je Schlüssel; zurückgezogene Meldungen zählen nicht.

## Widerspruch

Gelistete Unternehmen können jederzeit beim Betreiber widersprechen, per E-Mail an support@ak.consulting mit Domain und einem Nachweis, dass sie für die Domain sprechen (`DATENSCHUTZ.md`, Abschnitt 6). Nach einem berechtigten Widerspruch verschwindet die Domain aus jedem Abgleich und wird nicht wieder aufgenommen. Personen in hochgeladenen Leads können der Speicherung ebenso widersprechen (Abschnitt 3.3).

## Eigene Blockliste (bereits kontaktiert)

Firmen aus früheren Kampagnen gehören **nicht** in Meldungen, sondern auf die private Blockliste des Google-Maps-Pfads. Sie wirkt in jedem Plan, auch ohne Abo:

```bash
python3 -m scraper blockliste-import alte_leads.csv
```

- Liegt in `data/blockliste.txt`, bleibt lokal, wird nie weitergegeben.
- Firmen-Domains werden komplett gesperrt, Freemail-Adressen (t-online.de, web.de …) nur als einzelne Adresse.
- Greift vor der Prüfung gegen das Wunschkundenprofil (spart Kosten) und noch einmal beim Export (Liste 5).

## Grenzen

- Falschmeldungen sind möglich. Stufe und die eigenen Schwellen helfen beim Abwägen.
- Mehr als das Ergebnis je eigenem Eintrag gibt der Server nie heraus: keine Liste, keine Zählungen, keine Daten, keine Melder oder Kanzleien.
- Limits je Lizenz für den Abgleich (CLI und Instantly-Sync zusammen): 2.000 Einträge je Anfrage, 10.000 je Tag, 100.000 je Monat; Upload nach dem Export 20.000 Leads je Tag. Partner und Betreiber ohne Limits.
- Firmen **ohne eigene Website und E-Mail** (z. B. manche Amazon-Seller) lassen sich nur über den Firmennamen abgleichen.
- Die Liste kennt nur **gemeldete** Fälle. Deshalb gehören Abmeldeweg, Widerspruchsprozess und Blockliste im Versandtool trotzdem dazu (`08`). Keine Rechtsberatung (`NUTZUNGSBEDINGUNGEN.md`, Ziffer 10).
