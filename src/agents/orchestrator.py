"""Zentraler Orchestrator (BMAD-Orchestrator-Pattern).

Nimmt den Nutzerauftrag entgegen, delegiert sequenziell an die Fach-Agenten und
aggregiert die Ergebnisse zu einem einheitlichen :class:`~src.models.ListingResult`.
Jeder Agent kommuniziert ausschließlich über die typisierten Modelle aus
:mod:`src.models`.

CLI:
    python3 -m src.agents.orchestrator [--image PFAD] [--description TEXT] [--live]
"""

from __future__ import annotations

import argparse
import logging

from ..llm import ClaudeClient
from ..models import ChatReply, ItemAnalysis, Listing, ListingResult, PriceSuggestion
from .chat_moderation_agent import ChatModerationAgent
from .image_analysis_agent import ImageAnalysisAgent
from .listing_agent import ListingAgent
from .price_research_agent import PriceResearchAgent


class Orchestrator:
    """Koordiniert Vision → Market → Listing und beantwortet Käuferfragen."""

    def __init__(self, client: ClaudeClient | None = None) -> None:
        self.client = client or ClaudeClient()
        self.log = logging.getLogger("agent.orchestrator")
        self.vision = ImageAnalysisAgent(self.client)
        self.market = PriceResearchAgent(self.client)
        self.listing = ListingAgent(self.client)
        self.chat = ChatModerationAgent(self.client)

    @property
    def mode(self) -> str:
        return self.client.mode

    # ------------------------------------------------------------------ core
    def photo_to_listing(
        self,
        image_path: str | None = None,
        description: str | None = None,
    ) -> ListingResult:
        """Kern-Workflow: Foto/Beschreibung -> fertiges Listing."""
        if not image_path and not description:
            raise ValueError("image_path oder description erforderlich")

        self.log.info("1/3 Bildanalyse (mode=%s)…", self.mode)
        analysis: ItemAnalysis = self.vision.run(
            {"image_path": image_path, "description": description}
        )

        self.log.info("2/3 Preis-Recherche…")
        price: PriceSuggestion = self.market.run(analysis)

        self.log.info("3/3 Listing-Erstellung…")
        listing: Listing = self.listing.run((analysis, price))

        return ListingResult(analysis=analysis, price=price, listing=listing)

    # ------------------------------------------------------------------ chat
    def answer_question(self, question: str, listing: Listing) -> ChatReply:
        """Delegiert eine Käuferfrage an den Chat-Moderation-Agenten."""
        return self.chat.run({"question": question, "listing": listing})


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="eBay-Auto-Lister Orchestrator")
    parser.add_argument("--image", help="Pfad zu einem Produktfoto")
    parser.add_argument("--description", help="Textuelle Artikelbeschreibung (Fallback)")
    parser.add_argument(
        "--live", action="store_true",
        help="Live-Modus erzwingen (nutzt den claude-CLI statt Mock)",
    )
    parser.add_argument(
        "--mock", action="store_true",
        help="Mock-Modus erzwingen (kein CLI-Aufruf)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = _build_parser().parse_args(argv)

    mode = "auto"
    if args.live:
        mode = "live"
    elif args.mock:
        mode = "mock"

    image = args.image
    description = args.description
    if not image and not description:
        description = "Beispielartikel: gebrauchte Over-Ear Bluetooth-Kopfhörer"

    orch = Orchestrator(ClaudeClient(mode=mode))
    result = orch.photo_to_listing(image_path=image, description=description)
    print(result.to_json())
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
