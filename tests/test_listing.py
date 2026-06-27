"""Tests für den Listing-Erstellung-Agenten (Mock-Pfad)."""

import unittest

from src.agents import ListingAgent
from src.llm import ClaudeClient
from src.models import ItemAnalysis, Listing, PriceSuggestion


class ListingTest(unittest.TestCase):
    def setUp(self):
        self.agent = ListingAgent(ClaudeClient(mode="mock"))
        self.analysis = ItemAnalysis(
            title_guess="Over-Ear Kopfhörer", category="Kopfhörer",
            condition="Gebraucht – sehr gut", condition_score=0.85,
            brand="Sony", features=["Bluetooth", "ANC"],
        )
        self.price = PriceSuggestion(
            suggested_price=102.0, price_min=87.0, price_max=117.0,
        )

    def test_returns_listing(self):
        listing = self.agent.run((self.analysis, self.price))
        self.assertIsInstance(listing, Listing)
        self.assertEqual(listing.price, 102.0)

    def test_title_respects_ebay_limit(self):
        listing = self.agent.run((self.analysis, self.price))
        self.assertLessEqual(len(listing.title), 80)
        self.assertIn("Sony", listing.title)

    def test_category_id_mapped(self):
        listing = self.agent.run((self.analysis, self.price))
        self.assertEqual(listing.category_id, "112529")  # Kopfhörer

    def test_item_specifics_present(self):
        listing = self.agent.run((self.analysis, self.price))
        self.assertEqual(listing.item_specifics.get("Marke"), "Sony")

    def test_dict_payload(self):
        listing = self.agent.run({"analysis": self.analysis, "price": self.price})
        self.assertIsInstance(listing, Listing)


if __name__ == "__main__":
    unittest.main()
