"""eBay-Auto-Lister — BMAD-basiertes Multi-Agent-System.

Schnelleinstieg::

    from src import photo_to_listing
    result = photo_to_listing(description="gebrauchte Bluetooth-Kopfhörer")
    print(result.to_json())
"""

from .models import (
    ChatReply,
    ItemAnalysis,
    Listing,
    ListingResult,
    PriceSuggestion,
)
from .workflow import photo_to_listing

__all__ = [
    "ItemAnalysis",
    "PriceSuggestion",
    "Listing",
    "ChatReply",
    "ListingResult",
    "photo_to_listing",
]
__version__ = "0.1.0"
