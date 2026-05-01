Beheer milestones in het KZA AI Dashboard op basis van de opgegeven argumenten: $ARGUMENTS

Geldige subcommando's:
- `done <naam_of_id>` — markeer als afgerond
- `open <naam_of_id>` — zet terug op open
- `list` — toon alle milestones

Als er geen argumenten zijn opgegeven, toon dan eerst alle milestones:

```bash
cd "C:/Users/GSpronk/OneDrive - KZA B.V/KZA/AI Roadmap/AI Dashboard" && python kza_cli.py milestone list
```

Als de argumenten duidelijk zijn, voer dan uit:

```bash
cd "C:/Users/GSpronk/OneDrive - KZA B.V/KZA/AI Roadmap/AI Dashboard" && python kza_cli.py milestone $ARGUMENTS
```

**Voorbeelden:**
- `/kza-milestone done m2`
- `/kza-milestone done "Maand 2"`
- `/kza-milestone list`
