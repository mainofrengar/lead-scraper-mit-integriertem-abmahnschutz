<!-- Fassung vom 2026-11-04, anwaltlich abgenommen.
     Diese Datei gibt es dreimal, identisch: im Hauptordner, in lead-scraper/ und in abmahnung-werbemail-abwehr/. -->

# Nutzungsbedingungen

**Version 2026-11** · Stand 4. November 2026

## 1. Anbieter und Geltung

Anbieter ist Benjamin Wünsche, Am Zuckerberg 87, 71640 Ludwigsburg, E-Mail: support@ak.consulting (im Folgenden „Betreiber“).

Diese Bedingungen gelten für:
- das Paket „Akquise & Abmahnschutz“: den Lead-Scraper und die Claude-Skills „lead-scraper“ und „abmahnung-werbemail-abwehr“;
- die Dienste auf dem Server des Betreibers: Lizenzschlüssel, Sperrliste, Abmahnungs-Check, Meldungen, Adresssperren, Instantly-Anbindung und das Abo.

Sie gelten in der Version, die beim Anlegen des Lizenzschlüssels angezeigt wird. Abweichende Bedingungen des Nutzers gelten nicht.

## 2. Nur für Unternehmer

Paket und Dienste sind nur für Unternehmer im Sinne von § 14 BGB bestimmt, also für Nutzung in gewerblicher oder selbständiger beruflicher Tätigkeit. Mit der Nutzung bestätigt der Nutzer, dass er Unternehmer ist. Verbraucher dürfen Paket und Dienste nicht nutzen.

## 3. Lizenzschlüssel

1. Beim ersten Aufruf legt das Paket automatisch einen kostenlosen Lizenzschlüssel an (Free-Plan). Ein Schlüssel gilt für einen Rechner und alle Pfade und Skills darauf.
2. Der Schlüssel ist geheim zu halten und darf nicht weitergegeben werden. Wer ihn verliert, legt einen neuen an. Ein Abo hängt am Schlüssel, für den es abgeschlossen wurde.
3. Auf dem Server liegt nur ein Hash des Schlüssels. Der Betreiber kann einen Schlüssel sperren, wenn er missbraucht wird (Ziffer 8).

## 4. Leistungen

1. **Free-Plan (kostenlos):** Abmahnungs-Check im Skill, Meldungen, Adresssperren, Pro-Hinweise. Einen Sperrlisten-Abgleich gibt es im Free-Plan nicht; dort steht „Kostenpflichtige Features können im Free-Plan nicht verwendet werden“.
2. **Abo (kostenpflichtig):** zusätzlich der abgestufte Sperrlisten-Abgleich beim Export, die Abmahner-Frühwarnung, der Premium-Support (Bearbeitung technischer Anfragen über das Supportformular) und die Instantly-Anbindung. Fragen zu Abo, Rechnung, Kündigung und Datenschutz beantwortet der Betreiber auch im Free-Plan.
3. Die Sperrliste ist nicht öffentlich. Sie ist nur über den Abgleich einzelner Einträge zugänglich. Einen Download, einen Export oder eine Einsicht in die ganze Liste gibt es in keinem Plan.
4. Der Betreiber kann die Dienste weiterentwickeln. Wesentliche Einschränkungen eines laufenden Abos kündigt er mindestens sechs Wochen vorher an; der Nutzer kann dann zum Zeitpunkt der Änderung kündigen.
5. Eine bestimmte Verfügbarkeit des Servers ist nicht geschuldet. Wartung und Ausfälle sind möglich. Mit Abo und ohne erreichbaren Server exportiert das Paket nicht, damit keine ungeprüfte Liste entsteht (`lead-scraper/wissen/09_sperrliste.md`).

## 5. Abo, Preis und Kündigung

