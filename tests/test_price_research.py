"""Tests für den Preis-Recherche-Agenten (Mock-Pfad)."""

import unittest

from src.agents import PriceResearchAgent
from src.llm import ClaudeClient
from src.models import ItemAnalysis, PriceSuggestion


def _item(category="Kopfhörer", score=1.0):
    return ItemAnalysis(
        title_guess="Test", category=category,
        condition="Neu", condition_score=score, brand="Marke",
    )


class PriceResearchTest(unittest.TestCase):
    def setUp(self):
        self.agent = PriceResearchAgent(ClaudeClient(mode="mock"))

    def test_returns_price_suggestion(self):
        price = self.agent.run(_item())
        self.assertIsInstance(price, PriceSuggestion)
        self.assertEqual(price.currency, "EUR")
        self.assertLess(price.price_min, price.price_max)

    def test_condition_scales_price(self):
        good = self.agent.run(_item(score=1.0)).suggested_price
        worn = self.agent.run(_item(score=0.0)).suggested_price
        self.assertGreater(good, worn)

    def test_category_affects_base_price(self):
        headphones = self.agent.run(_item(category="Kopfhörer")).suggested_price
        unknown = self.agent.run(_item(category="Irgendwas")).suggested_price
        self.assertGreater(headphones, unknown)


if __name__ == "__main__":
    unittest.main()
