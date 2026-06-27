#!/usr/bin/env python3
"""Concept-Spike: Orchestrator-Pattern ohne externe Abhängigkeiten.

Minimaler Einstiegspunkt, der den vollständigen Photo-to-Listing-Prototyp im
deterministischen Mock-Modus startet – keine Installation, kein Netz nötig::

    python3 spike/concept_spike.py

Für die volle Demo mit echtem Foto siehe ``spike/prototype.py --image … --live``.
"""

from __future__ import annotations

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from spike.prototype import main  # noqa: E402

if __name__ == "__main__":
    # Mock erzwingen: der Spike läuft garantiert ohne CLI/Netz.
    raise SystemExit(main(["--mock"]))
