# Änderungen

## 4.3.4 – 2026-11-14

- **Ohne Terminal:** `README.md` beschreibt den Abgleich als Satz an Claude statt als Befehl; `SKILL.md` sagt ausdrücklich, dass der Nutzer nie im Terminal arbeitet.

## 4.3.3 – 2026-11-14

- **Klarer Text zum Datenzugriff:** `SKILL.md`, `README.md`, `references/06_sperrliste-server.md` und `scripts/sperrliste.py` sagen nicht mehr „für ausgewählte Personen mit Zugangsschlüssel einsehbar“, sondern dass die Daten nie ausgegeben werden und nur das Ergebnis des Abgleichs für selbst geprüfte Einträge zurückkommt.
- **Rechtstexte freigegeben:** Vermerk „Entwurf“ in `NUTZUNGSBEDINGUNGEN.md` und `DATENSCHUTZ.md` ersetzt durch „anwaltlich abgenommen“; der Text bleibt unverändert.

## 4.3.2 – 2026-11-13

- **Abgleich ohne Details aus der Datenbank:** `sperrliste.py pruefen` und `abgleich` zeigen je Treffer nur noch Stufe und Ergebnis; Anzahl, Datum und Status gibt der Server nicht mehr heraus. Toter Code zur Kanzlei-Echtheit im Check entfernt.

## 4.3.1 – 2026-11-13

- **Keine Warnungen vor E-Mail-Akquise:** `SKILL.md` sagt am Ende eines Falls nicht mehr, Kaltakquise sei unzulässig, und bewertet den Unterlassungsanspruch als Verhandlungsfrage (Spielraum bei DSGVO-Schadensersatz, Kosten, UE-Entwurf). Die Hinweise für eine saubere Akquise danach bleiben. `NUTZUNGSBEDINGUNGEN.md` Ziffer 9 ohne den Satz „Sie macht unerwünschte Werbung nicht zulässig“. Der Kasten „Keine Rechtsberatung“ bleibt.

## 4.3 – 2026-11-12

Erfahrungen aus der zweiten Runde eines echten Falls (Kanzlei verweigert Nachweis und Rechnung):
- **Kosten-Standard:** statt Kostennote nach § 10 RVG (kein vorprozessualer Anspruch, OLG Frankfurt 6 U 49/17) jetzt Darlegung verlangen, Kostenbelastung mit Nichtwissen bestreiten (BGH I ZR 152/21, Rn. 71 f.) und bei Umsatzsteuer die Rechnung des Abmahners nach § 14 Abs. 2 Satz 2 Nr. 1 UStG fordern; Zurückbehaltungsrecht bis zur Rechnung (BGH VII ZR 247/13).
- **Zweite Runde** in `references/02_antwortbausteine.md`: Variante A (Angebot auf begründetem Wert gegen Rechnung, nicht an einen Rechnungsbetrag geknüpft), Variante B (Ablehnung), Bausteine zu BFH XI R 27/14 („eigener Leistungsanspruch“), Rechnung, Gerichtsstand und nicht veröffentlichten Entscheidungen.
- **Rechtsprechung** (`references/01_rechtsprechung.md`) im Volltext geprüft und mit Randnummern: OLG Hamburg 15 W 32/25 (bis 1.000 €), KG 5 W 152/21 und 5 W 187/13, LG Hagen 2 O 278/13, OLG Hamm 9 U 73/14, BGH VI ZR 22/24 (keine Generalprävention), BGH I ZR 87/20, OLG Karlsruhe 6 U 255/21; Bewertung der von Abmahnern oft zitierten Streitwert-Liste; Gerichtsstand und Prozesskosten. LG München II 6 T 1583/17 nur noch als Sekundärquelle.
- **Begleitschreiben:** nie „Empfehlung“, immer „wir würden an Ihrer Stelle … vorgehen“; gerahmter Hinweis „keine Rechtsberatung“ oben und am Ende; Formel für die Abgabe des Falls an den Kunden.
- **Fallstricke:** Bedingung „Rechnung über [Betrag]“, „weisen zurück“ als Klageanlass, abgeschriebene Urteilspassagen, veraltetes UStG-Zitat, Sekundärquellen.
- Phase 6 verlangt Volltextprüfung mit Randnummer; Phase 10 regelt die Verweigerung von Darlegung oder Rechnung. „Empfehlungen“ in Beweisprotokoll und Kampagnenhinweisen heißen jetzt „Hinweise“.

## 4.2 – 2026-11-10

