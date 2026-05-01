# KZA Doelen AI – Dashboard

Visuele tracker van de KZA AI-strategie 2026: taken per pijler, KPI's, milestones, prioriteiten en waardepropositie.

## 🌐 Dashboard openen

**URL:** [ai-dashboard-kza.streamlit.app](https://ai-dashboard-kza.streamlit.app)

Het dashboard zit achter een wachtwoord. Vraag het wachtwoord op bij **Gerson** (gspronk@kza.nl) om toegang te krijgen.

Eenmaal ingelogd zie je de navigatie aan de linkerkant:

| Tab | Inhoud |
|-----|--------|
| 🏠 Dashboard | Overzicht: status per pijler, milestones-voortgang, KPI-snapshot |
| 📋 Taken | Alle taken met status, deadline en beschrijving — bewerkbaar |
| 🎯 Milestones | Milestone-overzicht met bewerk-formulier en tijdlijn-visualisatie |
| 📈 KPI's | Maandelijkse KPI-waarden + trendgrafiek |
| 🏆 Prioriteiten | Prioriteitenmatrix met urgentie en impact |
| 💡 Waardepropositie | Wat levert het op voor medewerkers en bedrijven |

Wijzigingen worden automatisch opgeslagen en zijn meteen zichtbaar voor andere gebruikers (via een gedeelde GitHub Gist als opslag).

## 🔧 Lokaal draaien (voor ontwikkelaars)

```bash
# Eenmalig: dependencies
pip install -r requirements.txt

# Starten
streamlit run kza_dashboard.py
```

Lokaal draait het dashboard zonder wachtwoord en slaat het op naar `kza_data.json` in dezelfde map. Wil je lokaal de Gist-backend testen? Maak dan `.streamlit/secrets.toml` aan op basis van `.streamlit/secrets.toml.example`.

## 📁 Bestanden

| Bestand | Doel |
|---------|------|
| `kza_dashboard.py` | Streamlit dashboard |
| `kza_cli.py` | CLI voor data-updates via terminal of agent |
| `kza_data.json` | Alle data: taken, KPI's, milestones, prioriteiten, waardeproposities |
| `test_dashboard.py` | Automatische tests — altijd uitvoeren na wijziging |
| `requirements.txt` | Python-dependencies |
| `.streamlit/secrets.toml.example` | Voorbeeld voor wachtwoord en Gist-config |
| `CLAUDE.md` | Instructies voor de AI-agent die het dashboard onderhoudt |

## ⌨️ CLI-commando's voor data-updates

```bash
python kza_cli.py status
python kza_cli.py taak update <nummer> --status <Gepland|Loopt|Klaar|Vertraagd>
python kza_cli.py kpi update "<naam>" --<maand> <waarde>
python kza_cli.py milestone done <id_of_naam>
python kza_cli.py prio update <rang> --status <status>
```

> Let op: de CLI werkt op het lokale `kza_data.json`. Voor wijzigingen die in de gedeelde cloud-versie moeten landen, gebruik je het dashboard (dat schrijft naar de Gist).

## 🧪 Tests

```bash
python test_dashboard.py
```

Alle tests moeten slagen voor een wijziging definitief is.
