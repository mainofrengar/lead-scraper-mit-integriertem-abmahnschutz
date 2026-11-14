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

## Loslegen

Du brauchst kein Terminal. Alles läuft im Chat mit Claude Code oder Codex.

1. **Paket holen:** Oben auf dieser Seite „Code“ → „Download ZIP“ und entpacken. Oder in Claude Code bzw. Codex sagen: *„Hol mir github.com/mainofrengar/lead-scraper-mit-integriertem-abmahnschutz in einen neuen Ordner.“*
2. **Ordner öffnen** in Claude Code (Desktop-App, VS Code oder Terminal-App) oder in Codex. Die beiden Skills `lead-scraper` und `abmahnung-werbemail-abwehr` sind damit sofort eingerichtet, ohne Installation. In Claude Code kannst du sie auch direkt aufrufen: `/lead-scraper`.
3. **Sagen, was du willst:** *„Ich will neue Kunden finden.“* Claude fragt nach Angebot, Wunschkunden, Fundort, Ländern und Umfang, schlägt den passenden Weg vor und macht erst einen Testlauf. Was du an Zugängen brauchst (z. B. Skael), sagt Claude dir unterwegs; die Übersicht steht in `lead-scraper/wissen/11_zugaenge-und-kosten.md`.

**Abmahnung bekommen?** Das PDF in den Chat legen: *„Ich habe diese Abmahnung wegen einer Werbe-Mail bekommen, bitte prüfen.“*

**Sätze, die du immer sagen kannst:**

| Du sagst | Claude macht |
|---|---|
| „Prüf meine Einrichtung“ | Selbsttest: Zugänge, Lizenz, Erreichbarkeit, mit Lösung, wenn etwas fehlt |
| „Zeig mir mein Abo“ | öffnet den Abschluss (Free) bzw. das Kundenportal mit Rechnungen, Zahlungsart und Kündigung (Abo) |
| „Ich brauche Support“ | erstellt das Support-Paket und füllt mit dir das Formular auf [ak.consulting/support](https://ak.consulting/support) aus |

**Andere Wege:** In der Claude-App (Chat) die beiden ZIPs aus [`skills/`](skills/) unter Einstellungen → Funktionen → Skills hochladen. Für ChatGPT, Gemini & Co.: [`WISSEN_KOMPLETT.md`](WISSEN_KOMPLETT.md) hochladen und den Start-Prompt aus `lead-scraper/wissen/00_INDEX.md` nutzen.

## Inhalt

| Was | Wozu |
|---|---|
| [`lead-scraper/`](lead-scraper/) | Skill: Interview, Pfadwahl, alle Pfade, Sperrlisten-Abgleich, Abo und Support |
| [`lead-scraper/wissen/`](lead-scraper/wissen/) | **Wissensbibliothek**: alles Fachwissen als Markdown, für jedes KI-Modell |
| [`abmahnung-werbemail-abwehr/`](abmahnung-werbemail-abwehr/) | Skill: Abmahnung prüfen, Antwort und Unterlassungserklärung als PDF, Website des Abmahners sichern, Meldung an den Server |
| [`skills/`](skills/) | beide Skills als ZIP für die Claude-App |
| [`WISSEN_KOMPLETT.md`](WISSEN_KOMPLETT.md) | die Wissensbibliothek in einer Datei |

**So arbeiten wir sauber:** persönliche Ansprache mit klarem Absender, Abmeldeweg und Datenschutzhinweis nach Art. 14 DSGVO; Widersprüche sofort sperren; jede Liste vor dem Versand mit der Sperrliste abgleichen. Die Checkliste steht in `lead-scraper/wissen/08_versand-und-recht.md`.

> **Keine Rechtsberatung.** Der Abmahnungs-Check und die Texte des Pakets zeigen, wie wir mit einem Fall umgehen würden. Sie ersetzen keine Beratung durch eine Anwältin oder einen Anwalt.

## Support

Mit Abo über [ak.consulting/support](https://ak.consulting/support). Am einfachsten sagst du Claude: *„Ich brauche Support.“*

## Nutzungsbedingungen und Datenschutz

[NUTZUNGSBEDINGUNGEN.md](NUTZUNGSBEDINGUNGEN.md) · [DATENSCHUTZ.md](DATENSCHUTZ.md)
