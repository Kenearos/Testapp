"""Tests für den Bildanalyse-Agenten (Mock-Pfad)."""

import unittest

from src.agents import ImageAnalysisAgent
from src.llm import ClaudeClient
from src.models import ItemAnalysis


class ImageAnalysisTest(unittest.TestCase):
    def setUp(self):
        self.agent = ImageAnalysisAgent(ClaudeClient(mode="mock"))

    def test_returns_item_analysis(self):
        result = self.agent.run({"image_path": "fotos/sneaker_01.jpg"})
        self.assertIsInstance(result, ItemAnalysis)
        self.assertEqual(result.source, "mock")
        self.assertGreaterEqual(result.condition_score, 0.0)
        self.assertLessEqual(result.condition_score, 1.0)

    def test_keyword_routing_from_filename(self):
        result = self.agent.run({"image_path": "img/sneaker.png"})
        self.assertEqual(result.category, "Sneaker")
        self.assertEqual(result.brand, "Nike")

    def test_keyword_routing_from_description(self):
        result = self.agent.run({"description": "alte Spielkonsole mit Controller"})
        self.assertEqual(result.category, "Konsolen")

    def test_string_payload_accepted(self):
        result = self.agent.run("uhr_vintage.jpg")
        self.assertEqual(result.category, "Armbanduhren")


if __name__ == "__main__":
    unittest.main()
