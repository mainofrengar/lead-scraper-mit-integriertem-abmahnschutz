---
name: abmahnung-werbemail-abwehr
description: Prüft Abmahnungen wegen Werbe-E-Mails/Cold-Mails (UWG, §§ 823/1004 BGB, Art. 82/15 DSGVO), holt den kostenlosen Abmahnungs-Check vom Server von Agentur Consulting, meldet den Abmahner nach Zustimmung (abgestufter Sperrlisten-Abgleich mit Abo), recherchiert Kanzlei, Rechtsprechung und Webauftritt des Abmahners, sichert Website-Verstöße gerichtsfest, lässt Gegenanwalt-Check laufen und baut Antwortschreiben plus modifizierte Unterlassungserklärung als PDF. Nutzen bei jeder Abmahnung, Unterlassungsaufforderung oder DSGVO-Schadensersatzforderung wegen E-Mail-Werbung.
---

# Abmahnung Werbe-E-Mail – Prüfung & Abwehr

Verfahren für Unternehmen, die wegen einer unerlaubten Werbe-E-Mail (typisch: B2B-Cold-Mail) abgemahnt wurden. Ergebnis: fundierte Einschätzung, verifizierte Rechtsprechung, versandfertiges Antwortschreiben und modifizierte Unterlassungserklärung (UE) als PDF. Auf Wunsch zusätzlich: gesicherte Prüfung des Webauftritts des Abmahners. Der Skill arbeitet mit dem Server von Agentur Consulting: Er holt zu jeder Abmahnung den kostenlosen Check „So würden wir damit umgehen“, meldet den Abmahner nach Zustimmung des Nutzers und nutzt den abgestuften Sperrlisten-Abgleich, wenn ein Abo besteht. **Es gibt keine öffentliche Liste.** Die Daten liegen nur auf dem Server und werden nie ausgegeben; Nutzer erhalten nur das Ergebnis des Abgleichs für selbst geprüfte Einträge. Der kostenlose Lizenzschlüssel wird beim ersten Aufruf automatisch angelegt; keine Einrichtung, kein Konto.

**Datenhinweis (einmal zu Beginn nennen, in einem Satz):** Für den kostenlosen Check gehen die Eckdaten der Abmahnung an den Server von Agentur Consulting und werden dort gespeichert; den Abmahner meldet der Skill am Ende nur, wenn der Nutzer zustimmt – nur Domains und Sachangaben, keine E-Mail-Adressen, keine Namen (Details: `references/06_sperrliste-server.md`).

Der Nutzer ist in der Regel das abgemahnte Unternehmen selbst (Geschäftsführung oder Mitarbeiter). Weise einmal zu Beginn kurz darauf hin, dass der Skill Recherche und Entwürfe liefert, aber keine anwaltliche Beratung ersetzt, und dass bei Klage, einstweiliger Verfügung oder hohen Beträgen ein Anwalt hinzugezogen werden sollte. Danach keine wiederholten Disclaimer. Der Nutzer arbeitet nie im Terminal: Skripte selbst ausführen, nie Befehle zum Abtippen zeigen.

## Aufbau dieses Skills

Diese Datei steuert den Ablauf. Details stehen in eigenen Dateien – lies sie in der Phase, in der sie gebraucht werden, nicht alle vorab.

| Datei | Inhalt | Wann lesen |
|---|---|---|
| `references/01_rechtsprechung.md` | Entscheidungen, Normen, RVG-Werte | Phase 2 und 6 |
| `references/02_antwortbausteine.md` | Aufbau Antwortschreiben, UE-Muster, verbotene Formulierungen | Phase 4 |
| `references/03_website-pruefraster.md` | Prüfraster Website des Abmahners | Modul W |
| `references/04_beweissicherung.md` | Mitschnitt, Seitensicherung, Hashes, Zeitstempel, Protokoll | Modul W |
| `references/05_fallstricke.md` | Bekannte Eigentore und Fehlgriffe | vor Phase 4 und vor Versand |
| `references/06_sperrliste-server.md` | Server, Abmahnungs-Check und sein JSON-Format, Datensparsamkeit, abgestufter Abgleich (Abo), Meldung, zugehörige Domains | Phase 1, 1b, 9 und 10 |
| `NUTZUNGSBEDINGUNGEN.md` | Nutzungsbedingungen (nur Unternehmer, Gegenseitigkeit, keine Rechtsberatung) | bei Fragen des Nutzers |
| `DATENSCHUTZ.md` | Datenschutzerklärung: was auf dem Server gespeichert wird, wie lange, Widerspruch | bei Fragen zu Daten, Speicherung, Löschung |
| `listen/drittanbieter.csv` | Bekannte Drittserver: Anbieter, Kategorie, Sitz, typische Norm | Modul W, Auswertung |
| `listen/consent-tools.csv` | Consent-Tools und wo sie die Ablehnung speichern | Modul W, Szenario B |
| `beispiele/` | Fiktive Musterfälle: Antwortschreiben, UE, Website-Block, Protokoll-Gliederung, Meldung an die Sperrliste | Phase 4, 8, 9 |
| `scripts/` | `sperrliste.py` (+ `lizenz.py`), `sicherung_netzwerk.py`, `sicherung_seiten.py`, `integritaet.sh`, `auswertung.py` | wie in den Phasen angegeben |