1. Das Abo wird über Stripe abgeschlossen. Es gilt der Preis, der im Stripe-Checkout angezeigt wird, zuzüglich gesetzlicher Umsatzsteuer, soweit ausgewiesen.
2. Das Abo läuft monatlich und verlängert sich jeweils um einen Monat. Es kann jederzeit zum Ende des laufenden Abrechnungsmonats gekündigt werden, im Kundenportal (`abo`-Befehl des Pakets) oder per E-Mail an den Betreiber.
3. Bei Zahlungsverzug kann der Betreiber die Abo-Leistungen aussetzen, bis die Zahlung eingegangen ist. Der Schlüssel fällt dann auf den Free-Plan zurück.
4. Preisänderungen kündigt der Betreiber mindestens sechs Wochen vorher an. Sie gelten ab dem nächsten Abrechnungsmonat, wenn der Nutzer nicht vorher kündigt.

## 6. Datenweitergabe im Free-Plan

**Diese Klausel gilt in jedem Plan, auch im kostenlosen.**

1. Nach jedem Export überträgt das Paket die exportierten Leads an den Server des Betreibers. Das geschieht automatisch und ohne eigene Meldung beim Export.
2. Übertragen werden:
   - Firmendaten: Name, Website, Domain, Anschrift, Telefon, Branche, Handelsregister;
   - Ansprechpartner, soweit vorhanden: Anrede, Vorname, Nachname, Position, E-Mail-Adresse, Art und Prüfstatus der Adresse;
   - Herkunft: externe ID, Quelle, Quell-URL, Erfassungsdatum.
   
   Nicht übertragen werden Personalisierungen, Mailtexte, API-Schlüssel, Einstellungen und Prompts.
3. Der Betreiber speichert die Leads als eigener Verantwortlicher in einer internen Datenbank. Er nutzt sie für die Sperrliste und den Abgleich, für die Verbesserung seiner Dienste und für eigene Geschäftszwecke. Er verkauft die Leads nicht und gibt sie nicht an Dritte weiter. Zugriff haben nur ausgewählte Personen des Betreibers mit persönlichem Zugangsschlüssel. Einzelheiten, Speicherdauer und Rechte der Betroffenen stehen in der Datenschutzerklärung (`DATENSCHUTZ.md`).
4. Der Nutzer räumt dem Betreiber das Recht ein, die übertragenen Leads für diese Zwecke zu nutzen, solange sie nach der Datenschutzerklärung gespeichert werden. Ein Entgelt dafür steht dem Nutzer nicht zu; die Übertragung ist Teil der Gegenleistung für den Free-Plan.
5. Wer die Übertragung nicht will, darf das Paket nicht nutzen. Ein Abschalten der Übertragung ist nicht vorgesehen und nicht erlaubt.

## 7. Hinweispflicht des Nutzers

1. Der Nutzer erhebt die Leads in eigener Verantwortung. Er stellt sicher, dass er sie erheben, nutzen und an den Betreiber übertragen darf.
2. In seiner Datenschutzinformation gegenüber angeschriebenen Personen (Art. 13, 14 DSGVO) nennt der Nutzer den Betreiber als Empfänger der Kontaktdaten. Ein Formulierungsvorschlag steht in `DATENSCHUTZ.md`, Abschnitt „Für Nutzer“.
3. Die Pro-Hinweise des Servers dürfen nicht entfernt oder unterdrückt werden. „Kostenfrei reicht“ blendet sie auf dem vorgesehenen Weg aus.

## 8. Pflichten bei Meldungen und Nutzung

1. **Gegenseitigkeit:** Wer wegen einer Werbe-E-Mail abgemahnt wird oder eine Drohung erhält, meldet den Absender. Davon lebt die Sperrliste. Gesendet wird eine Meldung erst nach Bestätigung durch den Nutzer im Einzelfall; der Skill zeigt vorher an, was übermittelt wird.
2. Gemeldet werden nur tatsächlich erhaltene Abmahnungen, Drohungen oder Widersprüche, und nur Domains, die nachweislich dem Absender gehören (Impressum, Schreiben, Handelsregister). Keine Meldungen über Wettbewerber oder Dritte zu anderen Zwecken. Wer bewusst falsch meldet, haftet dafür.
3. Nicht erlaubt sind: die Sperrliste oder den Lead-Bestand systematisch auszulesen, etwa durch massenhafte oder erfundene Abfragen; Abfragelimits zu umgehen; Abgleichsergebnisse an Dritte weiterzugeben oder zu verkaufen; den Schlüssel zu teilen; die Software so zu verändern, dass Übertragung oder Hinweise entfallen.
4. Bei Verstößen kann der Betreiber den Schlüssel sperren. Bei einem laufenden Abo kann er fristlos kündigen, wenn der Verstoß erheblich ist.

