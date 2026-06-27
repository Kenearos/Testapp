"""BMAD-Basisklasse für alle Fach-Agenten.

BMAD (Business-Modular Agent Design): jeder Agent ist eigenständig, hat einen
Namen/eine Rolle, einen klar definierten Eingang und Ausgang und kennt seinen
Betriebsmodus (live über den Claude-CLI oder deterministischer Mock).
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from ..llm import ClaudeClient, ClaudeError, ClaudeUnavailable


class BaseAgent(ABC):
    """Abstrakte Basis: ein Agent = eine Verantwortung, ein ``run``."""

    #: Kurzname / BMAD-Rolle, z. B. "vision", "market".
    name: str = "base"
    #: Menschenlesbare Beschreibung der Aufgabe.
    role: str = "Basis-Agent"

    def __init__(
        self,
        client: ClaudeClient | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.client = client or ClaudeClient()
        self.log = logger or logging.getLogger(f"agent.{self.name}")

    @property
    def mode(self) -> str:
        """Effektiver Modus dieses Agenten ("live" oder "mock")."""
        return self.client.mode

    @abstractmethod
    def run(self, payload):
        """Verarbeitet eine typisierte Eingabe zu einer typisierten Ausgabe."""
        raise NotImplementedError

    # -- Helfer für abgeleitete Agenten ------------------------------------

    def _try_live_json(self, prompt: str, image_path: str | None = None):
        """Versucht einen Live-JSON-Aufruf; gibt ``None`` im Mock/Fehlerfall.

        Kapselt das wiederkehrende Muster: live versuchen, bei fehlendem CLI
        oder Fehler sauber auf den Mock-Pfad zurückfallen (BMAD-Robustheit –
        ein Agent darf nie die gesamte Pipeline reißen).
        """
        if self.mode != "live":
            return None
        try:
            return self.client.complete_json(prompt, image_path=image_path)
        except (ClaudeError, ClaudeUnavailable) as exc:
            self.log.warning("Live-Aufruf fehlgeschlagen, nutze Mock: %s", exc)
            return None

    def __repr__(self) -> str:  # pragma: no cover - Komfort
        return f"<{type(self).__name__} name={self.name!r} mode={self.mode!r}>"