Skripte immer über ihren Pfad in diesem Skill-Ordner aufrufen.

**Support für den Skill selbst** (nicht für die Abmahnung): Will der Nutzer Support, `python3 scripts/lizenz.py support --thema abmahnung --anliegen … --beschreibung "…"` ausführen und die ausgegebenen Formularangaben für ak.consulting/support geordnet weitergeben. Ohne Abo zuerst sagen, dass Premium-Support ein Abo braucht (`python3 scripts/lizenz.py abo`). Nie den vollständigen Lizenzschlüssel weitergeben, nur die Kennung aus der Ausgabe.

## Was du vom Nutzer brauchst

Zu Beginn einsammeln (fehlendes nachfragen, den Rest selbst recherchieren):

- Abmahnung als PDF/Scan inkl. Anlagen (UE-Entwurf, Kopie der beanstandeten Mail)
- Name des eigenen Unternehmens (Registerdaten, Geschäftsführer, Kontaktdaten recherchierst du über Impressum/Handelsregister selbst)
- Welche Tools und Dienstleister am Versand beteiligt waren (Versandtool, CRM, Lead-Quelle, Video-/Tracking-Dienste) – nötig für Auskunft und Weitergabe-Frage
- Nur für Modul W: Ist das eigene Unternehmen in derselben Branche und Region wie der Abmahner tätig (Mitbewerber)?

## Grundhaltung

- Ehrlich bewerten, wo der Spielraum liegt: Über die Unterlassung selbst wird selten gestritten; eine modifizierte UE beendet diesen Teil meist am günstigsten. Angreifbar sind meist DSGVO-Schadensersatz, Kosten, UE-Entwurf und das Vorgehen des Abmahners.
- **Schnell bei der Unterlassung, fest beim Geld.**
  - Nur bei der Unterlassungserklärung zählt Tempo. Sie allein beseitigt die Wiederholungsgefahr und verhindert eine einstweilige Verfügung.
  - Bei allen Geldforderungen gilt die feste Linie. Das betrifft Anwaltskosten, Art. 82 und Zahlungspflichten im UE-Entwurf.
  - Im ersten Schreiben wird nichts gezahlt. Kosten erst nach Darlegung der Kostenbelastung und, wenn Umsatzsteuer verlangt wird, Rechnung des Abmahners (Phase 7).
  - Den Gegenstandswert immer prüfen und, wenn er überhöht ist, begründet rügen.
  - Jede Forderung einzeln prüfen. Nachgeben nur, wo die Rechtslage es verlangt, nicht wegen kurzer Fristen, hoher Beträge oder Druck im Ton.
- **Fest heißt nicht laut.** Die Härte entsteht durch genaue, prüfbare Sätze, nicht durch Drohungen, Wertungen oder eine Flut von Rückfragen. Jede Nachweisforderung muss rechtlich etwas bringen (Phase 4).
- Jede Behauptung im Schreiben muss halten, wenn ein erfahrener Gegenanwalt sie liest. Lieber weglassen als angreifbar formulieren.
- **Nichts preisgeben, was gegen den Nutzer verwendet werden kann.** Keine Angaben zu Tools, Listen, Sequenzen, Versanddomains oder weiteren Mails. Wer systematisch versendet, bekommt einen höheren Gegenstandswert und Folgeabmahnungen. Das gilt auch für Briefkopf, Absenderadresse und die Formulierung der Sperre.
- Keine Gegendrohungen, keine Verknüpfung von Hinweisen auf fremde Verstöße mit Geld- oder Verzichtsforderungen (Nötigungs-/Erpressungsvorwurf §§ 240, 253 StGB, Anfechtbarkeit § 123 BGB). Das gilt auch, wenn der Nutzer ausdrücklich eine „Wenn Sie …, dann sehen wir uns gezwungen …“-Formulierung wünscht: erklären, warum sie schadet, und die neutrale Fassung aus `references/02_antwortbausteine.md` anbieten.
- Fristen zuerst: UE-Frist aus der Abmahnung, Auskunftsfrist Art. 15 DSGVO (1 Monat ab Zugang). Nenne beide Daten früh im Gespräch.
- In eine Meldung gehören nur Domains und Sachdaten. Keine E-Mail-Adressen, keine Namen, keine Aktenzeichen, keine Wertungen („Abzocker“, „Serienabmahner“). Gesperrt wird immer die ganze Domain mit allen Subdomains und Adressen.
- An den Server geht nur, was das Format vorsieht und der Zweck braucht (Datensparsamkeit, `references/06_sperrliste-server.md`). Der Lizenzschlüssel wird nie angezeigt.

