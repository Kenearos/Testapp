"""Tests für die Datenmodelle / Serialisierung."""

import json
import unittest

from src.models import (
    ChatReply,
    ItemAnalysis,
    Listing,
    ListingResult,
    PriceSuggestion,
)


class ModelsTest(unittest.TestCase):
    def _result(self) -> ListingResult:
        return ListingResult(
            analysis=ItemAnalysis(
                title_guess="Kopfhörer", category="Kopfhörer",
                condition="Gut", condition_score=0.8,
            ),
            price=PriceSuggestion(suggested_price=99.0, price_min=84.0, price_max=114.0),
            listing=Listing(title="T", description="D", category_id="1", price=99.0),
        )

    def test_to_json_is_valid_and_roundtrips(self):
        result = self._result()
        parsed = json.loads(result.to_json())
        self.assertEqual(parsed["price"]["suggested_price"], 99.0)
        self.assertIn("title_guess", parsed["analysis"])
        self.assertEqual(parsed["listing"]["title"], "T")

    def test_defaults(self):
        reply = ChatReply(question="?", answer="!")
        self.assertFalse(reply.escalate)
        self.assertEqual(reply.source, "mock")


if __name__ == "__main__":
    unittest.main()
