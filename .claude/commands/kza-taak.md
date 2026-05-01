Werk een taak bij in het KZA AI Dashboard op basis van de opgegeven argumenten: $ARGUMENTS

Geldige opties:
- `<nummer> --status <Gepland|Loopt|Klaar|Vertraagd>`
- `<nummer> --wie "<naam>"`
- `<nummer> --deadline "<datum>"`
- `<nummer> --beschrijving "<tekst>"`
- `list` — toon alle taken

Als er geen argumenten zijn opgegeven, toon dan eerst alle taken met `python kza_cli.py taak list` zodat de gebruiker kan kiezen.

Als de argumenten duidelijk zijn, voer dan dit commando uit:

```bash
cd "C:/Users/GSpronk/OneDrive - KZA B.V/KZA/AI Roadmap/AI Dashboard" && python kza_cli.py taak $ARGUMENTS
```

Bevestig de wijziging en vraag of de gebruiker nog iets wil bijwerken.

**Voorbeelden:**
- `/kza-taak 1.1 --status Loopt`
- `/kza-taak 2.3 --wie "Gerson" --deadline "Eind augustus 2026"`
- `/kza-taak list`
