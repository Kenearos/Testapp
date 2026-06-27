"""Preis-Recherche-Agent ("Market").

Eingang: :class:`~src.models.ItemAnalysis`.
Ausgang: :class:`~src.models.PriceSuggestion`.

Hinweis: Echtes Scraping verkaufter eBay-Listings unterliegt den eBay-AGB und
ist hier bewusst NICHT enthalten (siehe ``src/scrapers``). Der Live-Pfad nutzt
die Marktkenntnis des Modells als Schätzung; der Mock-Pfad eine transparente
Heuristik aus Kategorie und Zustand.
"""

from __future__ import annotations

from ..models import ItemAnalysis, PriceSuggestion
from .base import BaseAgent

_PROMPT = (
    "Du bist ein eBay-Preisanalyst. Schätze auf Basis deiner Marktkenntnis den "
    "realistischen Verkaufspreis (Sofort-Kauf) für den folgenden Gebrauchtartikel "
    "auf dem deutschen eBay-Markt.\n\n"
    "Artikel: {title}\nMarke: {brand}\nKategorie: {category}\n"
    "Zustand: {condition} (Score {score})\nMerkmale: {features}\n\n"
    "JSON-Schema:\n"
    "{{\n"
    '  "suggested_price": float,\n'
    '  "price_min": float,\n'
    '  "price_max": float,\n'
    '  "currency": "EUR",\n'
    '  "rationale": str\n'
    "}}"
)

# Grobe Basispreise je Kategorie-Stichwort (EUR, gebraucht, mittlerer Zustand).
_BASE_PRICES = {
    "kopfhörer": 120.0,
    "sneaker": 70.0,
    "digitalkamera": 350.0,
    "kamera": 350.0,
    "armbanduhr": 180.0,
    "uhr": 180.0,
    "konsole": 250.0,
}
_BASE_DEFAULT = 40.0


class PriceResearchAgent(BaseAgent):
    name = "market"
    role = "Preis-Recherche-Agent – schlägt einen Marktpreis vor"

    def run(self, payload: ItemAnalysis) -> PriceSuggestion:
        prompt = _PROMPT.format(
            title=payload.title_guess,
            brand=payload.brand or "unbekannt",
            category=payload.category,
            condition=payload.condition,
            score=round(payload.condition_score, 2),
            features=", ".join(payload.features) or "keine",
        )
        data = self._try_live_json(prompt)
        if data is not None:
            return self._from_json(data)
        return self._mock(payload)

    # ----------------------------------------------------------------- live
    @staticmethod
    def _from_json(data: dict) -> PriceSuggestion:
        suggested = float(data.get("suggested_price", 0.0))
        return PriceSuggestion(
            suggested_price=round(suggested, 2),
            price_min=round(float(data.get("price_min", suggested * 0.8)), 2),
            price_max=round(float(data.get("price_max", suggested * 1.2)), 2),
            currency=str(data.get("currency", "EUR")),
            rationale=str(data.get("rationale", "")),
            sample_size=0,
            source="claude-cli",
        )

    # ----------------------------------------------------------------- mock
    @staticmethod
    def _mock(item: ItemAnalysis) -> PriceSuggestion:
        category = item.category.lower()
        base = _BASE_DEFAULT
        for keyword, price in _BASE_PRICES.items():
            if keyword in category:
                base = price
                break
        # Zustand skaliert den Preis zwischen 50 % (defekt) und 100 % (neuwertig).
        factor = 0.5 + 0.5 * max(0.0, min(1.0, item.condition_score))
        suggested = round(base * factor, 2)
        return PriceSuggestion(
            suggested_price=suggested,
            price_min=round(suggested * 0.85, 2),
            price_max=round(suggested * 1.15, 2),
            currency="EUR",
            sample_size=12,
            rationale=(
                f"Heuristik: Basispreis {base:.0f} € für Kategorie "
                f"'{item.category}', skaliert mit Zustands-Score "
                f"{item.condition_score:.2f}."
            ),
            source="mock",
        )
