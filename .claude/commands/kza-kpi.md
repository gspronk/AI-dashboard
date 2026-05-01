Werk een KPI-meting bij in het KZA AI Dashboard op basis van de opgegeven argumenten: $ARGUMENTS

Geldige maanden: `--mei`, `--juni`, `--juli`, `--aug`, `--sep`, `--okt`

Als er geen argumenten zijn opgegeven, toon dan eerst alle KPI's met `python kza_cli.py kpi list` zodat de gebruiker kan kiezen.

Als de argumenten duidelijk zijn, voer dan dit commando uit:

```bash
cd "C:/Users/GSpronk/OneDrive - KZA B.V/KZA/AI Roadmap/AI Dashboard" && python kza_cli.py kpi update $ARGUMENTS
```

**Voorbeelden:**
- `/kza-kpi "% Organisatie AI-actief" --juni 52`
- `/kza-kpi "Actieve AI-tool users" --mei 30 --juni 45`
- `/kza-kpi list`

Na de update: toon de bijgewerkte KPI-waarden.
