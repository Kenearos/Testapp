# eBay-Auto-Lister

**Automatisiertes Multi-Agent-System zur Erstellung und Verwaltung von eBay-Verkaufsangeboten.**

Der eBay-Auto-Lister analysiert Produktfotos, recherchiert aktuelle Marktpreise, generiert verkaufsoptimierte Listings und beantwortet Käuferanfragen – vollständig orchestriert durch ein BMAD-basiertes Agenten-Framework.

---

## Features / Was die App macht

- Automatische Artikelerkennung und Zustandsbewertung anhand von Produktfotos
- Marktpreisrecherche über verkaufte eBay-Artikel und weitere Marktplätze
- KI-generierte Verkaufstexte (Titel, Beschreibung, Kategorie, Attribute)
- Automatische Beantwortung und Moderation von Käufernachrichten
- Koordinierter Ablauf aller Agenten durch einen zentralen Orchestrator
- Erweiterbare Architektur nach BMAD-Prinzipien

---

## Die vier Fach-Agenten

| Agent | Aufgabe | Input | Output |
|---|---|---|---|
| **Bildanalyse-Agent** | Analysiert Produktfotos; erkennt Artikel, Zustand und Merkmale | Produktfotos (JPG/PNG) | Strukturierte Artikelbeschreibung (Typ, Zustand, Merkmale) |
| **Preis-Recherche-Agent** | Recherchiert Marktpreise über verkaufte Listings und Marktplätze; schlägt optimalen Verkaufspreis vor | Artikelbeschreibung vom Bildanalyse-Agenten | Preisvorschlag mit Marktdaten und Begründung |
| **Listing-Erstellung-Agent** | Erzeugt eBay-konformen Titel, Beschreibung, Kategorie und Produktattribute | Artikelbeschreibung + Preisvorschlag | Fertiges Listing (Titel, Beschreibung, Kategorie-ID, Attribute) |
| **Chat-Moderation-Agent** | Beantwortet Käuferfragen, moderiert Nachrichten und eskaliert bei Bedarf | Eingehende Käufernachrichten + Listing-Kontext | Antwortvorschläge bzw. automatische Antworten |

---

## BMAD-Orchestrierung

Das System folgt dem **BMAD-Orchestrator-Pattern** (Business-Modular Agent Design):

Ein zentraler **Orchestrator** nimmt den Nutzerauftrag entgegen, zerlegt ihn in Teilaufgaben und delegiert diese sequenziell oder parallel an die zuständigen Fach-Agenten. Jeder Agent ist eigenständig, hat klar definierte Eingaben und Ausgaben und kommuniziert ausschließlich über standardisierte Datenstrukturen (JSON/Pydantic-Modelle).

```
Nutzer
  └─► Orchestrator
        ├─► Bildanalyse-Agent      → Artikeldaten
        ├─► Preis-Recherche-Agent  → Preisvorschlag
        ├─► Listing-Erstellung-Agent → fertiges Listing
        └─► Chat-Moderation-Agent  → Käufer-Antworten
```

Der Orchestrator aggregiert alle Ergebnisse, behandelt Fehler und gibt dem Nutzer eine einheitliche Rückmeldung. Agenten können unabhängig ausgetauscht oder erweitert werden.

---

## Projektstruktur

```
Testapp/
├── src/
│   ├── agents/
│   │   ├── orchestrator.py          # Zentraler Orchestrator
│   │   ├── image_analysis_agent.py  # Bildanalyse-Agent
│   │   ├── price_research_agent.py  # Preis-Recherche-Agent
│   │   ├── listing_agent.py         # Listing-Erstellung-Agent
│   │   └── chat_moderation_agent.py # Chat-Moderation-Agent
│   ├── scrapers/
│   │   ├── ebay_sold_scraper.py     # Scraper für verkaufte eBay-Artikel
│   │   └── marketplace_scraper.py   # Weitere Marktplatz-Daten
│   ├── api/
│   │   ├── ebay_api.py              # eBay API-Integration
│   │   └── models.py                # Pydantic-Datenmodelle
│   └── __init__.py
├── docs/
│   ├── architecture.md              # Systemarchitektur
│   └── agent_specs.md               # Agenten-Spezifikationen
├── tests/
│   ├── test_image_analysis.py
│   ├── test_price_research.py
│   ├── test_listing.py
│   └── test_chat_moderation.py
├── spike/
│   └── concept_spike.py             # Proof-of-Concept (keine externen Abhängigkeiten)
├── .env                             # Secrets (NICHT committen, siehe Sicherheit)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Schnellstart / Setup

### Voraussetzungen

- Python 3.10+
- (Optional) eBay Developer Account für API-Zugang

### Installation

```bash
# Repository klonen
git clone <repo-url>
cd Testapp

