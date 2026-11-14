<!-- Fassung vom 2026-11-04, anwaltlich abgenommen.
     Diese Datei gibt es dreimal, identisch: im Hauptordner, in lead-scraper/ und in abmahnung-werbemail-abwehr/. -->

# Datenschutzerklärung

**Version 2026-11** · Stand 4. November 2026

Diese Erklärung gilt für das Paket „Akquise & Abmahnschutz“ und die Dienste auf dem Server des Betreibers. Sie richtet sich an drei Gruppen:
- **Nutzer** des Pakets;
- **Personen in hochgeladenen Leads**, also Ansprechpartner und Einzelunternehmer, deren Daten ein Nutzer exportiert hat;
- **gemeldete Unternehmen**, also Firmen und Kanzleien auf der Sperrliste.

## 1. Verantwortlicher

Benjamin Wünsche, Am Zuckerberg 87, 71640 Ludwigsburg, E-Mail: support@ak.consulting

Ein Datenschutzbeauftragter ist nicht benannt.

## 2. Was lokal bleibt

Der Lead-Scraper läuft auf dem Rechner des Nutzers. Suchanfragen, Rohantworten der Datendienste, Personalisierungen, Mailtexte, Einstellungen und API-Schlüssel bleiben dort und erreichen den Betreiber nicht. Dienste, die der Nutzer mit eigenem Konto einbindet (etwa Datendienste, KI-Anbieter, Mailtools), verarbeiten Daten in seiner Verantwortung. Diese Erklärung deckt sie nicht ab.

## 3. Verarbeitungen auf dem Server

### 3.1 Lizenzschlüssel (alle Nutzer)

- **Daten:** Hash des Schlüssels, die ersten 12 Zeichen (für den Support), Typ, Zeitpunkt des Anlegens und der letzten Nutzung, Version der beim Anlegen angezeigten Nutzungsbedingungen. Die IP-Adresse beim Anlegen nur als verschlüsselter Hash, um massenhaftes Anlegen zu verhindern.
- **Zweck und Rechtsgrundlage:** Bereitstellung der Dienste (Art. 6 Abs. 1 lit. b DSGVO), Schutz vor Missbrauch (Art. 6 Abs. 1 lit. f DSGVO).
- **Speicherdauer:** IP-Hash zwei Tage. Schlüssel, solange er genutzt wird; auf Anfrage wird er gelöscht.

### 3.2 Abo und Zahlung

- **Daten:** E-Mail-Adresse, Stripe-Kunden-ID, Status und Zeitraum des Abos. Zahlungsdaten (Karte, Konto) gibt der Nutzer direkt bei Stripe ein; der Betreiber sieht sie nicht.
- **Zweck und Rechtsgrundlage:** Abschluss und Abwicklung des Abos (Art. 6 Abs. 1 lit. b DSGVO), steuer- und handelsrechtliche Aufbewahrung (Art. 6 Abs. 1 lit. c DSGVO).
- **Empfänger:** Stripe Payments Europe Ltd., Irland, für die Zahlungsabwicklung.
- **Speicherdauer:** bis zum Ende des Abos; Rechnungs- und Buchungsdaten nach den gesetzlichen Fristen (bis zu zehn Jahre).

### 3.3 Hochgeladene Leads (Datenweitergabe im Free-Plan)

Nach jedem Export überträgt das Paket die exportierten Leads an den Server, auch im Free-Plan (Nutzungsbedingungen, Ziffer 6). Für Personen in diesen Leads ist das die Information nach Art. 14 DSGVO.

- **Daten:** Firmendaten (Name, Website, Domain, Anschrift, Telefon, Branche, Handelsregister); Ansprechpartner, soweit vorhanden (Anrede, Vorname, Nachname, Position, geschäftliche E-Mail-Adresse, Art und Prüfstatus der Adresse); Herkunft (Quelle, Quell-URL, Erfassungsdatum). Bei Einzelunternehmern sind auch die Firmendaten personenbezogen.
- **Quelle:** Der Nutzer hat die Daten mit dem Lead-Scraper aus öffentlich zugänglichen Quellen erhoben, etwa Unternehmenseinträgen in Kartendiensten, Impressen, Verkäuferprofilen und Stellenanzeigen. Die genaue Quelle ist je Lead gespeichert und wird auf Anfrage mitgeteilt.
- **Zweck:** Pflege einer internen Firmendatenbank des Betreibers; Abgleich mit der Sperrliste, damit Firmen, die keine Werbung wünschen, nicht angeschrieben werden; mit Abo die Abmahner-Frühwarnung an den Nutzer selbst, wenn eine Firma aus seinen Listen später als Abmahner bestätigt wird; Verbesserung der Dienste; eigene Geschäftszwecke des Betreibers.
- **Rechtsgrundlage:** berechtigtes Interesse (Art. 6 Abs. 1 lit. f DSGVO). Es umfasst die genannten Zwecke. Es werden nur geschäftliche Kontaktdaten verarbeitet, die ohnehin öffentlich sind.
- **Empfänger:** keine. Die Leads werden nicht verkauft und nicht an Dritte weitergegeben. Zugriff haben nur ausgewählte Personen des Betreibers mit persönlichem Zugangsschlüssel. Technisch eingebunden ist der Hosting-Dienstleister (Abschnitt 4).
- **Speicherdauer:** 24 Monate ab dem letzten Upload desselben Leads. Danach werden Ansprechpartner, Firmendaten und die hochgeladenen Listen in einem nächtlichen Lauf gelöscht.
- **Widerspruch:** Betroffene können der Verarbeitung jederzeit widersprechen (Art. 21 DSGVO), formlos per E-Mail an den Verantwortlichen. Ihre Daten werden dann gelöscht und die Adresse gesperrt, damit sie nicht erneut aufgenommen wird.

