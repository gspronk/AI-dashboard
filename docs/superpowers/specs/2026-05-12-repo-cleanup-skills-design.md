# Design: Repo opruimen + Skills introduceren

**Datum:** 2026-05-12  
**Project:** KZA AI Dashboard  
**Status:** Goedgekeurd door gebruiker

---

## Doel

De repo opschonen van onnodige binaire bestanden en externe skills installeren die de dagelijkse werkwijze met Claude Code verbeteren.

---

## 1. Repo cleanup

### Wat wordt verwijderd

| Bestand | Reden |
|---------|-------|
| `KZA_Doelen_AI.xlsx` | Originele brondata, niet meer nodig nu alles in `kza_data.json` zit |
| `kza-update.skill` | Binair skill-bestand in de root; overbodige kopie — inhoud zit al in `.claude/commands/kza-update.md` |

### .gitignore uitbreiden

Voeg toe aan `.gitignore`:
```
*.xlsx
*.docx
*.skill
```

Dit voorkomt dat dit soort bestanden in de toekomst per ongeluk worden gecommit.

---

## 2. Skills installeren

Vier skills via `npx skilladd` installeren in `.claude/skills/`:

| Skill | Bron | Installs | Install-commando |
|-------|------|----------|-----------------|
| `find-skills` | vercel-labs/skills | 20.2K | `npx skilladd vercel-labs/skills/find-skills` |
| `webapp-testing` | anthropics/skills | 66.6K | `npx skilladd anthropics/skills/webapp-testing` |
| `grill-me` | mattpocock/skills | 8.0K | `npx skilladd mattpocock/skills/grill-me` |
| `pptx` | anthropics/skills | 98.7K | `npx skilladd anthropics/skills/pptx` |

### Gebruik na installatie

- `/find-skills` — beschrijf een taak, krijg een aanbeveling welke skill te gebruiken
- `/webapp-testing` — betere tests schrijven voor `test_dashboard.py`
- `/grill-me` — plan of ontwerp laten uitdagen met kritische vragen vóór implementatie
- `/pptx` — PowerPoint-rapportages genereren vanuit dashboard-data

---

## 3. Eindstructuur repo

```
├── .claude/
│   ├── commands/          # KZA slash commands (ongewijzigd)
│   │   ├── kza-kpi.md
│   │   ├── kza-milestone.md
│   │   ├── kza-status.md
│   │   ├── kza-taak.md
│   │   └── kza-update.md
│   └── skills/            # Externe skills (nieuw)
│       ├── find-skills/
│       ├── webapp-testing/
│       ├── grill-me/
│       └── pptx/
├── kza_dashboard.py
├── kza_cli.py
├── kza_data.json
├── test_dashboard.py
├── requirements.txt
├── start_dashboard.bat
├── CLAUDE.md
└── README.md
```

---

## 4. Wat niet verandert

- `.claude/commands/` — alle KZA-specifieke slash commands blijven onaangeroerd
- `kza_dashboard.py`, `kza_cli.py`, `kza_data.json` — geen wijzigingen in applicatielogica
- `test_dashboard.py` — tests blijven geldig; na installatie `webapp-testing` kunnen ze worden uitgebreid

---

## 5. Implementatiestappen (volgorde)

1. `.gitignore` uitbreiden
2. `KZA_Doelen_AI.xlsx` verwijderen via `git rm`
3. `kza-update.skill` verwijderen via `git rm`
4. Commit "Verwijder onnodige bestanden, .gitignore uitbreiden"
5. `find-skills` installeren
6. `webapp-testing` installeren
7. `grill-me` installeren
8. `pptx` installeren
9. Commit "Installeer externe skills: find-skills, webapp-testing, grill-me, pptx"
