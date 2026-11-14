# Support

**Zweck:** wie man Hilfe bekommt: Support-Paket, Supportformular auf ak.consulting/support, was drin ist und was nicht.
**Für wen:** Nutzer und KI-Modelle, die bei einem Fehler weiterhelfen sollen.
**Verwandt:** `12_fehlerbehebung-faq.md` · `09_sperrliste.md` · `werkzeuge/lizenz.py`

---

## Erst selbst prüfen

1. `doctor` des Pfads ausführen (`python3 -m scraper doctor` bzw. `python3 -m ecom doctor`). Er prüft Zugänge, Prompts, Erreichbarkeit und die Lizenz.
2. `12_fehlerbehebung-faq.md` durchsehen.

## Wenn der Nutzer Support braucht

Sagt der Nutzer „Ich brauche Support“, oder kommt ein Fehler mit `doctor` und FAQ nicht weg:

1. Aus dem Gespräch Thema, „Wobei“ und eine kurze Beschreibung ableiten (Werte unten). Die Beschreibung enthält: was der Nutzer tun wollte, was passiert ist, die Fehlermeldung wörtlich, seit wann.
2. Den Befehl selbst ausführen:

   ```bash
   python3 -m scraper support --thema export_sperrliste --anliegen fehler --beschreibung "Export bricht nach Liste 2 ab. Fehlermeldung: …"
   ```

   Gleich in jedem Pfad: `python3 -m ecom support …` oder `python3 werkzeuge/lizenz.py support …`. `support-paket` ist derselbe Befehl.
3. Die Ausgabe geordnet an den Nutzer weitergeben, als Liste der Formularfelder 1 bis 7. Der Befehl öffnet die Seite **https://ak.consulting/support** im Browser.
4. **Ohne Abo** steht vor der Liste der Hinweis, dass technischer Support (Premium-Support) Teil des Abos ist. Diesen Hinweis zuerst und deutlich weitergeben, mit dem Befehl zum Abschließen (`… abo`). Der Nutzer kann die Anfrage trotzdem senden; er bekommt dann automatisch eine Mail mit dem Link zum Abo, und die Anfrage wird erst mit Abo bearbeitet. Fragen zu Abo, Rechnung, Kündigung und Datenschutz werden auch ohne Abo beantwortet.

Die Lizenz-Kennung sind die ersten 12 Zeichen des Lizenzschlüssels (`aks_…`). **Nie den vollständigen Schlüssel** ins Formular, in eine Mail oder in den Chat schreiben.

## Formularfelder

| Nr. | Feld | Woher |
|---|---|---|
| 1 | Thema | `--thema`, vom KI-Modell aus dem Gespräch |
| 2 | Wobei | `--anliegen`, vom KI-Modell aus dem Gespräch |
| 3 | Lizenz-Kennung | vom Befehl (erste 12 Zeichen) |
| 4 | Support-Paket (ZIP hochladen) | vom Befehl, liegt auf dem Schreibtisch |
| 5 | Beschreibung | `--beschreibung`, vom Nutzer prüfen lassen |
| 6 | Video (optional) | Link zu einer Bildschirmaufnahme (Loom, YouTube nicht gelistet, Google Drive), freigegeben für alle mit dem Link |
| 7 | Kontakt | Name, Firma, E-Mail für die Antwort |

**Thema** (`--thema`): `scraper_google_maps` · `scraper_ecommerce` (auch Amazon) · `scraper_stellensuche` (auch Recruiting) · `scraper_videoseiten` · `anreicherung` (Geschäftsführer, E-Mail, Ansprache) · `export_sperrliste` · `instantly` · `abmahnung` · `einrichtung_lizenz` · `abo_rechnung` · `datenschutz` · `sonstiges`

**Wobei** (`--anliegen`): technisch `fehler` · `ergebnis` · `einrichtung` · `bedienung` · `vorschlag`; bei `abo_rechnung` `zahlung` · `rechnung` · `kuendigung` · `frage`; bei `datenschutz` `auskunft` · `widerspruch` · `loeschung` · `frage`.

Bei `abo_rechnung` und `datenschutz` erstellt der Befehl kein Support-Paket; es ist dort nicht nötig.

## Was im Support-Paket ist und was nicht

| Enthalten | Nie enthalten |
|---|---|
| `system.txt`: Betriebssystem, Python-Version, Stand laut CHANGELOG, Präfix des Lizenzschlüssels (erste 12 Zeichen), Typ und Features | Werte aus `.env` und `kampagne.env` |
| `einstellungen.txt`: Namen aller Einstellungen; Werte nur, wenn sie harmlos sind (Zahlen, Schalter, Modellnamen) | API-Schlüssel, Passwörter, Tokens, der vollständige Lizenzschlüssel |
| `dateien.txt`: Liste der Programm- und Doku-Dateien mit Größe und Datum | Leads, Exporte, Datenbanken (`data/`, `exports/`, `auftraege/`, `arbeit/`) |
| `beschreibung.txt`: die eigene Beschreibung, wenn angegeben | E-Mail-Adressen (werden auch in der Beschreibung entfernt) |

Einstellungen, deren Name nach Schlüssel, Token, Passwort oder URL klingt, erscheinen immer nur als „(gesetzt)“ oder „(leer)“. Vor dem Packen werden alle Texte zusätzlich nach Schlüsseln und E-Mail-Adressen durchsucht und diese durch „[entfernt]“ ersetzt.

Wer sichergehen will, öffnet die ZIP-Datei vor dem Hochladen: Es sind vier Textdateien.

## Was nach dem Absenden passiert

Der Nutzer bekommt eine Vorgangsnummer (`SUP-2026-0001`) und eine Bestätigung per Mail, ohne Abo stattdessen die Mail mit dem Link zum Abo. Die Anfrage samt ZIP-Datei wird nach 12 Monaten gelöscht (`../DATENSCHUTZ.md`, Abschnitt 3.8).