- `scripts/lizenz.py support`: Support-Paket für alle und die Angaben für das Formular auf ak.consulting/support; ohne Abo zuerst der Hinweis auf den Premium-Support. Ersetzt die Mail an den Support. Verbindungen versuchen IPv4 zuerst.
- `SKILL.md`: wie die KI eine Support-Anfrage vorbereitet.
- `NUTZUNGSBEDINGUNGEN.md` Ziffer 4.2 (Premium-Support statt Support-Paket) und `DATENSCHUTZ.md` 3.8 (Supportformular, 12 Monate Speicherdauer).

## 4.1 – Nachtrag 2026-11-08

- `DATENSCHUTZ.md` 3.6: Speicherdauer der Einreichungen festgelegt auf drei Jahre nach Ende des Einreichungsjahres; der Server löscht danach nachts automatisch.

## 4.1 – 2026-11-04

- `NUTZUNGSBEDINGUNGEN.md` neu gefasst (Version 2026-11, identisch mit dem Lead-Scraper): nur Unternehmer, Gegenseitigkeit mit Bestätigung je Meldung, „Keine Rechtsberatung“ nach RDG, Haftung für Unternehmer. Betreiber ist Benjamin Wünsche.
- Neu `DATENSCHUTZ.md`: was der Server speichert (Abmahnungs-Check, Meldungen, Adresssperren, Lizenz), wie lange, und wie gelistete Unternehmen widersprechen.
- `scripts/lizenz.py`: Beim Anlegen des Schlüssels erscheint einmal eine Zeile mit Version und Pfaden der Texte; der Server speichert die Version.

## 4.0 – 2026-11-03

Keine öffentliche Liste mehr. Alles geht nur an den Server von Agentur Consulting und ist dort nur für ausgewählte Personen mit Zugangsschlüssel einsehbar.

- **Neu: kostenloser Abmahnungs-Check** in Phase 1b (`sperrliste.py check --datei abmahnung.json`). Der Server speichert die Abmahnung und antwortet mit „So würden wir damit umgehen“: Fristen, Schritte, Echtheit der Kanzlei, immer mit dem festen Hinweis „Keine Rechtsberatung …“. Vorher sagt Claude, dass die Eckdaten an den Server gehen und gespeichert werden.
- **Datensparsamkeit:** Das Skript sendet nur Felder des Formats (`references/06_sperrliste-server.md`), Kontaktdaten nur mit Einwilligung. Namen natürlicher Personen, E-Mail-Adressen und Mail-Inhalte bleiben weg.
- **Meldung nur nach Zustimmung** (Phase 9), über den Server statt über Relay und GitHub. Neue Option `--stufe` (Standard 5 mit Kanzlei, sonst 4), dazu `--beleg-art` und `--einreichung`; `--status` heißt auch `--ausgang`. Ist der Server nicht erreichbar, wird später erneut gesendet. Es gibt keinen GitHub-Link mehr.
- **Abgestufter Abgleich nur mit Abo:** `pruefen` und `abgleich` fragen den Server (Stufe, Anzahl, Datum, Status). Im Free-Plan erscheint „Kostenpflichtige Features können im Free-Plan nicht verwendet werden“, und es wird nichts übermittelt.
- Lizenzschlüssel: wird beim ersten Aufruf automatisch angelegt (Free-Plan) und nie angezeigt. Neu `scripts/lizenz.py`, dieselbe Datei wie im Lead-Scraper.
- Entfernt: `sperrliste.py laden`, Relay, GitHub-Repository und Issue-Formular, `scripts/community.json`.
- `references/06_community-sperrliste.md` heißt jetzt `references/06_sperrliste-server.md` und beschreibt Server, JSON-Format, Abgleich und Meldung. `beispiele/05_meldung-sperrliste.md`, `SKILL.md`, `README.md`, `references/02`, `references/05` und `listen/README.md` angepasst.
- Neu: Offline-Tests `scripts/test_sperrliste.py` gegen einen lokalen Test-Server.

## 3.1 – Oktober 2026

Feste Linie statt schnellem Nachgeben. Grundlage sind die Erfahrungen aus zwei echten Fällen mit Gegenanwalt-Check.

- **Grundhaltung „schnell bei der Unterlassung, fest beim Geld“:**
  - Im ersten Schreiben wird nichts gezahlt.
  - Der Gegenstandswert wird immer geprüft und, wenn überhöht, gerügt.
  - Keine Angaben zur eigenen Versandinfrastruktur.
