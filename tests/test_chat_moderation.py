"""Tests für den Chat-Moderation-Agenten (Mock-Pfad)."""

import unittest

from src.agents import ChatModerationAgent
from src.llm import ClaudeClient
from src.models import ChatReply, Listing


class ChatModerationTest(unittest.TestCase):
    def setUp(self):
        self.agent = ChatModerationAgent(ClaudeClient(mode="mock"))
        self.listing = Listing(
            title="Sony Kopfhörer", description="Guter Zustand.",
            category_id="112529", price=102.0,
            item_specifics={"Zustand": "Gebraucht – sehr gut"},
        )

    def _ask(self, question: str) -> ChatReply:
        return self.agent.run({"question": question, "listing": self.listing})

    def test_shipping_question(self):
        reply = self._ask("Wie hoch sind die Versandkosten?")
        self.assertFalse(reply.escalate)
        self.assertIn("Versand", reply.answer)

    def test_price_question_mentions_price(self):
        reply = self._ask("Geht der Preis noch runter?")
        self.assertIn("102", reply.answer)

    def test_complaint_escalates(self):
        reply = self._ask("Der Artikel ist defekt, ich will mein Geld zurück!")
        self.assertTrue(reply.escalate)

    def test_unknown_question_has_fallback(self):
        reply = self._ask("Welche Farbe hat die Verpackung innen?")
        self.assertFalse(reply.escalate)
        self.assertTrue(reply.answer)


if __name__ == "__main__":
    unittest.main()
