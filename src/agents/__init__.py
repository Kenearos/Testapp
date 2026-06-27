"""BMAD-Fach-Agenten des eBay-Auto-Listers.

Rollen-Mapping (Auftrag -> README):
    vision   = ImageAnalysisAgent   (Bildanalyse-Agent)
    market   = PriceResearchAgent   (Preis-Recherche-Agent)
    listing  = ListingAgent         (Listing-Erstellung-Agent)
    chat     = ChatModerationAgent  (Chat-Moderation-Agent)
"""

from .base import BaseAgent
from .chat_moderation_agent import ChatModerationAgent
from .image_analysis_agent import ImageAnalysisAgent
from .listing_agent import ListingAgent
from .orchestrator import Orchestrator
from .price_research_agent import PriceResearchAgent

# Kurz-Aliase entsprechend der BMAD-Rollennamen im Auftrag.
VisionAgent = ImageAnalysisAgent
MarketAgent = PriceResearchAgent
ChatAgent = ChatModerationAgent

__all__ = [
    "BaseAgent",
    "Orchestrator",
    "ImageAnalysisAgent",
    "PriceResearchAgent",
    "ListingAgent",
    "ChatModerationAgent",
    "VisionAgent",
    "MarketAgent",
    "ChatAgent",
]