- **Kosten:** Standard ist jetzt Variante B, also Kostennote nach § 10 RVG und Zahlungsnachweis zuerst. Die Zahlung bleibt ausdrücklich offen (§ 250 BGB), die Antwort kommt binnen 14 Tagen. Volle Zahlung nur noch auf ausdrücklichen Wunsch.
- **Keine Rückfragen-Runde vor der UE.** Nachweisforderungen kommen in dasselbe Schreiben. Die zulässigen und die schädlichen Rückfragen sind aufgelistet.
- **Neue Prüfpunkte:**
  - Frist und Zugang
  - eigene Zitate des Abmahners gegen ihn wenden
  - Auskunftsrecht nur für natürliche Personen
  - überdehnte Klauseln wie „sonstige elektronische Nachrichten“
  - Rechtsform des Abgemahnten
  - frühere Abmahnungen
  - Geschäftsmodell der Kanzlei
  - eigene Angriffsfläche (Versanddomains)
- **Auskunft Art. 15:** Vollmacht oder anwaltliche Versicherung mit Frist anfordern, sonst verschlossener Umschlag über die Kanzlei. Nicht mehr direkt an die anwaltlich vertretene Person.
- **UE-Muster:**
  - „und ohne § 7 Abs. 3 UWG“
  - „Werbung mittels elektronischer Post“
  - „gleich an welche Adresse“
  - „wie mit Schreiben … beanstandet“
  - Variante für die GbR
- **Versand:**
  - Nie per Telefax, vorab nur per E-Mail.
  - Bei Nicht-Kaufleuten Schriftform mit Original per Einschreiben.
  - Bei der GbR unterschreiben alle Gesellschafter.
  - Feiertage einrechnen.
  - Neutrales Absender-Postfach, Briefkopf ohne Versanddomain.
- Neue **Textbausteine** in `references/02_antwortbausteine.md`. Dazu weitere verbotene Formulierungen, Fallstricke und Rechtsprechung zum Gegenstandswert (AG München 142 C 1633/22, OLG Hamm 9 U 73/14 als Beschluss).
- Neue **Phase 10 „Nachgang“:** Kostennote, Mahnung, Änderungswünsche, Mahnbescheid.
- Musterfälle in `beispiele/01` und `02` auf die neue Linie umgestellt.

## 3.0 – Oktober 2026

- Community-Sperrliste auf ein **GitHub-Repository** umgestellt (vorher Google Sheet + Formular + Moderation).
- Gesperrt werden nur noch **Domains** mit allen Subdomains. Keine E-Mail-Adressen und keine Hashes mehr.
- Neuer Schritt in Phase 1: **zugehörige Domains ermitteln**, mit Quelle je Domain.
- Phase 9: Meldung ist **Nutzungsbedingung**. Sie wird angezeigt und automatisch über ein Relay gesendet, ohne Token beim Nutzer. Ersatzweise gibt es einen vorausgefüllten GitHub-Issue-Link.
- Automatische Prüfung statt Moderation:
  - Format, DNS, Schutzliste, Widerspruchsliste
  - Rate-Limits
  - anonymer Melder-Schlüssel
  - „bestätigt“ ab zwei Meldern
- `scripts/sperrliste.py` ersetzt `blockliste.py` (pruefen, melden, laden, abgleich); neu `scripts/community.json` und `NUTZUNGSBEDINGUNGEN.md`.
- Ersetzt: `references/06_community-sperrliste.md`, `beispiele/05_meldung-sperrliste.md`.

## 2.1 – Oktober 2026

- Keine Einrichtung mehr: Token, `config.json` und Web-Schnittstelle entfallen.
- Community-Blockliste: öffentlich lesbares Google Sheet, Meldung per vorausgefülltem Google-Formular (der Nutzer sendet selbst), Moderation durch den Betreiber vor der Veröffentlichung.
- `scripts/blockliste.py` ersetzt `register_client.py` (pruefen, meldelink, statuslink, sperrliste, abgleich, hash).
- Funktioniert eingeschränkt auch ohne Code-Ausführung (Abgleich über Domain, Link manuell gebaut).

## 2.0 – Oktober 2026

- Projektstruktur mit `references/`, `listen/`, `beispiele/`, `scripts/`; SKILL.md als schlanke Ablaufsteuerung.
- Modul W „Website-Verstöße des Abmahners“ mit Prüfraster, Beweissicherung (Browser-Mitschnitt, Seitensicherung, SHA-256, zwei RFC-3161-Zeitstempel) und Protokoll-Gliederung.
- Referenzlisten bekannter Drittserver (68 Einträge) und Consent-Tools (15 Einträge).
- Liste verbotener Formulierungen; Wenn-dann-Drohungen werden auch auf Nutzerwunsch nicht formuliert.
- Rechtsprechung ergänzt: EuGH C-21/23, LG München I 3 O 17493/20, EuGH C-311/18/DPF, VO (EU) 2024/3228, § 356a BGB; Amtsgerichtszuständigkeit bis 10.000 € seit 01.01.2026.

## 1.0

- Prüfung, Recherche, Gegenanwalt-Check, Antwortschreiben und modifizierte UE als PDF.