## Phase 1 – Abmahnung erfassen

Abmahnungen kommen oft als Scan-PDF ohne Textebene: `pdftotext` liefert dann nichts, also die Seiten als Bild lesen (Read mit `pages`). Erfassen:

- Abmahner (Person, Rechtsform, Branche, Adresse, **alle Domains**), Kanzlei (Briefkopf: Adressen, Telefon, E-Mail-Domain, Bank, USt-ID), Aktenzeichen, Datum
- Abgemahnter: Firma, Absenderdomain der Mail, Signatur (passt der Absender zur abgemahnten Firma?).
- **Rechtsform des Abgemahnten:** Kaufmann oder nicht (GbR, Freiberufler, Kleingewerbe)? Davon hängen Form und Unterschriften der UE ab (Phase 8).
- **Frühere Abmahnungen** gegen denselben Nutzer (eigene Fallakte, Sperrliste)? Mehrere in kurzer Zeit wirken wie systematischer Versand. Dann besonders streng auf Angaben zu Tools, Listen und Domains achten.
- Beanstandete Mail: Datum/Uhrzeit, Absender, Betreff, **Zieladresse**, Inhalt (Kopie vs. Inhaltsangabe im Schreiben abgleichen)
- **Zugang:** Datum und Weg (Einwurf-Einschreiben mit Sendungsnummer, Fax, E-Mail) festhalten. Umschlag und Sendungsverfolgung sichern lassen, falls das Schreiben mit der Frist argumentiert.
- Forderungen: Unterlassung, Auskunft Art. 15, Schadensersatz Art. 82 (Betrag), Anwaltskosten (Gegenstandswert, Gebührensatz, Pauschale), Fristen
- UE-Entwurf: Zahlungspflichten enthalten? Formulierungsfehler? Vertragsstrafe-Modell?
- Zitierte Urteile (alle notieren, später prüfen)

**Zugehörige Domains ermitteln** (für Sperrliste, UE und Meldung): Domain der Zieladresse; Domains im Abmahnschreiben (Briefkopf, Signatur, Mail-Kopie); Impressum der Website (weitere Marken, Shops, Landingpages); Weiterleitungen (`curl -sIL`); im Impressum oder Footer verlinkte Seiten desselben Rechtsträgers; Handelsregister/Northdata (weitere Firmen derselben Person nur, wenn dieselbe Anschrift oder dasselbe Geschäft). Nur Domains aufnehmen, die belegbar demselben Abmahner gehören; Quelle je Domain kurz notieren. **Nie** Freemail-, Hosting- oder Plattformdomains (gmail.com, web.de, t-online.de, myshopify.com, wixsite.com, immobilienscout24.de …) und nie die Kanzlei als Abmahner-Domain.

## Phase 1b – Abmahnungs-Check und Abgleich (Server von Agentur Consulting)

Sobald Abmahner, zugehörige Domains, Kanzlei, Fristen und Forderungen erfasst sind (Details und JSON-Format: `references/06_sperrliste-server.md`):

1. **Vorher sagen**, in einem Satz: Die Eckdaten der Abmahnung gehen an den Server von Agentur Consulting und werden dort gespeichert. Widerspricht der Nutzer, nicht senden und normal weitermachen.
2. Die Eckdaten **datensparsam** als JSON in den Arbeitsordner schreiben: nur Felder des Formats, keine Namen natürlicher Personen, keine E-Mail-Adressen, keine Mail-Inhalte, Kontaktdaten nur mit ausdrücklicher Einwilligung. Dann den kostenlosen Check senden:
   ```bash
   python3 scripts/sperrliste.py check --datei arbeit/abmahnung.json
   ```
3. Die Antwort „So würden wir damit umgehen“ (Fristen, Schritte, Echtheit der Kanzlei) dem Nutzer zusammengefasst zeigen, **immer mit dem festen Hinweis „Keine Rechtsberatung: …“ aus der Antwort direkt nach dem Titel und noch einmal am Ende**. Sie ist eine allgemeine Beschreibung und ersetzt die Prüfung in Phase 2 bis 7 nicht. Ist die Kanzlei mit Abweichungen bekannt, den Echtheitscheck in Phase 3 vorziehen. Die Nummer der Einreichung für Phase 9 notieren.
4. **Abgestufter Abgleich nur mit Abo:**
   ```bash
   python3 scripts/sperrliste.py pruefen --domain abmahner.de abmahner-shop.de --kanzlei-domain kanzlei.de
   ```
   - Im Free-Plan (Exit-Code 5, „Kostenpflichtige Features können im Free-Plan nicht verwendet werden“): einmal kurz erwähnen, nicht drängen, weitermachen. Der kostenlose Check gilt trotzdem.
   - **Treffer:** Stufe und Ergebnis (sperren oder warnen) zeigen; mehr gibt der Server nicht heraus. In Phase 3 und 7 berücksichtigen. Als Erfahrungswerte kennzeichnen, nicht als Prognose.
