"""Adapter für den bereits authentifizierten ``claude`` Command-Line-Client.

Statt einen API-Key im Code zu halten (siehe SOPS/age-Policy), rufen die
LLM-gestützten Agenten den lokal installierten ``claude``-CLI als Subprozess
auf (``claude -p``). Ist der CLI nicht verfügbar, melden die Agenten das über
``ClaudeUnavailable`` und schalten auf ihren deterministischen Mock-Pfad um –
so bleibt der Prototyp auch offline / in CI lauffähig.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess


class ClaudeError(RuntimeError):
    """Der CLI wurde aufgerufen, lieferte aber einen Fehler."""


class ClaudeUnavailable(RuntimeError):
    """Der CLI ist nicht installiert oder Mock-Modus ist erzwungen."""


def extract_json(text: str):
    """Extrahiert das erste vollständige JSON-Objekt/-Array aus ``text``.

    Modelle verpacken JSON gern in Prosa oder ```-Codeblöcke. Diese Funktion
    ist tolerant: erst direktes ``json.loads``, dann Suche nach dem ersten
    balancierten ``{...}``/``[...]``.
    """
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        if start == -1:
            continue
        depth = 0
        in_str = False
        escape = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    candidate = text[start : i + 1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        break
    raise ClaudeError(f"Keine gültige JSON-Antwort gefunden in:\n{text[:500]}")


class ClaudeClient:
    """Dünner Wrapper um ``claude -p``.

    Parameter
    ---------
    mode: ``"auto"`` (live wenn CLI da, sonst mock), ``"live"`` oder ``"mock"``.
    model: optionales Modell-Override (sonst CLI-Default bzw. ``CLAUDE_MODEL``).
    timeout: Sekunden bis Abbruch eines Aufrufs.
    """

    def __init__(
        self,
        mode: str = "auto",
        model: str | None = None,
        timeout: int = 180,
        cli: str = "claude",
        allowed_tools: str = "Read",
    ) -> None:
        if mode not in ("auto", "live", "mock"):
            raise ValueError(f"Ungültiger mode: {mode!r}")
        self._mode = mode
        self.cli = cli
        self.model = model or os.environ.get("CLAUDE_MODEL")
        self.timeout = timeout
        self.allowed_tools = allowed_tools

    def available(self) -> bool:
        return shutil.which(self.cli) is not None

    @property
    def mode(self) -> str:
        """Effektiver Modus: löst ``"auto"`` zur Laufzeit auf."""
        if self._mode == "auto":
            return "live" if self.available() else "mock"
        return self._mode

    def complete(
        self,
        prompt: str,
        image_path: str | None = None,
        system: str | None = None,
    ) -> str:
        """Sendet ``prompt`` an den CLI und liefert die Textantwort."""
        if self.mode == "mock":
            raise ClaudeUnavailable("ClaudeClient läuft im Mock-Modus")
        if not self.available():
            raise ClaudeUnavailable(f"CLI {self.cli!r} nicht im PATH")

        full = prompt
        if image_path:
            full = (
                f"Lies und analysiere die Bilddatei unter dem absoluten Pfad: "
                f"{image_path}\n\n{prompt}"
            )

        cmd = [self.cli, "-p", full]
        if self.model:
            cmd += ["--model", self.model]
        if system:
            cmd += ["--append-system-prompt", system]
        if image_path and self.allowed_tools:
            # Lesezugriff auf die Bilddatei vorab erlauben -> kein Prompt im
            # nicht-interaktiven Modus.
            cmd += ["--allowed-tools", self.allowed_tools]

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise ClaudeError(f"Timeout nach {self.timeout}s") from exc
        except FileNotFoundError as exc:
            raise ClaudeUnavailable(str(exc)) from exc

        if proc.returncode != 0:
            raise ClaudeError(proc.stderr.strip() or f"exit code {proc.returncode}")
        return proc.stdout.strip()

    def complete_json(
        self,
        prompt: str,
        image_path: str | None = None,
        system: str | None = None,
    ):
        """Wie :meth:`complete`, parst die Antwort aber als JSON."""
        text = self.complete(
            prompt + "\n\nAntworte AUSSCHLIESSLICH mit gültigem JSON "
            "(ohne Markdown-Codeblock, ohne erklärenden Text davor oder danach).",
            image_path=image_path,
            system=system,
        )
        return extract_json(text)
