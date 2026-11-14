"""Sperrliste: graded server check for the export (subscription), thin wrapper around werkzeuge/lizenz.py.

There is no public list. The list lives only on the server of Akquise & Abmahnschutz and is checked entry by
entry (severity 1–6). With a subscription (or a partner/intern key) every e-mail address and website that can
end up in list 1 or 2 is checked at export: from SPERREN_AB (default 3) the lead goes to list 4, from
WARNEN_AB (default 1) it stays in the list with a note. In the free plan there is no check; the export
shows a notice instead.

With a subscription and the server unreachable the export stops (SPERRLISTE_PFLICHT=false allows it anyway).

After every export the exported leads are handed to the server (also in the free plan), see `hochladen`
and the terms of use.
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

PFAD = "e-commerce"


def norm_domain(wert: str | None) -> str:
    d = str(wert or "").strip().lower()
    if "@" in d:
        d = d.rsplit("@", 1)[1]
    d = re.sub(r"^[a-z]+://", "", d)
    d = d.split("/")[0].split("?")[0].split("#")[0].split(":")[0].rstrip(".")
    return re.sub(r"^www\d?\.", "", d)


class Sperrliste:
    """Fixed set of domains with the same interface as lizenz.Sperrabgleich (tests, local stubs)."""

    def __init__(self, domains: set[str], quelle: str):
        self.domains = domains
        self.quelle = quelle

    def treffer(self, *werte: str | None) -> str | None:
        """Returns the blocked domain if one of the values (e-mail, URL, domain) or a parent domain is listed."""
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
    """Graded check for all values (e-mail addresses, websites). None in the free plan.

    With a subscription and no connection: SystemExit if pflicht (default SPERRLISTE_PFLICHT), else None.
    """
    pflicht = CONFIG.sperrliste_pflicht if pflicht is None else pflicht
    return lizenz.sperrabgleich_laden(list(werte), pflicht=pflicht)


def hochladen(leads: list[dict], *, pfad: str = PFAD, bezeichnung: str | None = None) -> bool:
    """Hands the exported leads to the server. Never raises; False on errors."""
    return lizenz.leads_hochladen(leads, pfad=pfad, bezeichnung=bezeichnung)