### 3.4 Sperrliste und Meldungen

- **Daten:** Domains von Unternehmen, die sich gegen Werbe-E-Mails gewehrt haben, und ihrer Kanzleien; dazu Stufe (von Beschwerde bis Gericht), Monat, Forderungsspanne, ob Schadensersatz nach Art. 82 DSGVO verlangt wurde, Vorgehen, Ausgang und Status. Der meldende Nutzer wird nur als verschlüsselter Hash seiner Domain gespeichert, nicht mit Namen.
- **Quelle:** Meldungen von Nutzern (nur nach Zustimmung im Einzelfall), automatische Einordnung von Instantly-Antworten (3.6), eigene Fälle des Betreibers.
- **Zweck und Rechtsgrundlage:** Nutzer davor zu bewahren, Unternehmen anzuschreiben, die keine Werbung wünschen oder schon abgemahnt haben (Art. 6 Abs. 1 lit. f DSGVO). Bei Unternehmen ohne Bezug zu einer natürlichen Person gilt die DSGVO nicht; bei Einzelunternehmern mit Namensdomain schon.
- **Empfänger:** Nutzer mit Abo erhalten für einen von ihnen geprüften Eintrag nur das Ergebnis (sperren, warnen, frei) und bei einem Treffer die Stufe. Die ganze Liste, Zählungen, Daten oder Angaben zu Meldern und Kanzleien erhält niemand.
- **Speicherdauer:** solange der Eintrag dem Zweck dient. Nach einem berechtigten Widerspruch wird die Domain entfernt (Abschnitt 6).

### 3.5 Adresssperren

- **Daten:** E-Mail-Adressen, die nicht mehr angeschrieben werden sollen (Austragung, Widerspruch, Beschwerde), nur als verschlüsselter Hash, mit Grund und Datum.
- **Zweck und Rechtsgrundlage:** einen Werbewiderspruch dauerhaft zu beachten (Art. 6 Abs. 1 lit. c und f DSGVO).
- **Speicherdauer:** dauerhaft, weil sonst der Widerspruch nicht beachtet werden könnte.

### 3.6 Abmahnungs-Check

- **Daten:** die Angaben zur Abmahnung, die der Nutzer im Skill einreicht: eigenes Unternehmen, Abmahner, Kanzlei, Fristen, Forderungen, beanstandete E-Mails und Zitate. Kontaktdaten des Nutzers nur mit seiner Einwilligung. Dokumente werden vom Skill nicht hochgeladen.
- **Zweck und Rechtsgrundlage:** die Antwort „So würden wir damit umgehen“ zu erstellen, Kanzleien auf Echtheit zu prüfen und die Sperrliste zu verbessern (Art. 6 Abs. 1 lit. b und f DSGVO; Kontaktdaten lit. a).
- **Speicherdauer:** drei Jahre nach Ende des Jahres, in dem die Angaben eingereicht wurden. Danach werden die Einreichung, der daraus angelegte Fall und die Angaben zum eigenen Unternehmen gelöscht. Meldungen zur Sperrliste enthalten keinen Freitext und bleiben nach Abschnitt 3.4 bestehen.

### 3.7 Instantly-Anbindung (Abo)

- **Daten:** der Instantly-API-Schlüssel des Nutzers, verschlüsselt gespeichert; eingehende Antworten aus Instantly (Betreff und Text); die Leads des Nutzers in Instantly während des nächtlichen Abgleichs.
- **Verarbeitung:** Der Text einer Antwort geht zur Einordnung (Absage, Austragung, Beschwerde, Drohung, Abmahnung) an die Schnittstelle von Anthropic. Gespeichert wird nur das Ergebnis, nicht der Text. Beim nächtlichen Abgleich werden die Leads des Nutzers in Instantly geprüft; nur Treffer werden in seine Instantly-Sperrliste eingetragen. Die Leads selbst werden dabei nicht gespeichert.
- **Zweck und Rechtsgrundlage:** Abo-Leistung (Art. 6 Abs. 1 lit. b DSGVO); Austragungen und Widersprüche zu beachten (lit. c und f).
- **Empfänger:** Anthropic PBC, USA, als Auftragsverarbeiter. Die Übermittlung erfolgt auf Grundlage der EU-Standardvertragsklauseln. Instantly verarbeitet die Daten im Auftrag des Nutzers.
- **Speicherdauer:** API-Schlüssel bis zur Trennung (`instantly trennen`) oder zum Ende des Abos.

