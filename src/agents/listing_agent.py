"""Listing-Erstellung-Agent.

Eingang: :class:`~src.models.ItemAnalysis` + :class:`~src.models.PriceSuggestion`.
Ausgang: :class:`~src.models.Listing` (eBay-konform).
"""

from __future__ import annotations

from ..models import ItemAnalysis, Listing, PriceSuggestion
from .base import BaseAgent

_TITLE_MAX = 80  # eBay-Titel-Limit

_PROMPT = (
    "Du bist ein Profi für verkaufsstarke eBay-Angebote. Erstelle ein "
    "eBay-konformes Listing für den folgenden Artikel.\n\n"
    "Artikel: {title}\nMarke: {brand}\nKategorie: {category}\n"
    "Zustand: {condition}\nMerkmale: {features}\nMängel: {defects}\n"
    "Vorgeschlagener Preis: {price} {currency}\n\n"
    "Regeln: Titel max. 80 Zeichen, keyword-stark, ohne Ausrufezeichen-Spam. "
    "Beschreibung sachlich, ehrlich zum Zustand, mit Stichpunkten.\n\n"
    "JSON-Schema:\n"
    "{{\n"
    '  "title": str,                 // <= 80 Zeichen\n'
    '  "description": str,\n'
    '  "category_id": str,           // eBay-Kategorie-ID (Schätzung erlaubt)\n'
    '  "item_specifics": {{ }}       // Schlüssel/Wert, z. B. Marke, Zustand\n'
    "}}"
)

# Stichwort -> eBay-Kategorie-ID (Auszug, Demo-Werte).
_CATEGORY_IDS = {
    "kopfhörer": "112529",
    "sneaker": "15709",
    "schuh": "15709",
    "kamera": "31388",
    "uhr": "31387",
    "konsole": "139971",
}
_CATEGORY_DEFAULT = "267"  # "Sonstiges"


class ListingAgent(BaseAgent):
    name = "listing"
    role = "Listing-Erstellung-Agent – erzeugt Titel, Text, Kategorie, Attribute"

    def run(self, payload) -> Listing:
        """``payload``: (ItemAnalysis, PriceSuggestion) oder dict."""
        analysis, price = self._unpack(payload)
        prompt = _PROMPT.format(
            title=analysis.title_guess,
            brand=analysis.brand or "unbekannt",
            category=analysis.category,
            condition=analysis.condition,
            features=", ".join(analysis.features) or "keine",
            defects=", ".join(analysis.defects) or "keine bekannt",
            price=price.suggested_price,
            currency=price.currency,
        )
        data = self._try_live_json(prompt)
        if data is not None:
            return self._from_json(data, analysis, price)
        return self._mock(analysis, price)

    @staticmethod
    def _unpack(payload) -> tuple[ItemAnalysis, PriceSuggestion]:
        if isinstance(payload, dict):
            return payload["analysis"], payload["price"]
        analysis, price = payload
        return analysis, price

    # ----------------------------------------------------------------- live
    def _from_json(
        self, data: dict, analysis: ItemAnalysis, price: PriceSuggestion
    ) -> Listing:
        title = str(data.get("title", analysis.title_guess))[:_TITLE_MAX]
        specifics = data.get("item_specifics") or {}
        if not isinstance(specifics, dict):
            specifics = {}
        return Listing(
            title=title,
            description=str(data.get("description", "")),
            category_id=str(data.get("category_id") or self._category_id(analysis)),
            item_specifics={str(k): str(v) for k, v in specifics.items()},
            price=price.suggested_price,
            currency=price.currency,
            source="claude-cli",
        )

    # ----------------------------------------------------------------- mock
    def _mock(self, analysis: ItemAnalysis, price: PriceSuggestion) -> Listing:
        brand = analysis.brand or ""
        title = " ".join(
            part for part in [brand, analysis.title_guess, analysis.condition]
            if part
        )[:_TITLE_MAX]

        feature_lines = "\n".join(f"- {f}" for f in analysis.features)
        defect_lines = "\n".join(f"- {d}" for d in analysis.defects) or "- keine bekannt"
        description = (
            f"{brand + ' ' if brand else ''}{analysis.title_guess}\n\n"
            f"Zustand: {analysis.condition}\n\n"
            f"Merkmale:\n{feature_lines}\n\n"
            f"Hinweise zum Zustand:\n{defect_lines}\n\n"
            f"Preis: {price.suggested_price:.2f} {price.currency} (Sofort-Kauf). "
            f"Versand als versichertes Paket. Privatverkauf, keine Rücknahme."
        )
        specifics = {"Zustand": analysis.condition}
        if brand:
            specifics["Marke"] = brand
        for i, feat in enumerate(analysis.features, 1):
            specifics[f"Merkmal {i}"] = feat

        return Listing(
            title=title,
            description=description,
            category_id=self._category_id(analysis),
            item_specifics=specifics,
            price=price.suggested_price,
            currency=price.currency,
            source="mock",
        )

    @staticmethod
    def _category_id(analysis: ItemAnalysis) -> str:
        haystack = f"{analysis.category} {analysis.title_guess}".lower()
        for keyword, cid in _CATEGORY_IDS.items():
            if keyword in haystack:
                return cid
        return _CATEGORY_DEFAULT
