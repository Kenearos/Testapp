"""End-to-End-Test des Photo-to-Listing-Workflows (Mock-Pfad)."""

import unittest

from src.agents.orchestrator import Orchestrator
from src.llm import ClaudeClient
from src.models import ListingResult
from src.workflow import photo_to_listing


class WorkflowTest(unittest.TestCase):
    def test_orchestrator_end_to_end(self):
        orch = Orchestrator(ClaudeClient(mode="mock"))
        result = orch.photo_to_listing(description="gebrauchte Bluetooth-Kopfhörer")
        self.assertIsInstance(result, ListingResult)
        # Daten fließen sauber durch die Kette:
        self.assertEqual(result.listing.price, result.price.suggested_price)
        self.assertLessEqual(len(result.listing.title), 80)
        self.assertTrue(result.listing.description)

    def test_workflow_facade(self):
        result = photo_to_listing(description="Sneaker Gr. 43", mode="mock")
        self.assertIsInstance(result, ListingResult)

    def test_requires_input(self):
        orch = Orchestrator(ClaudeClient(mode="mock"))
        with self.assertRaises(ValueError):
            orch.photo_to_listing()

    def test_chat_via_orchestrator(self):
        orch = Orchestrator(ClaudeClient(mode="mock"))
        result = orch.photo_to_listing(description="Kopfhörer")
        reply = orch.answer_question("Was kostet der Versand?", result.listing)
        self.assertFalse(reply.escalate)


if __name__ == "__main__":
    unittest.main()
