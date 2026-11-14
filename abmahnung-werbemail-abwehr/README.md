# Skill „Abmahnung Werbe-E-Mail – Prüfung & Abwehr“

Ein Claude-Skill für Unternehmen, die wegen einer Werbe-E-Mail (Cold-Mail) abgemahnt wurden. Claude prüft die Abmahnung, recherchiert Kanzlei und Rechtsprechung, holt den kostenlosen Abmahnungs-Check „So würden wir damit umgehen“ vom Server von Agentur Consulting und erstellt ein versandfertiges Antwortschreiben samt modifizierter Unterlassungserklärung als PDF. Optional prüft und sichert Claude Rechtsverstöße auf der Website des Abmahners.

**Wichtig – keine Rechtsberatung:** Der Skill liefert Recherche und Entwürfe. Er ersetzt keine anwaltliche Beratung. Bei Klage, einstweiliger Verfügung, hohen Beträgen oder Unsicherheit einen Anwalt einschalten.

## Installation (2 Minuten, keine Einrichtung)

1. In Claude: **Einstellungen → Funktionen → Skills → Skill hochladen** und diese ZIP-Datei auswählen.
2. Fertig. Empfohlen ist eingeschaltete Code-Ausführung; ohne sie funktioniert der Skill auch, nur ohne Abmahnungs-Check, Meldung und Beweissicherung.

Für Abmahnungs-Check, Meldung, Abgleich und Beweissicherung muss die Umgebung den Server `leads-db.akconsulting.cloud`, die Zeitstempeldienste (`zeitstempel.dfn.de`, `timestamp.sectigo.com`) und die Website des Abmahners erreichen dürfen. Der kostenlose Lizenzschlüssel wird beim ersten Aufruf automatisch angelegt.

## Nutzung

Abmahnung als PDF in den Chat legen und schreiben: „Ich habe diese Abmahnung wegen einer Werbe-Mail bekommen, bitte prüfen.“ Claude führt durch die Schritte und fragt nur nach, was sich nicht recherchieren lässt.

## Server von Agentur Consulting

Es gibt keine öffentliche Liste. Abmahnungen, Meldungen und die Sperrliste liegen nur auf dem Server von Agentur Consulting und werden nie ausgegeben: Nutzer und Partner erhalten nur das Ergebnis des Abgleichs für selbst geprüfte Einträge. Details und Datenformat: `references/06_sperrliste-server.md`.

- **Abmahnungs-Check (kostenlos):** Claude sagt vorher, dass die Eckdaten der Abmahnung an den Server gehen und dort gespeichert werden. Gesendet wird nur, was das Format vorsieht, ohne Namen, E-Mail-Adressen und Mail-Inhalte. Die Antwort „So würden wir damit umgehen“ endet immer mit dem Hinweis „Keine Rechtsberatung …“.
- **Meldung (kostenlos):** Am Ende fragt Claude, ob der Abmahner gemeldet werden soll. Gemeldet werden nur Domains und Sachangaben: Kanzlei-Domain, Stufe, Monat, Forderungsspanne, Vorgehen, Ausgang. Keine E-Mail-Adressen, keine Namen.
- **Abgestufter Abgleich (nur mit Abo):** Ist der Abmahner bekannt, mit welcher Stufe? Vor jeder Kampagne die Kontaktliste bereinigen:
  ```bash
  python3 scripts/sperrliste.py abgleich --kontakte kontakte.csv --spalte email   # schreibt _bereinigt.csv und _gesperrt.csv
  ```
  Im Free-Plan erscheint „Kostenpflichtige Features können im Free-Plan nicht verwendet werden“. Abo: `python3 scripts/lizenz.py abo`.

## Ordnerstruktur

```
abmahnung-werbemail-abwehr/
├── SKILL.md                    Ablaufsteuerung für Claude
├── README.md · CHANGELOG.md · NUTZUNGSBEDINGUNGEN.md · DATENSCHUTZ.md
├── references/                 Fachwissen, wird phasenweise geladen
├── listen/                     Drittserver und Consent-Tools (fest)
├── beispiele/                  fiktive Musterfälle
└── scripts/
    ├── sperrliste.py           Abmahnungs-Check, Meldung, Abgleich (Server)
    ├── lizenz.py               Lizenzschlüssel und Server-Zugriff (gleiche Datei wie im Lead-Scraper)
    ├── test_sperrliste.py      Offline-Tests gegen einen lokalen Test-Server
    ├── sicherung_netzwerk.py   Browser-Mitschnitt in drei Szenarien
    ├── sicherung_seiten.py     Seitensicherung (HTML, PNG, PDF, MHTML)
    ├── auswertung.py           Zuordnung Drittserver + Consent-Status
    └── integritaet.sh          SHA-256 + RFC-3161-Zeitstempel
```

## Hinweise

- Die Inhalte entsprechen dem Rechtsstand Oktober 2026; Claude prüft vor jeder Nutzung per Websuche auf Neuerungen. Eine Gewähr für Vollständigkeit und Richtigkeit wird nicht übernommen.
- Fragen zu gespeicherten Daten, Widerspruch oder Löschung: an den Betreiber (Kontakt und Ablauf in `DATENSCHUTZ.md`).