5. Server nicht erreichbar (Exit-Code 4) oder keine Code-Ausführung: kurz sagen, dass Check und Abgleich entfallen, und normal weitermachen.

## Phase 2 – Erstprüfung auf Angriffspunkte

Prüfraster (Fundstellen in `references/01_rechtsprechung.md`):

1. **Art. 82 DSGVO**: Ohne konkret dargelegten Schaden kein Anspruch (BGH VI ZR 109/23). Achte auf spekulative Formulierungen („naheliegende Möglichkeit“) – das ist der Versuch, den BGH-Ausnahmefall „Weitergabe an Dritte“ zu konstruieren.
2. **Zitate**: Jedes Urteil prüfen (Az., Datum, Urteil oder Beschluss, worum ging es wirklich). Fehlzitate sind Indiz für Textbausteine. **Besonders prüfen, ob die eigenen Zitate des Abmahners einen niedrigeren Wert tragen** als den geforderten. Das ist das stärkste Argument gegen den Gegenstandswert (Beispiel in 01).
3. **Kosten**: RVG-Rechnung nachrechnen (Tabelle in 01). Gegenstandswert gegen die Rechtsprechung am voraussichtlichen Gerichtsstand halten (Phase 6). Erstattungsfähig sind nur Kosten, die der Mandant seinem Anwalt tatsächlich schuldet.
4. **UE-Entwurf**:
   - Zahlungspflichten gehören nicht hinein.
   - Feste Vertragsstrafe statt neuem Hamburger Brauch.
   - Überdehnte Reichweite: „sonstige elektronische Nachrichten“ ohne Werbebezug, alle Kanäle, verbundene Unternehmen.
   - „oder“-Falle bei § 7 Abs. 3 UWG.
   - Sinnlose Klauseln (z. B. „Gefährdungshaftung“), falsche Bezeichnungen, UWG-Formeln ohne Wettbewerbsverhältnis.
5. **Passivlegitimation**: Absender/Marke vs. abgemahnte Firma.
6. **Inhaltsabgleich**: Beschreibt das Schreiben Inhalte, die in der Mail-Kopie fehlen? Fehlt die Kopie ganz?
7. **Vollmacht**: Für die Abmahnung irrelevant (BGH I ZR 140/08), für Herausgabe personenbezogener Daten an Dritte darf sie verlangt werden.
8. **Frist und Zugang**: Läuft die Frist am oder vor dem Zugangstag ab, ist sie unangemessen kurz. Dann gilt eine angemessene Frist. Das im Schreiben kurz festhalten, trotzdem sofort handeln.
9. **Auskunft Art. 15**: Das Recht hat nur die betroffene natürliche Person, nicht die GmbH oder KG, die abmahnt. Die Forderung trotzdem als Antrag der Person behandeln (Phase 4).

## Phase 3 – Kanzlei- und Abmahner-Recherche

Per Websuche und Abruf von Webseiten:

- Kanzlei-Website + Impressum: Schwerpunkte, Fachanwaltschaften, Partner, Rechtsform, offizielle Kontaktdaten.
- **Echtheitscheck**: Briefkopf-Kontaktdaten (Domain, Telefon, Bank) mit Impressum abgleichen; bei Abweichung das Aktenzeichen über die Impressumsnummer bestätigen lassen.
- Verbundene Gesellschaften der Anwälte (Inkasso-/Legal-Tech-UG, „No-win-no-fee“-Portale): Handelsregister, Impressum, Werbeaussagen wörtlich sichern.
- **Geschäftsmodell der Kanzlei:** Einzelanwalt mit Abmahnroutine oder Massenbetrieb? Wirbt die Kanzlei öffentlich um Empfänger von Werbe-Mails, etwa mit Rechtstipps nach dem Muster „die Kosten trägt der Verursacher“? Quellen: Kanzlei-Website, anwalt.de-Profil, Abmahnanwälte-Liste des Händlerbunds. Für Rechtsmissbrauch reicht das nicht. Es stützt aber die Linie „erst Kostennachweis“. Im Schreiben nicht erwähnen.
- Berichte über frühere Abmahnungen derselben Kanzlei/desselben Mandanten (Abmahnwarner-Seiten, Blogs Betroffener): Forderungshöhen, Muster, Vollmacht-Auffälligkeiten, Verhalten nach Widerspruch. Mit den Ergebnissen aus Phase 1b abgleichen.
- Abmahner selbst: Website, weitere Firmen; die Liste der zugehörigen Domains aus Phase 1 vervollständigen.
- **Eigene Angriffsfläche des Nutzers:** Versanddomain prüfen (Registrierungsdatum, Website, Impressum, gleichzeitig registrierte Schwesterdomains). Was die Gegenseite findet, stützt einen höheren Wert. Es darf deshalb weder im Schreiben noch im Briefkopf auftauchen.
- Website des Abmahners prüfen? → **Modul W** anbieten. Die Sicherung muss **vor** Versand des Antwortschreibens fertig sein.
- Seiten, die einen einfachen Abruf mit 403 blocken, im Browser öffnen. Bot-Schutz nie umgehen, also keine gefälschten User-Agents.