# Virtuelle Umgebung erstellen und aktivieren
python3 -m venv .venv
source .venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# .env-Datei anlegen (Vorlage: .env.example)
cp .env.example .env
# .env mit eigenen API-Keys befüllen (siehe Sicherheit & Secrets)
```

### Concept Spike (ohne externe Pakete)

Der Spike demonstriert das Grundprinzip der Agenten-Orchestrierung mit reinem Python — keine Installation erforderlich:

```bash
python3 spike/concept_spike.py
```

### Photo-to-Listing-Prototyp (end-to-end)

```bash
# Vollständige Demo im deterministischen Mock-Modus (kein Netz nötig)
python3 spike/prototype.py --mock

# Mit echtem Produktfoto über den authentifizierten claude-CLI
python3 spike/prototype.py --image /pfad/zum/foto.jpg --live

# Nur maschinenlesbares JSON-Ergebnis
python3 spike/prototype.py --mock --json
```

### Orchestrator direkt aufrufen

```bash
python3 -m src.agents.orchestrator --description "gebrauchte Bluetooth-Kopfhörer"
```

### Tests

```bash
python3 -m unittest discover -s tests -v
```

---

## Status / Roadmap

| Phase | Status | Beschreibung |
|---|---|---|
| Grundgerüst | ✅ Fertig | Projektstruktur, BMAD-Basisklasse, Datenmodelle |
| Concept Spike + Prototyp | ✅ Fertig | `spike/prototype.py` — Photo-to-Listing end-to-end |
| Bildanalyse-Agent | ✅ Fertig (v0.1) | Live über `claude -p` (Vision), deterministischer Mock-Fallback |
| Preis-Recherche-Agent | ✅ Fertig (v0.1) | Modell-Schätzung (Live) / Kategorie-Heuristik (Mock) |
| Listing-Erstellung-Agent | ✅ Fertig (v0.1) | Titel/Beschreibung/Kategorie/Attribute |
| Chat-Moderation-Agent | ✅ Fertig (v0.1) | FAQ-Antworten + Eskalation |
| Tests | ✅ Fertig | 28 `unittest`-Tests (Stdlib, offline deterministisch) |
| eBay API-Integration | 📋 Geplant | Trading API / Listing-Upload, echte Preisrecherche |
| CI | 📋 Geplant | GitHub Actions |

> **v0.1-Hinweis:** Der Prototyp läuft Stdlib-only. LLM-Agenten nutzen den lokal
> authentifizierten `claude`-CLI (`claude -p`) statt eines API-Keys im Code; ohne
> CLI/Netz schalten alle Agenten automatisch auf einen deterministischen Mock um.
> Details: [`docs/agent_specs.md`](docs/agent_specs.md).

---

## Sicherheit & Secrets

**Niemals API-Keys oder Passwörter im Klartext committen.**

Dieses Projekt verwendet **SOPS + age** zur verschlüsselten Verwaltung aller Secrets:

```bash
# Secret sicher bearbeiten
/opt/secrets/secrets.sh edit <app-name>

# .env nach Änderung verschlüsseln
/opt/secrets/secrets.sh encrypt <app-name>

# .env aus verschlüsselter Datei wiederherstellen
/opt/secrets/secrets.sh decrypt <app-name>
```

**Regeln:**
- `.env`-Dateien müssen `chmod 600` haben
- `.env` ist in `.gitignore` eingetragen — unter keinen Umständen committen
- Neue Secrets immer zuerst in `secrets.sh` registrieren, dann verschlüsseln
- Encrypted Secrets liegen unter `/opt/secrets/*.enc.env`

---

## Rechtlicher Hinweis

- **eBay API:** Die Nutzung der eBay-API unterliegt den [eBay Developer Program Agreement](https://developer.ebay.com) und den geltenden Nutzungsbedingungen. Vor dem Produktiveinsatz ist ein gültiger API-Key erforderlich.
- **Scraping:** Web-Scraping ist nur im Rahmen der eBay-Nutzungsbedingungen zulässig. Automatisiertes Scraping, das gegen die Terms of Service verstößt, ist verboten und nicht Bestandteil dieses Projekts.
- **Dieses Projekt** dient ausschließlich dem legalen Eigengebrauch. Der Betreiber übernimmt keine Haftung für missbräuchliche Nutzung.

---

## Lizenz

*Lizenz: Platzhalter — noch nicht festgelegt.*
