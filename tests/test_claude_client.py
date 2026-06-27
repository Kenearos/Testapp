"""Tests für den Claude-CLI-Adapter (ohne echten CLI-Aufruf)."""

import unittest

from src.llm import ClaudeClient, ClaudeUnavailable, extract_json


class ExtractJsonTest(unittest.TestCase):
    def test_plain_object(self):
        self.assertEqual(extract_json('{"a": 1}'), {"a": 1})

    def test_object_in_prose(self):
        text = 'Klar! Hier:\n```json\n{"a": 1, "b": [2, 3]}\n```\nViel Erfolg.'
        self.assertEqual(extract_json(text), {"a": 1, "b": [2, 3]})

    def test_brace_inside_string_is_ignored(self):
        self.assertEqual(extract_json('{"s": "ein } Zeichen"}'), {"s": "ein } Zeichen"})

    def test_array(self):
        self.assertEqual(extract_json("Liste: [1, 2, 3]"), [1, 2, 3])


class ClientModeTest(unittest.TestCase):
    def test_forced_mock_mode(self):
        client = ClaudeClient(mode="mock")
        self.assertEqual(client.mode, "mock")
        with self.assertRaises(ClaudeUnavailable):
            client.complete("hallo")

    def test_invalid_mode_rejected(self):
        with self.assertRaises(ValueError):
            ClaudeClient(mode="quatsch")


if __name__ == "__main__":
    unittest.main()