Daraus eine Reaktionsprognose ableiten (wahrscheinlich / möglich / unwahrscheinlich) und als Einschätzung kennzeichnen. Einzelquellen als solche benennen.

## Phase 4 – Antwortentwurf

Vorher `references/05_fallstricke.md` lesen. Aufbau, Textbausteine und UE-Muster: `references/02_antwortbausteine.md`; ein vollständiger fiktiver Musterfall liegt in `beispiele/`.

Kurzfassung des Aufbaus:

0. Zugang und, falls nötig, Absatz zur unangemessen kurzen Frist.
1. Modifizierte UE ohne Anerkennung einer Rechtspflicht:
   - Änderungen gegenüber dem Entwurf offen benennen.
   - Konkrete Änderungswünsche anbieten.
   - Sperre neutral formulieren.
   - Um alle Adressen und Domains des Abmahners bitten.
2. Art. 82 zurückweisen.
3. Kosten: Standard „erst Nachweis“ und im selben Schreiben die Rüge des Gegenstandswerts.
4. Auskunft Art. 15: Vollmacht oder anwaltliche Versicherung mit Frist anfordern, sonst verschlossen über die Kanzlei.
5. Optional Website-Hinweise aus Modul W.
6. Schluss: „Mit der anliegenden Erklärung ist die Wiederholungsgefahr entfallen.“

**Keine Rückfragen-Runde vor der UE.** Rückfragen halten die Frist nicht an. Sie kosten das Kostenprivileg nach § 93 ZPO und lesen sich als Hinhalten. Eine Kanzlei mit Abmahnroutine beantwortet sie nebenbei, eine einstweilige Verfügung kostet den Nutzer schnell 2.000 bis 3.000 €. Nachweisforderungen gehören deshalb **in dasselbe Schreiben wie die UE**. Zulässig sind nur Forderungen, die rechtlich etwas bringen:

- Darlegung der Kostenbelastung (Kostenbelastung mit Nichtwissen bestreiten; ein vorprozessualer Anspruch auf die Kostennote nach § 10 RVG besteht nicht) und bei Umsatzsteuer eine Rechnung des Abmahners nach § 14 UStG
- Vollmacht oder anwaltliche Versicherung für die Herausgabe personenbezogener Daten
- Kopie der beanstandeten Mail, falls sie fehlt
- alle Adressen und Domains des Abmahners

Nie anfordern: Header oder .eml-Datei, Vollmacht für die Abmahnung, Schadensnachweis, wenn kein Schaden gefordert wird. Wünscht der Nutzer ein „Bombardement“, das kurz begründen und diese Auswahl anbieten.

## Phase 5 – Gegenanwalt-Check

Wenn Subagenten verfügbar sind, einen starten, der als der abmahnende Anwalt agiert; sonst selbst in einem bewusst getrennten Durchgang die Gegenrolle einnehmen. Übergeben: Pfad zur Abmahnungs-PDF (Hinweis: Scan, seitenweise als Bild lesen) und den Antwortentwurf als Datei. Auftrag: das Schreiben so scharf wie möglich zerlegen, sortiert nach kritisch/mittel/gering, je Punkt (a) Problem, (b) wie er es ausnutzt, (c) Korrekturvorschlag; Fundstellen recherchieren und Verifikationsstatus angeben; keine erfundenen Fundstellen. Ausdrücklich prüfen lassen:

- UE-Wirksamkeit, Form und Unterschriften
- Zitate, auch Urteil oder Beschluss und Fundstelle
- Kostenargumente, besonders Sätze, die als ernsthafte Zahlungsverweigerung gelesen werden können (§ 250 BGB)
- Frist und Zugang
- Auskunftsstrategie und Zustellweg
- Website-Block: Aktivlegitimation, Nötigung, Beweislage jeder Feststellung
- Rückfragen
- Tatsachenbehauptungen und Eingeständnisse, etwa „nur eine Mail“ oder „in allen Systemen gesperrt“
- Hinweise auf die Versandinfrastruktur in Briefkopf und Absenderadresse
- Formalien

Danach jeden Punkt einarbeiten oder bewusst verwerfen und dem Nutzer knapp als Tabelle (Angriffspunkt → Korrektur) zeigen.

## Phase 6 – Rechtsprechungsprüfung

