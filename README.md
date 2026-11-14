# Akquise & Abmahnschutz

Ein Paket für B2B-Akquise, von der Zielgruppe bis zur Abmahnung:

```
 1 Interview         2 Pfad                 3 Sperrliste          4 Versand        5 Abmahnung?
 Wen willst du?  ──► Google Maps        ──► Abmahner-Domains  ──► dein Tool   ──►  Skill abmahnung-
 Wo findet man       Amazon-Seller          fliegen raus                           werbemail-abwehr
 sie?                E-Commerce                  ▲                                       │
                     Recruiting, Stellensuche    └──── 6 Abmahner wird gemeldet ◄───────┘
```

Kostenlos: der Lead-Scraper mit allen Pfaden, der Abmahnungs-Check „So würden wir damit umgehen“, Meldungen und Adresssperren. Mit Abo: der abgestufte Sperrlisten-Abgleich beim Export, die Abmahner-Frühwarnung, die Instantly-Anbindung und das Support-Paket. Die Sperrliste liegt nur auf dem Server von Agentur Consulting und wird nie ausgegeben; zurück kommt nur das Ergebnis für die eigenen Leads.

Nach jedem Export überträgt der Scraper die exportierten Leads an den Server, auch im Free-Plan ([NUTZUNGSBEDINGUNGEN.md](NUTZUNGSBEDINGUNGEN.md), [DATENSCHUTZ.md](DATENSCHUTZ.md)). **Bedingung der Nutzung:** Wer abgemahnt wird, meldet den Abmahner. Der Skill zeigt vorher an, was übermittelt wird.

## Inhalt

| Was | Wozu |
|---|---|
| [`skills/lead-scraper.zip`](skills/lead-scraper.zip) | Claude-Skill: Interview, Pfadwahl, alle Pfade, Sperrlisten-Abgleich, Wissensbibliothek |
| [`skills/abmahnung-werbemail-abwehr.zip`](skills/abmahnung-werbemail-abwehr.zip) | Claude-Skill: Abmahnung prüfen, Antwort und Unterlassungserklärung als PDF, Website des Abmahners sichern, Meldung an den Server |
| [`lead-scraper/`](lead-scraper/) | derselbe Skill als Ordner, zum Öffnen in Claude Code oder Codex |
| [`lead-scraper/wissen/`](lead-scraper/wissen/) | **Wissensbibliothek**: alles Fachwissen als Markdown, für jedes KI-Modell |
| [`WISSEN_KOMPLETT.md`](WISSEN_KOMPLETT.md) | die Wissensbibliothek in einer Datei (für ChatGPT, Gemini & Co.) |
| [`abmahnung-werbemail-abwehr/`](abmahnung-werbemail-abwehr/) | der Abmahnungs-Skill als Ordner |

## Loslegen

1. **Skills installieren:** beide ZIPs aus `skills/` herunterladen und in Claude unter Einstellungen → Funktionen → Skills hochladen. In Claude Code reicht es, diesen Ordner zu öffnen.
2. **Loslegen:** *„Ich will neue Kunden finden.“* Claude fragt nach Angebot, Wunschkunden, Fundort, Ländern und Umfang. Danach schlägt es den passenden Weg vor und macht erst einen Testlauf.
3. **Voraussetzungen je Weg** (Details in `lead-scraper/wissen/11_zugaenge-und-kosten.md`):
   - **Google Maps, Recruiting, Stellensuche:** Python 3.10+, eigener Zugang bei Skael (die KI läuft standardmäßig über Skael). OpenAI nur bei `LLM_PROVIDER=openai` oder `DOMAINSUCHE=openai`, dann mit aufgeladenem Guthaben.
   - **Amazon:** Node.js 18+, Oxylabs-Zugang (Pflicht); Bright Data für Kontaktdaten; Skael für E-Mail-Prüfung, Website und Geschäftsführung.
   - **E-Commerce:** eine Shop-Liste als CSV (Firmenname und/oder Website), Python 3.10+, eigene Zugänge bei Skael und OpenAI.
4. **Ergebnis:** Versandlisten. Mit Abo sind die Firmen auf der Sperrliste aussortiert und stehen in einer eigenen Datei. Im Free-Plan gibt es keinen Abgleich; `python3 werkzeuge/lizenz.py abo` (im Ordner `lead-scraper/`) öffnet den Checkout.
5. **Abmahnung bekommen?** Das PDF in Claude legen: *„Ich habe diese Abmahnung wegen einer Werbe-Mail bekommen, bitte prüfen.“*
6. **Fragen zwischendurch:** einfach stellen. Die Antworten kommen aus der Wissensbibliothek. Mit einem anderen KI-Modell: `WISSEN_KOMPLETT.md` hochladen und den Start-Prompt aus `lead-scraper/wissen/00_INDEX.md` nutzen.

**So arbeiten wir sauber:** persönliche Ansprache mit klarem Absender, Abmeldeweg und Datenschutzhinweis nach Art. 14 DSGVO; Widersprüche sofort sperren; jede Liste vor dem Versand mit der Sperrliste abgleichen. Die Checkliste steht in `lead-scraper/wissen/08_versand-und-recht.md`.

> **Keine Rechtsberatung.** Der Abmahnungs-Check und die Texte des Pakets zeigen, wie wir mit einem Fall umgehen würden. Sie ersetzen keine Beratung durch eine Anwältin oder einen Anwalt.

## Support

Mit Abo über das Formular auf [ak.consulting/support](https://ak.consulting/support). Der Skill hilft beim Ausfüllen (`python3 werkzeuge/lizenz.py support` im Ordner `lead-scraper/`).

## Nutzungsbedingungen und Datenschutz

[NUTZUNGSBEDINGUNGEN.md](NUTZUNGSBEDINGUNGEN.md) · [DATENSCHUTZ.md](DATENSCHUTZ.md)
