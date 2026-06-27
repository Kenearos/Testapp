#!/usr/bin/env python3
"""Lauffähiger Photo-to-Listing-Prototyp des eBay-Auto-Listers.

Demonstriert die komplette BMAD-Orchestrierung end-to-end:
    Foto ──► Bildanalyse ──► Preis-Recherche ──► Listing ──► Käufer-Chat

Betrieb
-------
Ohne Argumente läuft eine vollständige Demo im Mock-Modus (nur Standard-
bibliothek, keine Installation, kein Netz nötig)::

    python3 spike/prototype.py

Mit echtem Produktfoto über den authentifizierten claude-CLI::

    python3 spike/prototype.py --image /pfad/zum/foto.jpg --live

Das Skript ist bewusst aus jedem Verzeichnis lauffähig (es fügt den Projekt-
Root selbst zum Importpfad hinzu).
"""

from __future__ import annotations

import argparse
import logging
import os
import sys

# Projekt-Root (eine Ebene über spike/) importierbar machen.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.agents.orchestrator import Orchestrator  # noqa: E402
from src.llm import ClaudeClient  # noqa: E402
from src.models import Listing  # noqa: E402

_RULE = "═" * 64
_DEMO_QUESTIONS = [
    "Was kostet der Versand?",
    "Ist der Preis noch verhandelbar?",
    "Der Artikel kam defekt an, ich will mein Geld zurück.",  # -> Eskalation
]


def _section(title: str) -> None:
    print(f"\n{_RULE}\n  {title}\n{_RULE}")


def run_demo(
    image_path: str | None,
    description: str | None,
    mode: str,
    questions: list[str],
) -> int:
    client = ClaudeClient(mode=mode)
    orch = Orchestrator(client)

    print(f"\n eBay-Auto-Lister · Photo-to-Listing-Prototyp")
    print(f" Betriebsmodus: {orch.mode.upper()}"
          f"{'  (claude-CLI)' if orch.mode == 'live' else '  (deterministischer Mock)'}")
    if image_path:
        print(f" Eingabe-Foto:  {image_path}")
    elif description:
        print(f" Eingabe-Text:  {description}")

    # --- Kern-Workflow ----------------------------------------------------
    result = orch.photo_to_listing(image_path=image_path, description=description)
    a, p, listing = result.analysis, result.price, result.listing

    _section("1 · BILDANALYSE (Vision-Agent)")
    print(f" Erkannt:   {a.title_guess}")
    print(f" Marke:     {a.brand or '–'}")
    print(f" Kategorie: {a.category}")
    print(f" Zustand:   {a.condition}  (Score {a.condition_score:.2f})")
    print(f" Merkmale:  {', '.join(a.features) or '–'}")
    print(f" Mängel:    {', '.join(a.defects) or '–'}")
    print(f" Sicherheit: {a.confidence:.0%}   [Quelle: {a.source}]")

    _section("2 · PREIS-RECHERCHE (Market-Agent)")
    print(f" Vorschlag: {p.suggested_price:.2f} {p.currency}")
    print(f" Spanne:    {p.price_min:.2f} – {p.price_max:.2f} {p.currency}")
    print(f" Basis:     {p.rationale}   [Quelle: {p.source}]")

    _section("3 · LISTING (Listing-Agent)")
    print(f" Titel ({len(listing.title)}/80): {listing.title}")
    print(f" Kategorie-ID: {listing.category_id}")
    print(f" Preis:        {listing.price:.2f} {listing.currency}")
    print(" Artikelmerkmale:")
    for key, value in listing.item_specifics.items():
        print(f"   • {key}: {value}")
    print("\n Beschreibung:\n")
    for line in listing.description.splitlines():
        print(f"   {line}")

    # --- Chat-Demo --------------------------------------------------------
    if questions:
        _section("4 · KÄUFER-CHAT (Chat-Moderation-Agent)")
        for q in questions:
            reply = orch.answer_question(q, listing)
            flag = "  ⚠ ESKALATION an Mensch" if reply.escalate else ""
            print(f"\n Frage:   {q}")
            print(f" Antwort: {reply.answer}{flag}")

    _section("✓ FERTIG")
    print(" Der komplette Photo-to-Listing-Ablauf wurde durchlaufen.")
    print(f" (Tipp: mit --json gibt es das Ergebnis maschinenlesbar aus.)\n")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--image", help="Pfad zu einem Produktfoto (Live-Modus)")
    parser.add_argument("--description", help="Textuelle Artikelbeschreibung")
    parser.add_argument("--live", action="store_true", help="Live-Modus erzwingen (claude-CLI)")
    parser.add_argument("--mock", action="store_true", help="Mock-Modus erzwingen")
    parser.add_argument("--json", action="store_true", help="Nur JSON-Ergebnis ausgeben")
    parser.add_argument("--no-chat", action="store_true", help="Chat-Demo überspringen")
    parser.add_argument(
        "--question", action="append", default=None,
        help="Eigene Käuferfrage (mehrfach möglich)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(level=logging.WARNING, format="%(message)s")

    mode = "auto"
    if args.live:
        mode = "live"
    elif args.mock:
        mode = "mock"

    image = args.image
    description = args.description
    # Standard-Demo, wenn weder Foto noch Text angegeben wurde.
    if not image and not description:
        description = "gebrauchte Over-Ear Bluetooth-Kopfhörer mit Noise Cancelling"

    if args.json:
        orch = Orchestrator(ClaudeClient(mode=mode))
        print(orch.photo_to_listing(image_path=image, description=description).to_json())
        return 0

    questions = [] if args.no_chat else (args.question or _DEMO_QUESTIONS)
    return run_demo(image, description, mode, questions)


if __name__ == "__main__":
    raise SystemExit(main())
