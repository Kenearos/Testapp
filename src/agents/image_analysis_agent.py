"""Bildanalyse-Agent ("Vision").

Eingang: Pfad zu einem Produktfoto (oder eine textuelle Beschreibung als
Fallback für Demos ohne Bild).
Ausgang: :class:`~src.models.ItemAnalysis`.
"""

from __future__ import annotations

from ..models import ItemAnalysis
from .base import BaseAgent

_PROMPT = (
    "Du bist ein Experte für Gebrauchtwaren-Ankauf. Analysiere das Produktfoto "
    "und liefere eine strukturierte Einschätzung für ein eBay-Verkaufsangebot. "
    "Schätze Artikeltyp, Marke, Zustand und sichtbare Merkmale/Mängel.\n\n"
    "JSON-Schema:\n"
    "{\n"
    '  "title_guess": str,         // kurze Artikelbezeichnung\n'
    '  "category": str,            // z. B. "Kopfhörer", "Sneaker"\n'
    '  "brand": str|null,\n'
    '  "condition": str,           // z. B. "Gebraucht – sehr gut"\n'
    '  "condition_score": float,   // 0.0 defekt .. 1.0 neuwertig\n'
    '  "features": [str],\n'
    '  "defects": [str],\n'
    '  "confidence": float         // 0.0 .. 1.0\n'
    "}"
)

# Deterministische Mock-Heuristik: Stichwort im Dateinamen/Beschreibung ->
# plausibles Beispielobjekt. Hält den Prototyp ohne Bild/CLI lauffähig.
_MOCK_TABLE = {
    "kopfhörer": ("Over-Ear Bluetooth-Kopfhörer", "Kopfhörer", "Sony",
                  ["Bluetooth", "Active Noise Cancelling", "faltbar"]),
    "headphone": ("Over-Ear Bluetooth-Kopfhörer", "Kopfhörer", "Sony",
                  ["Bluetooth", "Active Noise Cancelling", "faltbar"]),
    "sneaker": ("Sneaker Low-Top", "Sneaker", "Nike",
                ["Gr. 43", "Leder", "Originalkarton"]),
    "schuh": ("Sneaker Low-Top", "Sneaker", "Nike",
              ["Gr. 43", "Leder", "Originalkarton"]),
    "kamera": ("Spiegellose Systemkamera", "Digitalkameras", "Canon",
               ["24 MP", "inkl. Kit-Objektiv", "WLAN"]),
    "uhr": ("Automatik-Armbanduhr", "Armbanduhren", "Seiko",
            ["Edelstahl", "Saphirglas", "Datumsanzeige"]),
    "konsole": ("Spielkonsole", "Konsolen", "Sony",
                ["1 TB", "inkl. Controller", "4K"]),
}
_MOCK_DEFAULT = (
    "Over-Ear Bluetooth-Kopfhörer", "Kopfhörer", "Sony",
    ["Bluetooth", "Active Noise Cancelling", "faltbar"],
)


class ImageAnalysisAgent(BaseAgent):
    name = "vision"
    role = "Bildanalyse-Agent – erkennt Artikel, Zustand und Merkmale"

    def run(self, payload) -> ItemAnalysis:
        """``payload``: dict mit ``image_path`` und/oder ``description``."""
        if isinstance(payload, str):
            payload = {"image_path": payload}
        image_path = payload.get("image_path")
        description = payload.get("description")

        prompt = _PROMPT
        if description:
            prompt += f"\n\nZusätzlicher Kontext zum Artikel: {description}"

        data = self._try_live_json(prompt, image_path=image_path)
        if data is not None:
            return self._from_json(data)
        return self._mock(image_path, description)

    # ----------------------------------------------------------------- live
    @staticmethod
    def _from_json(data: dict) -> ItemAnalysis:
        return ItemAnalysis(
            title_guess=str(data.get("title_guess", "Unbekannter Artikel")),
            category=str(data.get("category", "Sonstiges")),
            brand=data.get("brand") or None,
            condition=str(data.get("condition", "Gebraucht")),
            condition_score=float(data.get("condition_score", 0.7)),
            features=[str(f) for f in data.get("features", [])],
            defects=[str(d) for d in data.get("defects", [])],
            confidence=float(data.get("confidence", 0.6)),
            source="claude-cli",
        )

    # ----------------------------------------------------------------- mock
    @staticmethod
    def _mock(image_path: str | None, description: str | None) -> ItemAnalysis:
        haystack = f"{image_path or ''} {description or ''}".lower()
        title, category, brand, features = _MOCK_DEFAULT
        for keyword, entry in _MOCK_TABLE.items():
            if keyword in haystack:
                title, category, brand, features = entry
                break
        return ItemAnalysis(
            title_guess=title,
            category=category,
            brand=brand,
            condition="Gebraucht – sehr gut",
            condition_score=0.85,
            features=list(features),
            defects=["leichte Gebrauchsspuren"],
            confidence=0.55,
            source="mock",
        )
