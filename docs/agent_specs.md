# Agenten-Spezifikation — Implementierungsstand v0.1

Dieses Dokument beschreibt die **tatsächlich implementierten** Agenten des
Photo-to-Listing-Prototyps. Es ergänzt das Ziel-Design in
[`architecture.md`](architecture.md) um den konkreten Ist-Zustand.

## Designentscheidungen v0.1 (Abweichungen vom Ziel-Design)

| Thema | Ziel-Design (`architecture.md`) | Prototyp v0.1 | Begründung |
|---|---|---|---|
| Validierung | Pydantic v2 | `dataclasses` (Stdlib) | Spike/Agenten laufen **ohne** `pip install` (siehe `requirements.txt`) |
| LLM-Zugang | Anthropic API + `ANTHROPIC_API_KEY` | lokaler **`claude -p`** CLI | Kein Klartext-Key im Code (SOPS-Policy); CLI ist bereits authentifiziert |
| Preisdaten | eBay Finding API | Heuristik (Mock) bzw. Modell-Schätzung (Live) | Echtes Scraping = AGB-/Rechtsthema, bewusst nicht enthalten |
| Robustheit | Retry/Backoff | Mock-Fallback je Agent | Ein Agent darf die Pipeline nie reißen; Prototyp bleibt offline lauffähig |

Jeder LLM-gestützte Agent hat zwei Pfade:
- **live** — ruft `claude -p` auf (wenn CLI vorhanden, sonst automatisch Fallback),
- **mock** — deterministische Logik, garantiert offline/in CI reproduzierbar.

Der Betriebsmodus wird zentral über `ClaudeClient(mode="auto"|"live"|"mock")`
gesetzt und vom Orchestrator an alle Agenten durchgereicht.

---

## Orchestrator — `src/agents/orchestrator.py`

| Eigenschaft | Wert |
|---|---|
| Rolle | Zentraler Koordinator (BMAD-Orchestrator-Pattern) |
| Kein KI-Modell | reine Python-Orchestrierung |
| Kern-Methode | `photo_to_listing(image_path=None, description=None) -> ListingResult` |
| Chat-Methode | `answer_question(question, listing) -> ChatReply` |
| Ablauf | Vision → Market → Listing, danach optional Chat |

---

## Vision — `ImageAnalysisAgent` (`image_analysis_agent.py`)

| Eigenschaft | Wert |
|---|---|
| Rolle | Bildanalyse: Artikel, Zustand, Merkmale erkennen |
| Input | `{"image_path": str, "description": str}` (oder Pfad-String) |
| Output | `ItemAnalysis(title_guess, category, brand, condition, condition_score, features, defects, confidence, source)` |
| Live | `claude -p` liest die Bilddatei (Tool `Read`) und liefert JSON |
| Mock | Stichwort-Heuristik aus Dateiname/Beschreibung → plausibles Beispielobjekt |

## Market — `PriceResearchAgent` (`price_research_agent.py`)

| Eigenschaft | Wert |
|---|---|
| Rolle | Marktpreis vorschlagen |
| Input | `ItemAnalysis` |
| Output | `PriceSuggestion(suggested_price, price_min, price_max, currency, sample_size, rationale, source)` |
| Live | Modell schätzt Preisspanne (deutscher eBay-Markt) als JSON |
| Mock | Basispreis je Kategorie × Zustands-Faktor (0,5 … 1,0) |

## Listing — `ListingAgent` (`listing_agent.py`)

| Eigenschaft | Wert |
|---|---|
| Rolle | eBay-konformes Listing erzeugen |
| Input | `(ItemAnalysis, PriceSuggestion)` (oder dict) |
| Output | `Listing(title≤80, description, category_id, item_specifics, price, currency, source)` |
| Live | Modell erzeugt Titel/Text/Attribute als JSON |
| Mock | Template: Titel aus Marke+Artikel+Zustand, Beschreibung mit Stichpunkten, Kategorie-ID-Lookup |

## Chat — `ChatModerationAgent` (`chat_moderation_agent.py`)

| Eigenschaft | Wert |
|---|---|
| Rolle | Käuferfragen beantworten / eskalieren |
| Input | `{"question": str, "listing": Listing}` |
| Output | `ChatReply(question, answer, escalate, source)` |
| Live | Modell antwortet + setzt `escalate` bei Reklamation/Recht |
| Mock | FAQ-Intents (Versand, Preis, Zustand, Verfügbarkeit) + Eskalations-Stichwörter |

---

## Datenfluss (implementiert)

```
Foto/Text
   │
   ▼  ImageAnalysisAgent
ItemAnalysis
   │
   ▼  PriceResearchAgent
PriceSuggestion
   │
   ▼  ListingAgent
Listing ──► ListingResult (analysis + price + listing)
   │
   ▼  ChatModerationAgent (auf Käuferfrage)
ChatReply
```

Alle Strukturen sind in `src/models.py` definiert und über `.to_dict()` /
`.to_json()` serialisierbar.