## 9. Versand und Recht

Für Inhalt und Zulässigkeit seiner Werbung ist allein der Nutzer verantwortlich, insbesondere nach UWG und DSGVO. Die Sperrliste kennt nur gemeldete Fälle; Abmeldeweg, Widerspruchsprozess und Blockliste im Versandtool ersetzt sie nicht. Ein Eintrag sagt nur, dass sich ein Unternehmen gegen Werbe-E-Mails gewehrt hat, nicht, ob das berechtigt war.

## 10. Keine Rechtsberatung

Paket, Skills, Abmahnungs-Check und Sperrliste geben allgemeine Informationen und zeigen, wie der Betreiber mit einem Fall umgehen würde („So würden wir damit umgehen“). Sie sind keine Rechtsdienstleistung im Sinne des Rechtsdienstleistungsgesetzes (RDG) und ersetzen keine anwaltliche Beratung im Einzelfall. Ein Mandats- oder Beratungsverhältnis entsteht nicht. Wer abgemahnt wird, sollte eine Rechtsanwältin oder einen Rechtsanwalt hinzuziehen.

## 11. Haftung

1. Der Betreiber haftet unbeschränkt bei Vorsatz und grober Fahrlässigkeit, bei Verletzung von Leben, Körper oder Gesundheit, nach dem Produkthaftungsgesetz und soweit er eine Garantie übernommen hat.
2. Im Abo haftet er bei leichter Fahrlässigkeit nur für die Verletzung wesentlicher Vertragspflichten, also solcher, deren Erfüllung die Durchführung des Vertrags erst ermöglicht und auf die der Nutzer vertrauen darf. Die Haftung ist dann auf den vertragstypischen, vorhersehbaren Schaden begrenzt, höchstens auf die Abo-Entgelte der letzten zwölf Monate.
3. Im Free-Plan haftet der Betreiber nur nach Absatz 1.
4. Für Vollständigkeit und Richtigkeit der Sperrliste und der Einordnungen wird keine Gewähr übernommen. Sie beruhen auf Meldungen anderer Nutzer und auf automatischer Einordnung.

## 12. Freistellung

Der Nutzer stellt den Betreiber von Ansprüchen Dritter frei, die daraus entstehen, dass der Nutzer Werbung versendet, Leads unzulässig erhebt oder überträgt, falsch meldet oder gegen diese Bedingungen verstößt. Das umfasst angemessene Kosten der Rechtsverteidigung. Das gilt nicht, soweit der Nutzer die Verletzung nicht zu vertreten hat.

## 13. Widerspruch gelisteter Unternehmen

Gelistete Unternehmen können beim Betreiber widersprechen (Kontakt in Ziffer 1, Ablauf in `DATENSCHUTZ.md`, Abschnitt „Widerspruch gegen die Listung“). Nach einem berechtigten Widerspruch wird die Domain aus jedem Abgleich entfernt und nicht wieder aufgenommen.

## 14. Änderungen dieser Bedingungen

Neue Versionen zeigt das Paket beim nächsten Anlegen eines Schlüssels an und legt sie dem Paket bei. Für ein laufendes Abo gilt eine neue Version erst, wenn der Betreiber sie mindestens sechs Wochen vorher per E-Mail angekündigt hat und der Nutzer nicht bis zum Inkrafttreten kündigt. Auf diese Folge weist die Ankündigung hin.

## 15. Schluss

Es gilt deutsches Recht unter Ausschluss des UN-Kaufrechts. Gerichtsstand für Kaufleute, juristische Personen des öffentlichen Rechts und öffentlich-rechtliche Sondervermögen ist der Wohnsitz des Betreibers. Sollte eine Bestimmung unwirksam sein, bleibt der Rest wirksam.