Jede Aussage gegen tatsächliche Entscheidungen prüfen, **im Volltext und mit Randnummer** (amtliche Portale, juris.bundesgerichtshof.de, NRWE, landesrecht-*.de); was nur in Blogs oder Leitsatz-Sammlungen steht, nicht zitieren. Jede Fundstelle der Gegenseite einzeln prüfen: Was trägt sie wirklich, ist sie veröffentlicht, ist eine Passage abgeschrieben? Fokus auf den **voraussichtlichen Gerichtsstand einer Kostenklage**: allgemeiner Gerichtsstand am Sitz des Abgemahnten (§§ 12, 13, 17 ZPO); ob § 32 ZPO (Empfangsort) bei der reinen Zahlungsklage auf Abmahnkosten greift, ist umstritten; der Sitz der Kanzlei begründet keine Zuständigkeit (Details: `references/01_rechtsprechung.md`; Amtsgerichte bis 10.000 € seit 01.01.2026). Regionale AG-Urteile über Landesjustizportale suchen (z. B. nrwe.justiz.nrw.de, gesetze-bayern.de, landesrecht-bw.de). Ergebnis als Prüfprotokoll: Aussage | Rechtsprechung | trägt / nicht haltbar / Risiko. Nicht haltbare Argumente streichen statt abschwächen. Bei Kostenablehnung das Prozessrisiko grob beziffern (Hauptforderung + 3,0 GKG-Gebühr + gegnerische Anwaltsgebühren + ggf. eigener Anwalt). Die Tabelle in `references/01_rechtsprechung.md` vor Nutzung per Websuche auf neue Entscheidungen prüfen.

## Phase 7 – Entscheidungen beim Nutzer abholen

Firmendaten des Nutzers selbst füllen (Impressum, Handelsregister/Northdata: Registergericht, HRB, Geschäftsführer, USt-ID, Kontakt). Dann – gebündelt, per Rückfragetool falls vorhanden – nur das klären, was nicht recherchierbar ist:

- **Kostenposition. Standard ist „erst Nachweis“ (Variante B):**
  - Um Darlegung der Kostenbelastung bitten und sie bis dahin mit Nichtwissen bestreiten (Baustein in `references/02_antwortbausteine.md`).
  - Bei Umsatzsteuer eine Rechnung des Abmahners nach § 14 UStG verlangen.
  - Ausdrücklich schreiben, dass eine Zahlung damit nicht abgelehnt wird.
  - Antwort binnen 14 Tagen nach Eingang zusagen.
  - Im selben Schreiben den Gegenstandswert begründet rügen.

  Die anderen Optionen nur auf ausdrücklichen Wunsch, je mit beziffertem Risiko:
  - Teilzahlung auf reduzierten Wert, ohne Anerkennung, wenn der Nutzer Ruhe will.
  - Volle Zahlung ohne Anerkennung, nur bei Stufe A mit Wert bis 3.000 €.
  - Ablehnung, nur bei Missbrauchsverdacht mit belegbaren Tatsachen.

  Dazu Erfahrungswerte aus dem Abgleich, falls vorhanden (Abo). Volle Zahlung nie von sich aus vorschlagen, nur weil sie bequem ist.
- Weitergabe-Satz zu Dienstleistern/AV-Verträgen: nur rein, wenn belegt; im Zweifel streichen
- Sperre umgesetzt? Formulierung neutral: „haben veranlasst, dass … keine Werbung mehr zugeht“. Nie „in allen Systemen gesperrt“, das verrät Massenversand.
- Gab es weitere Mails an den Abmahner (Follow-ups, Sequenzen)? Der Nutzer muss das intern prüfen. Gibt es welche, darf das Schreiben nicht von „einer E-Mail“ ausgehen.
- Versanddatum, Unterzeichner (bei der GbR alle Gesellschafter), PDF-Aufbau (Schreiben und UE getrennt ist praktisch zum Unterschreiben)
- Website-Hinweise aufnehmen? Nur gesicherte Punkte aus Modul W, höchstens 3–6.

## Phase 8 – PDFs bauen

Mit Python/reportlab (Platypus); falls nicht installiert, nachinstallieren. Schrift: Carlito (Calibri-metrisch), sonst Liberation Sans oder DejaVu Sans – vorher mit `fc-list` prüfen. Layout angelehnt an DIN 5008: Firmenkopf oben, Rücksendezeile, Anschriftfeld links, Infoblock rechts (Ihr Zeichen, Ihr Schreiben vom, Datum), Betreff fett, Fließtext Blocksatz 11 pt, Fußzeile mit Pflichtangaben nach § 35a GmbHG (Registergericht, HRB, Geschäftsführer, USt-ID, Kontakt) und Seitenzahl. Zwei Dateien: `JJJJ-MM-TT_Antwort_[Kanzlei]_[Az].pdf` und `JJJJ-MM-TT_Unterlassungserklaerung_[Firma]_[Abmahner].pdf`. Keine Platzhalter im Endprodukt. Vor dem Ausliefern die Seiten rendern (z. B. pdftoppm) und ansehen.

