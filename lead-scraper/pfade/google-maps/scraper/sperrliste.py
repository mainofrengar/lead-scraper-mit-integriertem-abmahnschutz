"""Sperrlisten-Abgleich beim Export: dünne Schicht über werkzeuge/lizenz.py.

Eine öffentliche Sperrliste gibt es nicht. Die Einträge (Abmahner, gemeldete Domains und Adressen,
Stufe 1–6) liegen nur auf dem Server und werden je Lead abgefragt:

  * Free-Plan: kein Abgleich. laden() gibt None zurück, der Export zeigt einen Pro-Hinweis.
  * Abo (auch Partner-/Intern-Schlüssel): Der Server prüft alle E-Mail-Adressen und Websites des
    Exports. Ab SPERREN_AB (Standard 3) landet der Lead in Liste 5, ab WARNEN_AB (Standard 1) bekommt
    er einen Hinweis. Ist der Server nicht erreichbar, bricht der Export ab (abschaltbar mit
    SPERRLISTE_PFLICHT=false).

Nach jedem Export werden die exportierten Leads an den Server übertragen, auch im Free-Plan
(siehe hochladen() und die Nutzungsbedingungen).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from .config import CONFIG

_WERKZEUGE = Path(__file__).resolve().parents[3] / "werkzeuge"
if str(_WERKZEUGE) not in sys.path:
    sys.path.insert(0, str(_WERKZEUGE))

import lizenz  # noqa: E402


def norm_domain(wert: str | None) -> str:
    d = str(wert or "").strip().lower()
    if "@" in d:
        d = d.rsplit("@", 1)[1]
    d = re.sub(r"^[a-z]+://", "", d)
    d = d.split("/")[0].split("?")[0].split("#")[0].split(":")[0].rstrip(".")
    return re.sub(r"^www\d?\.", "", d)


class Sperrliste:
    """Local, set-based list with the same interface as lizenz.Sperrabgleich (used as a stub in tests)."""

    def __init__(self, domains: set[str], quelle: str):
        self.domains = domains
        self.quelle = quelle

    def treffer(self, *werte: str | None) -> str | None:
        """Gibt die gesperrte Domain zurück, falls einer der Werte (E-Mail, URL, Domain) betroffen ist."""
        for wert in werte:
            d = norm_domain(wert)
            if not d:
                continue
            teile = d.split(".")
            for i in range(len(teile) - 1):
                kandidat = ".".join(teile[i:])
                if kandidat in self.domains:
                    return kandidat
        return None

    def warnung(self, *werte: str | None) -> str | None:  # noqa: ARG002
        return None

    def __len__(self) -> int:
        return len(self.domains)


def laden(werte=(), *, pflicht: bool | None = None):
    """Abgleich für alle Werte (E-Mail-Adressen, Websites). None im Free-Plan.

    Mit Abo und ohne Verbindung bricht der Export ab (SystemExit), außer pflicht ist False.
    """
    return lizenz.sperrabgleich_laden(list(werte),
                                      pflicht=CONFIG.sperrliste_pflicht if pflicht is None else pflicht)


def hochladen(leads: list[dict], *, pfad: str, bezeichnung: str) -> bool:
    """Überträgt die exportierten Leads (Lead-Format) an den Server. Wirft nie, Fehler ergeben False."""
    return lizenz.leads_hochladen(leads, pfad=pfad, bezeichnung=bezeichnung)
