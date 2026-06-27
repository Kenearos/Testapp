"""Kern-Workflow des eBay-Auto-Listers.

Dünne, bequeme Fassade über den :class:`~src.agents.orchestrator.Orchestrator`,
damit Aufrufer den Photo-to-Listing-Ablauf in einer Zeile auslösen können.
"""

from __future__ import annotations

from .agents.orchestrator import Orchestrator
from .llm import ClaudeClient
from .models import ListingResult


def photo_to_listing(
    image_path: str | None = None,
    description: str | None = None,
    *,
    mode: str = "auto",
    client: ClaudeClient | None = None,
) -> ListingResult:
    """Foto (oder Beschreibung) -> fertiges :class:`ListingResult`.

    Parameter
    ---------
    image_path: Pfad zu einem Produktfoto.
    description: Alternative/zusätzliche textuelle Beschreibung.
    mode: ``"auto"`` | ``"live"`` | ``"mock"`` (ignoriert, wenn ``client`` gesetzt).
    client: optionaler vorkonfigurierter :class:`ClaudeClient`.
    """
    orchestrator = Orchestrator(client or ClaudeClient(mode=mode))
    return orchestrator.photo_to_listing(image_path=image_path, description=description)