Briefkopf ohne Versand- oder Akquisedomain: Firma, Anschrift und Telefon genügen. Bei der GbR in der Fußzeile alle Gesellschafter.

Versandhinweise:

- **Form:**
  - **Kaufleute:** unterschriebene UE als PDF per E-Mail genügt (BGH I ZR 49/22).
  - **Nicht-Kaufleute** (GbR, Freiberufler, Kleingewerbe): Schriftform (§§ 780, 781 BGB; § 350 HGB gilt nur für Kaufleute). Vorab per E-Mail senden, Original per Einschreiben hinterher.
  - **GbR:** alle Gesellschafter unterschreiben (§ 720 BGB).
- **Kein Telefax:** Es wird nie per Fax versendet, auch wenn die Kanzlei eine Faxnummer nennt. Vorab geht alles nur per E-Mail. Lässt die Kanzlei zur Fristwahrung ausdrücklich nur ein Fax genügen, das Original noch am selben Tag per Einschreiben aufgeben, damit es binnen der genannten Werktage ankommt.
- **Absender:** aus einem Postfach senden, das nicht für Akquise genutzt wird. An alle Kanzlei-Adressen, mit Lesebestätigung.
- **Fristen:** vor Fristablauf versenden. Verlangt die Kanzlei das Original binnen weniger Werktage, Feiertage an beiden Orten einrechnen und den Termin für die Post nennen.
- **Datum:** Das Schreiben trägt den Versandtag. Verschiebt sich der Versand, das Datum in allen Dokumenten anpassen.

To-do-Liste:

- Sperre umsetzen: alle Domains und Adressen des Abmahners, in allen Kanälen (Mail, LinkedIn, Telefon, Messenger) und bei Dienstleistern. Dokumentieren.
- Laufende Sequenzen an den Abmahner stoppen.
- Auskunft nach Art. 15 bis zum Fristende erteilen: Quelle, Zwecke, Empfänger namentlich, Speicherdauer, Kopie der Daten.
- Art.-14-Information nachholen.

Ist der Nutzer ein Dienstleister, der den Fall für einen Kunden bearbeitet, zusätzlich ein Begleitschreiben an den Kunden: Fristen, Einschätzung, Kosten und Risiko je Variante, To-dos mit Datum, nächste Schritte. Darin **nie „Empfehlung“**, sondern „wir würden an Ihrer Stelle … vorgehen“, und **oben und am Ende der gerahmte Hinweis „keine Rechtsberatung“** (Wortlaut und Regeln in `references/02_antwortbausteine.md`, Abschnitt Begleitschreiben). Vor der Auslieferung jede Seite auf Überlauf prüfen.

## Phase 9 – Meldung des Abmahners (nach Zustimmung)

Am Ende des Falls bietet der Skill an, den Abmahner an den Server von Agentur Consulting zu melden. Die Meldung ist kostenlos und nicht öffentlich. Details: `references/06_sperrliste-server.md`, Beispiel: `beispiele/05_meldung-sperrliste.md`.

1. Dem Nutzer die Meldung in zwei, drei Zeilen zeigen: Domains (mit Quelle), Kanzlei-Domain, Stufe, Monat, Forderungsspanne, Art. 82 ja/nein, Vorgehen-Codes, Ausgang. Dazu: Die eigene Domain wird nur als nicht umkehrbarer Schlüssel gespeichert, damit unabhängige Meldungen gezählt werden können. Bei Bedarf vorher `--dry-run`.
2. **Fragen, ob gemeldet werden soll.** Nur bei einem klaren Ja senden:
   ```bash
   python3 scripts/sperrliste.py melden --domains abmahner.de abmahner-shop.de --kanzlei-domain kanzlei.de \
     --monat 2026-09 --forderung 1000-2000 --art82 ja \
     --vorgehen UE_MODIFIZIERT,ART82_ABGELEHNT --status offen --melder-domain eigene-firma.de \
     --einreichung NUMMER-AUS-DEM-CHECK
   ```
   - `--stufe`: ohne Angabe 5, wenn eine Kanzlei abgemahnt hat, sonst 4. Gerichtliches Verfahren: 6.
   - Bei „erst Nachweis“ (Variante B) noch keinen `KOSTEN_`-Code melden. Der Ausgang bleibt `offen`. Der Code (`KOSTEN_GEZAHLT`, `KOSTEN_VERGLEICH`, `KOSTEN_ABGELEHNT`) wird nachgemeldet, sobald die Kostenfrage entschieden ist.
3. Ergebnis nennen: Meldungs-Nr. oder Ablehnungsgrund des Servers. **Server nicht erreichbar** (Exit-Code 4): sagen, dass nichts gesendet wurde, und anbieten, es später erneut zu versuchen. Es gibt keinen Ersatzweg.
4. **Lehnt der Nutzer ab:** nicht senden, nicht drängen, normal weitermachen.
5. Ohne Code-Ausführung entfällt die Meldung.
6. **Ausgang später** (keine Reaktion, Mahnbescheid, Klage, Vergleich): dieselben Domains mit demselben `--monat` und derselben `--stufe` und neuem `--status` erneut melden, wieder nach Zustimmung.

