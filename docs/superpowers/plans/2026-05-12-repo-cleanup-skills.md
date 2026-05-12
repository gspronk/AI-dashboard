# Repo Cleanup + Skills Introductie — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verwijder overbodige binaire bestanden uit de repo en installeer 4 externe skills via npx skilladd.

**Architecture:** Twee onafhankelijke stappen: (1) git rm + .gitignore uitbreiding als één commit, (2) npx skilladd voor elk van de 4 skills als tweede commit. Geen applicatielogica wijzigt.

**Tech Stack:** Git, npx (Node.js), Claude Code skills-systeem

---

## Task 1: .gitignore uitbreiden

**Files:**
- Modify: `.gitignore`

- [ ] **Stap 1: Voeg regels toe aan .gitignore**

Huidige inhoud van `.gitignore` uitbreiden met drie regels. Het bestand ziet er na aanpassing zo uit:

```
# Streamlit secrets — nooit committen
.streamlit/secrets.toml

# Test-backup
kza_data.json.testbak

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# Editor
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Binaire en Office-bestanden
*.xlsx
*.docx
*.skill
```

- [ ] **Stap 2: Verifieer de wijziging**

```bash
git diff .gitignore
```

Verwacht: drie nieuwe regels zichtbaar onder `# Binaire en Office-bestanden`

---

## Task 2: Verwijder overbodige bestanden

**Files:**
- Delete: `KZA_Doelen_AI.xlsx`
- Delete: `kza-update.skill`

- [ ] **Stap 1: Verwijder de Excel uit de repo**

```bash
git rm "KZA_Doelen_AI.xlsx"
```

Verwacht output: `rm 'KZA_Doelen_AI.xlsx'`

- [ ] **Stap 2: Verwijder het binaire skill-bestand uit de repo**

```bash
git rm "kza-update.skill"
```

Verwacht output: `rm 'kza-update.skill'`

- [ ] **Stap 3: Controleer git status**

```bash
git status
```

Verwacht: beide bestanden staan onder `Changes to be committed` als `deleted`

- [ ] **Stap 4: Commit cleanup**

```bash
git add .gitignore
git commit -m "Verwijder onnodige bestanden, .gitignore uitbreiden met xlsx/docx/skill"
```

Verwacht: commit slaagt, 3 bestanden gewijzigd (2 deleted, 1 modified)

---

## Task 3: Installeer find-skills

**Files:**
- Create: `.claude/skills/find-skills/` (aangemaakt door npx)

- [ ] **Stap 1: Installeer find-skills**

```bash
npx skilladd vercel-labs/skills/find-skills
```

Verwacht: skill wordt gedownload naar `.claude/skills/find-skills/`

- [ ] **Stap 2: Verifieer installatie**

```bash
ls .claude/skills/find-skills/
```

Verwacht: map bestaat met minimaal een `SKILL.md` of vergelijkbaar bestand

---

## Task 4: Installeer webapp-testing

**Files:**
- Create: `.claude/skills/webapp-testing/` (aangemaakt door npx)

- [ ] **Stap 1: Installeer webapp-testing**

```bash
npx skilladd anthropics/skills/webapp-testing
```

Verwacht: skill wordt gedownload naar `.claude/skills/webapp-testing/`

- [ ] **Stap 2: Verifieer installatie**

```bash
ls .claude/skills/webapp-testing/
```

Verwacht: map bestaat

---

## Task 5: Installeer grill-me

**Files:**
- Create: `.claude/skills/grill-me/` (aangemaakt door npx)

- [ ] **Stap 1: Installeer grill-me**

```bash
npx skilladd mattpocock/skills/grill-me
```

Verwacht: skill wordt gedownload naar `.claude/skills/grill-me/`

- [ ] **Stap 2: Verifieer installatie**

```bash
ls .claude/skills/grill-me/
```

Verwacht: map bestaat

---

## Task 6: Installeer pptx

**Files:**
- Create: `.claude/skills/pptx/` (aangemaakt door npx)

- [ ] **Stap 1: Installeer pptx**

```bash
npx skilladd anthropics/skills/pptx
```

Verwacht: skill wordt gedownload naar `.claude/skills/pptx/`

- [ ] **Stap 2: Verifieer installatie**

```bash
ls .claude/skills/pptx/
```

Verwacht: map bestaat

---

## Task 7: Commit geïnstalleerde skills

- [ ] **Stap 1: Controleer welke nieuwe bestanden er zijn**

```bash
git status
```

Verwacht: nieuwe mappen onder `.claude/skills/` als untracked of staged

- [ ] **Stap 2: Voeg skills toe en commit**

```bash
git add .claude/skills/
git commit -m "Installeer externe skills: find-skills, webapp-testing, grill-me, pptx"
```

Verwacht: commit slaagt met de vier nieuwe skill-mappen
