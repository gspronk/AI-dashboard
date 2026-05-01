# KZA AI Dashboard – Instructies voor Claude

Dit is het projectbestand voor het KZA Doelen AI dashboard. Volg deze regels bij elke aanpassing.

## Projectstructuur

| Bestand            | Doel                                              |
|--------------------|---------------------------------------------------|
| `kza_dashboard.py` | Streamlit dashboard (start via start_dashboard.bat) |
| `kza_cli.py`       | CLI tool voor data-updates via agent/terminal     |
| `kza_data.json`    | Alle data: taken, KPI's, milestones, prioriteiten |
| `test_dashboard.py`| Automatische tests – altijd uitvoeren na wijziging |
| `CLAUDE.md`        | Dit bestand                                       |

## Datastructuur kza_data.json

Sleutels: `taken`, `milestones`, `kpis`, `prioriteiten`, `waarde_medewerkers`, `waarde_bedrijven`

Geldige statuswaarden voor taken en prioriteiten: `Gepland` | `Loopt` | `Klaar` | `Vertraagd`

KPI-maandkolommen: `Mei`, `Juni`, `Juli`, `Aug`, `Sep`, `Okt`

## CLI-commando's (snelreferentie)

```bash
python kza_cli.py status
python kza_cli.py taak update <nummer> --status <status>
python kza_cli.py taak add
python kza_cli.py kpi update "<naam>" --<maand> <waarde>
python kza_cli.py milestone done <id_of_naam>
python kza_cli.py prio update <rang> --status <status>
```

## Werkwijze bij elke ontwikkeling

### Nooit data overschrijven zonder eerst te lezen

De gebruiker slaat tussendoor zelf data op via het Streamlit dashboard (omschrijvingen, KPI-metingen, statuswijzigingen, milestone-notities). Een volledige herschrijving van `kza_data.json` gooit die edits weg.

**Regels voor het muteren van `kza_data.json`:**

1. **Lees altijd éérst** de huidige `kza_data.json` in met `Read` voordat je iets schrijft.
2. **Muteer alleen de velden die expliciet aan de orde zijn.** Alle overige sleutels, taken, KPI's, milestones, prioriteiten en waardeproposities blijven exact zoals ze waren.
3. **Gebruik bij voorkeur de CLI** voor kleine wijzigingen — die past surgisch één veld aan:
   - `python kza_cli.py taak update <nummer> --status <s>` / `--wie` / `--deadline` / `--beschrijving`
   - `python kza_cli.py kpi update "<naam>" --<maand> <waarde>`
   - `python kza_cli.py milestone done <id_of_naam>` / `milestone open <id_of_naam>`
   - `python kza_cli.py prio update <rang> --status <s>` / `--urgentie`
4. **Volledige herschrijving alleen bij expliciete opdracht** (bijv. "reset alle taken"). In alle andere gevallen: lees → muteer → schrijf terug.
5. **Bij bulk-wijzigingen via Python-script**: laad eerst `json.load()`, wijzig alleen de target-keys in de in-memory dict, en doe dan `json.dump()` — nooit een volledig opnieuw opgebouwde dict schrijven tenzij dat expliciet is gevraagd.

### Na elke wijziging aan dashboard of CLI — altijd:

1. **Voer de tests uit** voordat je rapporteert dat iets klaar is:
   ```bash
   python test_dashboard.py
   ```

2. **Alle tests moeten slagen.** Bij een falende test: fix eerst de code, dan pas afronden.

3. **Pas de tests aan bij nieuwe features.** Voeg een test toe in `test_dashboard.py` voor elke:
   - Nieuw CLI-commando of nieuwe optie
   - Nieuw dashboard-scherm of nieuwe sectie
   - Nieuw veld in `kza_data.json`
   - Bugfix (schrijf een regressietest die de bug reproduceert)

4. **Schrijf bestanden via bash** (`cat > bestand << 'EOF'`), niet via de Write-tool — die kan bestanden afkappen bij grote inhoud.

## Bekende valkuilen

- `pd.DataFrame([])` geeft een lege DataFrame zonder kolommen — gebruik altijd `columns=` mee bij aanmaken, of `.rename(columns=...)` na aanmaken met expliciete kolommen.
- Streamlit laadt `kza_data.json` bij elke page-load. Na een CLI-update: gebruik de Vernieuwen-knop of F5 in de browser.
- De Write-tool kan grote bestanden afkappen. Gebruik bash voor bestanden groter dan ~100 regels.
