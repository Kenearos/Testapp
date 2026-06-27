"""Standardisierte Datenstrukturen für den eBay-Auto-Lister.

BMAD-Prinzip: Agenten kommunizieren *ausschließlich* über diese typisierten
Verträge. Bewusst mit ``dataclasses`` aus der Standardbibliothek umgesetzt
(kein Pydantic), damit Spike und Agenten ohne ``pip install`` lauffähig sind.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field


@dataclass
class ItemAnalysis:
    """Ergebnis des Bildanalyse-Agenten (Vision)."""

    title_guess: str
    category: str
    condition: str            # menschenlesbar, z. B. "Gebraucht – sehr gut"
    condition_score: float    # 0.0 (defekt) .. 1.0 (neuwertig)
    brand: str | None = None
    features: list[str] = field(default_factory=list)
    defects: list[str] = field(default_factory=list)
    confidence: float = 0.0   # 0.0 .. 1.0, Sicherheit der Erkennung
    source: str = "mock"      # "claude-cli" oder "mock"
    raw: str = ""             # Rohausgabe des Modells (Debug)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PriceSuggestion:
    """Ergebnis des Preis-Recherche-Agenten (Market)."""

    suggested_price: float
    price_min: float
    price_max: float
    currency: str = "EUR"
    sample_size: int = 0      # Anzahl ausgewerteter Vergleichsangebote
    rationale: str = ""
    source: str = "mock"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Listing:
    """Ergebnis des Listing-Erstellung-Agenten."""

    title: str                # eBay-Limit: max. 80 Zeichen
    description: str
    category_id: str
    item_specifics: dict[str, str] = field(default_factory=dict)
    price: float = 0.0
    currency: str = "EUR"
    source: str = "mock"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ChatReply:
    """Ergebnis des Chat-Moderation-Agenten."""

    question: str
    answer: str
    escalate: bool = False    # True = an Menschen eskalieren
    source: str = "mock"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ListingResult:
    """Aggregiertes Endergebnis des Photo-to-Listing-Workflows."""

    analysis: ItemAnalysis
    price: PriceSuggestion
    listing: Listing

    def to_dict(self) -> dict:
        return {
            "analysis": self.analysis.to_dict(),
            "price": self.price.to_dict(),
            "listing": self.listing.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
