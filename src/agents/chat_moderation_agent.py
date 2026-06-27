"""Chat-Moderation-Agent.

Eingang: Käufernachricht + Listing-Kontext.
Ausgang: :class:`~src.models.ChatReply` (Antwortvorschlag, ggf. Eskalation).
"""

from __future__ import annotations

from ..models import ChatReply, Listing
from .base import BaseAgent

_PROMPT = (
    "Du bist ein freundlicher, knapper eBay-Verkäufer-Assistent. Beantworte die "
    "Käuferfrage zum folgenden Angebot sachlich auf Deutsch. Erfinde keine Fakten, "
    "die nicht aus dem Angebot hervorgehen. Eskaliere (escalate=true), wenn es um "
    "Reklamation, Rückgabe, Beschwerde, Streit oder rechtliche Themen geht.\n\n"
    "Angebot:\nTitel: {title}\nPreis: {price} {currency}\n"
    "Beschreibung: {description}\n\n"
    "Käuferfrage: {question}\n\n"
    'JSON-Schema:\n{{ "answer": str, "escalate": bool }}'
)

# Eskalations-Trigger (Mock-Pfad).
_ESCALATE = (
    "reklamation", "rückgabe", "ruckgabe", "zurück", "defekt", "kaputt",
    "beschwerde", "anwalt", "betrug", "geld zurück", "widerruf", "streit",
)

# Einfache FAQ-Intents -> Antwortbaustein (Mock-Pfad).
def _faq_answer(question: str, listing: Listing) -> str | None:
    q = question.lower()
    if any(w in q for w in ("versand", "verschick", "porto", "liefer")):
        return ("Der Versand erfolgt als versichertes Paket innerhalb von 1–2 "
                "Werktagen nach Zahlungseingang.")
    if any(w in q for w in ("preis", "vb", "verhandel", "nachlass", "günstiger", "gunstiger")):
        return (f"Der Preis beträgt {listing.price:.2f} {listing.currency} (Sofort-Kauf). "
                "Ein faires Angebot prüfe ich gern.")
    if any(w in q for w in ("zustand", "kratzer", "gebraucht", "neu")):
        zustand = listing.item_specifics.get("Zustand", "siehe Beschreibung")
        return f"Zum Zustand: {zustand}. Alle Details stehen in der Artikelbeschreibung."
    if any(w in q for w in ("verfügbar", "verfugbar", "noch da", "vorhanden")):
        return "Ja, der Artikel ist noch verfügbar."
    if any(w in q for w in ("abhol", "selbstabhol")):
        return "Abholung ist nach Absprache möglich."
    return None


class ChatModerationAgent(BaseAgent):
    name = "chat"
    role = "Chat-Moderation-Agent – beantwortet und moderiert Käuferanfragen"

    def run(self, payload) -> ChatReply:
        """``payload``: dict mit ``question`` und ``listing`` (Listing)."""
        question = payload["question"]
        listing: Listing = payload["listing"]

        prompt = _PROMPT.format(
            title=listing.title,
            price=listing.price,
            currency=listing.currency,
            description=listing.description[:600],
            question=question,
        )
        data = self._try_live_json(prompt)
        if data is not None:
            return ChatReply(
                question=question,
                answer=str(data.get("answer", "")).strip(),
                escalate=bool(data.get("escalate", False)),
                source="claude-cli",
            )
        return self._mock(question, listing)

    # ----------------------------------------------------------------- mock
    @staticmethod
    def _mock(question: str, listing: Listing) -> ChatReply:
        q = question.lower()
        if any(trigger in q for trigger in _ESCALATE):
            return ChatReply(
                question=question,
                answer=("Danke für Ihre Nachricht – ich kümmere mich persönlich darum "
                        "und melde mich zeitnah."),
                escalate=True,
                source="mock",
            )
        answer = _faq_answer(question, listing)
        if answer is None:
            answer = ("Danke für Ihre Nachricht! Alle bekannten Details stehen in der "
                      "Beschreibung – bei konkreten Rückfragen helfe ich gern weiter.")
        return ChatReply(question=question, answer=answer, escalate=False, source="mock")