Melde nie: Freemail- oder Plattformdomains, die Kanzlei als Abmahner, Domains ohne Beleg der Zugehörigkeit, die eigene Domain. Das Skript und der Server lehnen solche Meldungen zusätzlich ab.

Hinweis für den Nutzer mit Abo: Vor jeder E-Mail-Kampagne die Kontaktliste abgleichen:
```bash
python3 scripts/sperrliste.py abgleich --kontakte kontakte.csv --spalte email
```

## Phase 10 – Nachgang (wenn die Kanzlei antwortet)

Die feste Linie gilt auch nach dem Versand:

- **Darlegung oder Rechnung kommt:**
  - Prüfen: Rechnung des Abmahners (nicht der Kanzlei)? Umsatzsteuer gesondert ausgewiesen? Stimmen Wert und Betrag?
  - Binnen der zugesagten Frist zahlen, aber auf Basis des eigenen, begründeten Werts, ohne Anerkennung einer Rechtspflicht.
  - Dazu der Satz: „Einen darüber hinausgehenden Anspruch Ihrer Mandantin sehen wir nicht.“
- **Kanzlei verweigert Darlegung oder Rechnung** (oft mit „eigener Leistungsanspruch“, BFH XI R 27/14, und einer Liste von Streitwert-Entscheidungen): Alle Fundstellen im Volltext prüfen, Gegenanwalt-Check, dann dem Nutzer zwei Varianten mit beziffertem Risiko vorlegen: A Angebot auf begründetem Wert gegen Rechnung, B Ablehnung. Bausteine und Gegenargumente: `references/02_antwortbausteine.md` (Zweite Runde) und `references/01_rechtsprechung.md` (Kosten). Die Zahlungsfrist der Kanzlei ist dann meist abgelaufen; zügig antworten.
- **Nur Mahnung ohne Begründung:** Nicht von sich aus zahlen. Die Darlegung einmal sachlich erneut anfordern.
- **Änderungswünsche zur UE:** zügig prüfen. Berechtigte Wünsche übernehmen. Das sichert die Kostenposition nach § 93 ZPO.
- **Mahnbescheid:** binnen 2 Wochen Widerspruch einlegen und einen Anwalt beauftragen. Ebenso bei Klage, einstweiliger Verfügung oder Vertragsstrafe-Forderung.
- **Ausgang** nachmelden, nach Zustimmung (Phase 9, Punkt 6).

## Modul W – Website-Verstöße des Abmahners

Nur auf Wunsch. Ablauf: Rahmen klären → prüfen → sichern → protokollieren → auswählen.

1. **Rahmen** (`references/03_website-pruefraster.md`, Abschnitt M1): Mitbewerber oder branchenfremd? Kein eigener Schaden, keine Gegendrohung, keine Formulare absenden.
2. **Prüfen** nach dem Raster in `references/03_website-pruefraster.md`. Die Spalte „Typischer Fehlgriff“ ist verbindlich.
3. **Sichern** nach `references/04_beweissicherung.md`: `scripts/sicherung_netzwerk.py` (Szenarien A/B/C), `scripts/sicherung_seiten.py`, `scripts/auswertung.py` (ordnet Drittserver über `listen/drittanbieter.csv` zu und liest den Consent-Status über `listen/consent-tools.csv`), `scripts/integritaet.sh` (SHA-256 + zwei RFC-3161-Zeitstempel).
4. **Protokoll** als PDF nach der Gliederung in `beispiele/04_beweisprotokoll-gliederung.md`, inklusive Grenzen und Hinweisen (Zeugenwiederholung, archive.org, Notar).
5. **Auswahl** von höchstens 3–6 gesicherten Punkten und neutrale Formulierung nach `references/02_antwortbausteine.md`, Abschnitt „Website-Block“.

## Hinweise für künftige Kampagnen

Am Ende kurz mitgeben, wie die Akquise sauber weiterläuft: keine frisch registrierten Versanddomains ohne Website und Impressum; nach einer Abmahnung Kampagne, Liste und Vorlagen durchsehen, denn zwei Abmahnungen in wenigen Wochen sind ein Muster; fingierte Aufhänger („Kollege hat mich aufmerksam gemacht“, falsche Weiterleitungen) aus Vorlagen streichen (§ 6 DDG), Footer mit Rechtsträger und Anschrift (§ 7 Abs. 2 Nr. 3 UWG), Art.-14-Information beachten, Kontaktlisten vor jedem Versand abgleichen (mit Abo: `sperrliste.py abgleich`). Nicht vor E-Mail-Akquise warnen.