### 3.8 Support

- **Daten:** Angaben im Supportformular auf ak.consulting/support (Thema, die ersten 12 Zeichen des Lizenzschlüssels, Beschreibung, optional ein Link zu einem Video, Name, Firma, E-Mail-Adresse), das hochgeladene Support-Paket, E-Mails an den Support sowie ein verschlüsselter Hash der IP-Adresse, um massenhafte Anfragen zu verhindern. Das Support-Paket enthält Betriebssystem, Python-Version, Programmstand, die ersten 12 Zeichen des Lizenzschlüssels, die Namen der Einstellungen und eine Dateiliste. Es enthält keine Leads, keine Schlüssel und keine E-Mail-Adressen. Ein verlinktes Video liegt beim jeweiligen Anbieter; der Betreiber ruft es nur auf.
- **Zweck und Rechtsgrundlage:** Bearbeitung der Anfrage und Prüfung, ob ein Abo besteht (Art. 6 Abs. 1 lit. b und f DSGVO). Bestätigung und Antwort gehen per E-Mail an die angegebene Adresse.
- **Speicherdauer:** Die Anfrage samt Support-Paket wird 12 Monate nach dem Eingang gelöscht. E-Mails zum Vorgang werden nach den gesetzlichen Fristen gelöscht.

### 3.9 Abfrageprotokoll

Jeder Aufruf wird mit Zeitpunkt, Art, Anzahl und Trefferzahl protokolliert, ohne die geprüften Werte. Das dient der Abrechnung von Limits und dem Schutz vor Missbrauch (Art. 6 Abs. 1 lit. f DSGVO). Die Protokolle werden nach 24 Monaten gelöscht.

## 4. Hosting

Der Server steht bei der Hetzner Online GmbH in Deutschland, die als Auftragsverarbeiter tätig ist. Verbindungen sind verschlüsselt (HTTPS).

## 5. Automatisierte Entscheidungen

Die Einordnung von Antworten und die Stufen der Sperrliste werden automatisch gebildet. Sie entscheiden nur, ob ein Nutzer ein Unternehmen anschreiben sollte. Eine Entscheidung mit rechtlicher Wirkung gegenüber einer Person im Sinne von Art. 22 DSGVO ist das nicht.

## 6. Widerspruch gegen die Listung

Ein Unternehmen, das auf der Sperrliste steht, kann der Listung jederzeit per E-Mail an den Verantwortlichen widersprechen. Nötig sind die Domain und ein Nachweis, dass der Absender für sie spricht (etwa eine E-Mail von dieser Domain). Nach einem berechtigten Widerspruch wird die Domain aus jedem Abgleich entfernt und auf eine Widerspruchsliste gesetzt, damit sie nicht wieder aufgenommen wird.

## 7. Rechte der Betroffenen

Jede betroffene Person hat das Recht auf Auskunft (Art. 15 DSGVO), Berichtigung (Art. 16), Löschung (Art. 17), Einschränkung der Verarbeitung (Art. 18), Datenübertragbarkeit (Art. 20) und Widerspruch (Art. 21). Eine erteilte Einwilligung kann jederzeit mit Wirkung für die Zukunft widerrufen werden. Anfragen per E-Mail an den Verantwortlichen.

Außerdem besteht das Recht, sich bei einer Datenschutz-Aufsichtsbehörde zu beschweren (Art. 77 DSGVO), etwa bei der Behörde am eigenen Wohnort oder am Wohnsitz des Verantwortlichen.

## Für Nutzer: Hinweis in der eigenen Datenschutzinformation

Wer angeschriebene Personen nach Art. 13 oder 14 DSGVO informiert, nennt den Betreiber als Empfänger (Nutzungsbedingungen, Ziffer 7). Vorschlag:

> Ihre geschäftlichen Kontaktdaten (Firma, Name, Position, E-Mail-Adresse, Quelle) übermitteln wir an Benjamin Wünsche, Am Zuckerberg 87, 71640 Ludwigsburg, der sie als eigener Verantwortlicher zum Abgleich mit einer Sperrliste und zur Pflege einer Firmendatenbank verarbeitet. Dort können Sie der Verarbeitung jederzeit widersprechen: support@ak.consulting.

Keine Rechtsberatung. Ob dieser Hinweis im Einzelfall genügt, sollte der Nutzer prüfen lassen.
