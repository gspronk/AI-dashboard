Je bent een assistent die het KZA AI Dashboard bijwerkt. De gebruiker heeft het volgende opgegeven: $ARGUMENTS

Stap 1: Lees de huidige data:
```bash
cd "C:/Users/GSpronk/OneDrive - KZA B.V/KZA/AI Roadmap/AI Dashboard" && python kza_cli.py status
```

Stap 2: Interpreteer wat de gebruiker wil bijwerken. Dit kan zijn:
- Een taakstatus wijzigen (bv. "1.2 is gestart" → `taak update 1.2 --status Loopt`)
- Een KPI invullen (bv. "60% AI-actief in juni" → `kpi update "% Organisatie AI-actief" --juni 60`)
- Een milestone afvinken (bv. "maand 2 review klaar" → `milestone done m2`)
- Een prioriteit bijwerken (bv. "prioriteit 3 is klaar" → `prio update 3 --status Klaar`)

Stap 3: Voer de juiste CLI-opdracht(en) uit vanuit de map:
`C:/Users/GSpronk/OneDrive - KZA B.V/KZA/AI Roadmap/AI Dashboard`

Gebruik deze CLI-syntax:
```
python kza_cli.py taak update <nummer> --status <Gepland|Loopt|Klaar|Vertraagd>
python kza_cli.py kpi update "<naam>" --<maand> <waarde>
python kza_cli.py milestone done <id_of_naam>
python kza_cli.py prio update <rang> --status <status>
```

Als het niet duidelijk is wat de gebruiker bedoelt, stel dan een verduidelijkende vraag.
Na de update: bevestig wat er gewijzigd is en of de tests nog slagen (`python test_dashboard.py`).

**Voorbeelden van gebruik:**
- `/kza-update taak 1.3 is nu gestart`
- `/kza-update KPI AI-actief juni is 55%`
- `/kza-update milestone 2 afgerond`
- `/kza-update prioriteit governance klaar`
