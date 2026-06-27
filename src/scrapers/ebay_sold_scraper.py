"""Stub für die Recherche verkaufter eBay-Artikel.

WICHTIG / RECHTLICH: Automatisiertes Scraping von eBay unterliegt den
eBay-Nutzungsbedingungen. Eine produktive Umsetzung MUSS die offizielle
eBay-API (z. B. Marketplace Insights / Browse API) mit gültigem Developer-Key
nutzen, nicht das HTML-Scraping der Website.

Dieser Stub ist absichtlich nicht implementiert; der Preis-Recherche-Agent
arbeitet stattdessen mit einer Heuristik (Mock) bzw. der Markteinschätzung des
Modells (Live).
"""

from __future__ import annotations


class EbaySoldScraper:
    """Platzhalter – noch nicht implementiert (siehe Rechtshinweis oben)."""

    def search_sold(self, query: str, limit: int = 20) -> list[dict]:
        raise NotImplementedError(
            "Verkaufte Listings bitte über die offizielle eBay-API beziehen "
            "(Marketplace Insights API). HTML-Scraping ist nicht implementiert."
        )
