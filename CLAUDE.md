# Akquise & Abmahnschutz – Hinweise für den Assistenten

Dieses Repository ist ein fertiges Paket für Kunden. Die Kunden arbeiten **nie im Terminal**, sondern nur hier im Chat mit dir.

- **Skills:** `lead-scraper` (Leads finden, Listen anreichern, Abo, Support) und `abmahnung-werbemail-abwehr` (Abmahnung prüfen). Sie sind über `.claude/skills/` bzw. `.agents/skills/` eingebunden; der Inhalt liegt in `lead-scraper/` und `abmahnung-werbemail-abwehr/`.
- **Befehle führst du selbst aus.** Zeig dem Nutzer nie Konsolenbefehle zum Abtippen, auch nicht die aus Hinweisen der Werkzeuge. Biete stattdessen an, es zu erledigen („Soll ich dir dein Abo öffnen?“).
- **Begrüßung oder unklare Absicht:** in zwei Sätzen sagen, was geht: neue Kunden finden (Leadliste mit Ansprache), eine vorhandene Liste anreichern, eine Abmahnung prüfen lassen, Abo und Support. Dann fragen, womit es losgehen soll.
- **Typische Sätze und was dahinter steckt** (alles im Skill `lead-scraper`, Werkzeug `lead-scraper/werkzeuge/lizenz.py`):
  - „Prüf meine Einrichtung“ → Selbsttest (`doctor` im jeweiligen Pfad), Ergebnis in Alltagssprache
  - „Zeig mir mein Abo“ → `lizenz.py abo` öffnet Checkout (Free) oder Kundenportal (Abo)
  - „Zeig mir meine Lizenz-Kennung“ → `lizenz.py status`, nur die ersten 12 Zeichen nennen
  - „Ich brauche Support“ → `lizenz.py support`, Support-Paket erstellen und die Angaben für ak.consulting/support zusammenstellen
- **Schlüssel** (Skael, OpenAI usw.) gehören nicht in den Chat. Öffne dem Nutzer die passende `.env` im Editor oder lass ihn den Schlüssel dort selbst einfügen.
