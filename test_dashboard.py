"""
KZA Dashboard - Automatische tests
Voer uit met: python test_dashboard.py
"""
import json, os, sys, ast, shutil, subprocess
import pandas as pd

DASHBOARD_FILE = os.path.join(os.path.dirname(__file__), "kza_dashboard.py")
DATA_FILE      = os.path.join(os.path.dirname(__file__), "kza_data.json")
CLI_FILE       = os.path.join(os.path.dirname(__file__), "kza_cli.py")

PASSED = []
FAILED = []

def test(naam, conditie, info=""):
    if conditie:
        PASSED.append(naam)
        print(f"  OK  {naam}")
    else:
        FAILED.append(naam)
        print(f"  FAIL  {naam}" + (f"  ->  {info}" if info else ""))

# -- 1. SYNTAX -----------------------------------------------------------------
print("\n[1] Syntax controle")
for label, path in [("dashboard", DASHBOARD_FILE), ("CLI", CLI_FILE)]:
    try:
        with open(path, encoding="utf-8") as f:
            ast.parse(f.read())
        test(f"{label}.py syntax correct", True)
    except SyntaxError as e:
        test(f"{label}.py syntax correct", False, str(e))

# -- 2. DATA BESTAND -----------------------------------------------------------
print("\n[2] kza_data.json structuur")
try:
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    test("kza_data.json leesbaar", True)
    for sleutel in ["taken", "milestones", "kpis", "prioriteiten",
                    "waarde_medewerkers", "waarde_bedrijven"]:
        test(f"sleutel '{sleutel}' aanwezig", sleutel in data)
    test("minimaal 1 taak aanwezig", len(data.get("taken", [])) >= 1)
    test("minimaal 1 milestone aanwezig", len(data.get("milestones", [])) >= 1)
    test("minimaal 1 KPI aanwezig", len(data.get("kpis", [])) >= 1)
except Exception as e:
    test("kza_data.json leesbaar", False, str(e))
    data = {}

# -- 3. TAKEN SCHEMA -----------------------------------------------------------
print("\n[3] Taak datastructuur")
verplichte_velden = ["id", "nummer", "pijler", "subtaak", "verantwoordelijke",
                     "startmaand", "deadline", "beschrijving", "status"]
STATUS_OK = {"Gepland", "Loopt", "Klaar", "Vertraagd"}

ontbrekend = [
    (t.get("nummer", "?"), v)
    for t in data.get("taken", [])
    for v in verplichte_velden
    if v not in t
]
test("alle taken hebben verplichte velden", not ontbrekend,
     f"ontbrekend: {ontbrekend}")

ongeldige = [
    (t.get("nummer", "?"), t.get("status"))
    for t in data.get("taken", [])
    if t.get("status") not in STATUS_OK
]
test("alle taken hebben geldige status", not ongeldige,
     f"ongeldig: {ongeldige}")

# -- 4. WAARDEPROPOSITIE LEGE LIJST (bugfix-test) ------------------------------
print("\n[4] Waardepropositie met lege data")
MW_COLS  = {"doel": "Doel", "waarde_mw": "Wat levert het de medewerker op?",
            "resultaat_mw": "Concreet resultaat", "pijler": "Pijler"}
BDR_COLS = {"doel": "Doel", "waarde_bdr": "Wat levert het het bedrijf op?",
            "resultaat_bdr": "Concreet resultaat", "pijler": "Pijler"}

for label, cols in [("medewerkers", MW_COLS), ("bedrijven", BDR_COLS)]:
    try:
        df = pd.DataFrame([], columns=list(cols.keys())).rename(columns=cols)
        test(f"lege '{label}' DataFrame heeft juiste kolommen",
             list(df.columns) == list(cols.values()))
    except Exception as e:
        test(f"lege '{label}' DataFrame heeft juiste kolommen", False, str(e))

for label, cols, voorbeeld in [
    ("medewerkers", MW_COLS,
     [{"doel": "AI Training", "waarde_mw": "Kennis",
       "resultaat_mw": "Sneller werken", "pijler": "P1.1"}]),
    ("bedrijven", BDR_COLS,
     [{"doel": "AI Service", "waarde_bdr": "Voordeel",
       "resultaat_bdr": "Meer omzet", "pijler": "P3.1"}]),
]:
    try:
        df = pd.DataFrame(voorbeeld,
                          columns=list(cols.keys())).rename(columns=cols)
        test(f"gevulde '{label}' DataFrame heeft juiste kolommen",
             list(df.columns) == list(cols.values()))
    except Exception as e:
        test(f"gevulde '{label}' DataFrame heeft juiste kolommen", False, str(e))

# -- 5. CLI COMMANDO'S ---------------------------------------------------------
print("\n[5] CLI commando's")

backup = DATA_FILE + ".testbak"
shutil.copy2(DATA_FILE, backup)

test_data = {
    "taken": [
        {"id": "1", "nummer": "1.1", "pijler": "PIJLER 1", "subtaak": "Test taak",
         "verantwoordelijke": "Tester", "startmaand": "Maand 1",
         "deadline": "Eind mei 2026", "beschrijving": "Test", "status": "Gepland"}
    ],
    "milestones": [
        {"id": "m1", "naam": "Test Review", "datum": "Eind mei 2026",
         "betrokkenen": "Tester", "aandachtspunten": "Check alles", "afgerond": False}
    ],
    "kpis": [
        {"id": "k1", "naam": "Test KPI", "target": ">=10", "eenheid": "%",
         "Mei": "", "Juni": "", "Juli": "", "Aug": "", "Sep": "", "Okt": ""}
    ],
    "prioriteiten": [
        {"rang": 1, "urgentie": "Nu", "actie": "Test actie", "pijler": "P1",
         "verantwoordelijke": "Tester", "deadline": "Eind mei",
         "impact": "Hoog", "reden": "Test", "status": "Gepland"}
    ],
    "waarde_medewerkers": [],
    "waarde_bedrijven": []
}

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(test_data, f, ensure_ascii=False, indent=2)

def cli(*args):
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    r = subprocess.run([sys.executable, CLI_FILE] + list(args),
                       capture_output=True, text=True, encoding="utf-8", env=env)
    return r.stdout + r.stderr

def read_data():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)

try:
    out = cli("status")
    test("'status' commando werkt", "OVERZICHT" in out, out[:60])
except Exception as e:
    test("'status' commando werkt", False, str(e))

try:
    cli("taak", "update", "1.1", "--status", "Loopt")
    taak = next((t for t in read_data()["taken"] if t["nummer"] == "1.1"), None)
    test("taak status update werkt", taak and taak["status"] == "Loopt", str(taak))
except Exception as e:
    test("taak status update werkt", False, str(e))

try:
    cli("kpi", "update", "Test KPI", "--mei", "42")
    kpi = next((k for k in read_data()["kpis"] if "Test KPI" in k["naam"]), None)
    test("kpi update werkt", kpi and str(kpi.get("Mei")) == "42", str(kpi))
except Exception as e:
    test("kpi update werkt", False, str(e))

try:
    cli("milestone", "done", "m1")
    ms = next((m for m in read_data()["milestones"] if m["id"] == "m1"), None)
    test("milestone done werkt", ms and ms["afgerond"] is True, str(ms))
except Exception as e:
    test("milestone done werkt", False, str(e))

try:
    cli("prio", "update", "1", "--status", "Klaar")
    prio = next((p for p in read_data()["prioriteiten"] if p["rang"] == 1), None)
    test("prio status update werkt", prio and prio["status"] == "Klaar", str(prio))
except Exception as e:
    test("prio status update werkt", False, str(e))

# -- 6. REFERENTIELE INTEGRITEIT EN DASHBOARD ARCHITECTUUR --------------------
print("\n[6] Referentiele integriteit en dashboardarchitectuur")

try:
    with open(DATA_FILE + ".testbak", encoding="utf-8") as f:
        prod = json.load(f)

    # Pijler-codes in prioriteiten verwijzen naar bestaande taken
    geldige_pijlers = {f"P{t['nummer']}" for t in prod.get("taken", [])}
    ongeldige_prios = [p.get("pijler") for p in prod.get("prioriteiten", [])
                       if p.get("pijler") not in geldige_pijlers]
    test("alle prioriteiten verwijzen naar bestaande pijler",
         not ongeldige_prios, f"ongeldig: {ongeldige_prios}")

    # Elke taak heeft een prioriteit-rij
    prio_codes = {p.get("pijler", "") for p in prod.get("prioriteiten", [])}
    ontbrekende_prios = [f"P{t['nummer']}" for t in prod.get("taken", [])
                         if f"P{t['nummer']}" not in prio_codes]
    test("elke taak heeft een prioriteit-rij", not ontbrekende_prios,
         f"ontbreekt: {ontbrekende_prios}")

    # Doel-waarden in waardepropositie verwijzen naar bestaande subtaken
    geldige_subtaken = {t["subtaak"] for t in prod.get("taken", [])}
    for label in ("waarde_medewerkers", "waarde_bedrijven"):
        ongeldige_doelen = [i["doel"] for i in prod.get(label, [])
                            if i.get("doel") not in geldige_subtaken]
        test(f"{label}: doelen bestaan als subtaak", not ongeldige_doelen,
             f"ongeldig: {ongeldige_doelen}")

    # Milestone structuur
    verwachte_ms_ids = {"m1", "m2", "m3", "m4", "m5", "m6"}
    ms_ids = {m.get("id") for m in prod.get("milestones", [])}
    test("productie heeft 6 milestones (m1..m6)", ms_ids == verwachte_ms_ids,
         f"gevonden: {sorted(ms_ids)}")
    ms_velden = ["id", "naam", "datum", "betrokkenen", "aandachtspunten", "afgerond"]
    ms_ontbrekend = [(m.get("id", "?"), v) for m in prod.get("milestones", [])
                     for v in ms_velden if v not in m]
    test("alle milestones hebben verplichte velden", not ms_ontbrekend,
         f"ontbrekend: {ms_ontbrekend}")

    # Strategische doelen structuur
    if "strategische_doelen" in prod:
        sd_velden = ("id", "naam", "omschrijving", "eigenaar",
                     "deadline", "status", "succescriteria")
        sd_ontbrekend = [(s.get("id", "?"), v)
                         for s in prod.get("strategische_doelen", [])
                         for v in sd_velden if v not in s]
        test("alle strategische doelen hebben verplichte velden",
             not sd_ontbrekend, f"ontbrekend: {sd_ontbrekend}")
        sd_ongeldige = [(s.get("id", "?"), s.get("status"))
                        for s in prod.get("strategische_doelen", [])
                        if s.get("status") not in STATUS_OK]
        test("alle strategische doelen hebben geldige status",
             not sd_ongeldige, f"ongeldig: {sd_ongeldige}")

    # Dashboard architectuur: kritieke helpers en patronen
    with open(DASHBOARD_FILE, encoding="utf-8") as f:
        dash_src = f.read()

    # Helper-functies
    test("dashboard heeft taak_pijler_codes helper", "def taak_pijler_codes" in dash_src)
    test("dashboard heeft taak_subtaken helper", "def taak_subtaken" in dash_src)
    test("dashboard heeft parse_nl_date helper", "def parse_nl_date" in dash_src)

    # Authenticatie
    test("dashboard heeft check_password", "def check_password" in dash_src)
    test("check_password gebruikt st.secrets", 'st.secrets.get("password"' in dash_src)
    test("dashboard stopt bij mislukte login", "st.stop()" in dash_src)

    # Persistente opslag via GitHub Gist
    test("dashboard heeft _gist_config helper", "def _gist_config" in dash_src)
    test("dashboard heeft _gist_fetch helper", "def _gist_fetch" in dash_src)
    test("dashboard heeft _gist_write helper", "def _gist_write" in dash_src)
    test("Gist-fetch is gecached met TTL", "@st.cache_data(ttl=" in dash_src)
    test("_gist_fetch retourneert status tuple",
         "'ok'," in dash_src and "'wrong_file'" in dash_src and "'empty'" in dash_src)
    test("dashboard handelt corrupte JSON in gist af", "bad_json" in dash_src)
    test("_write valt terug op lokaal bestand", "Val terug op lokaal bestand" in dash_src)
    test("Vernieuwen-knop bust Gist-cache", "_gist_fetch.clear()" in dash_src)
    test("sidebar toont actieve opslag-backend",
         "Opslag: GitHub Gist" in dash_src and "Opslag: lokaal bestand" in dash_src)

    # Databescherming
    test("gevaarlijke 'Data resetten' knop is verwijderd",
         "Data resetten" not in dash_src)
    test("load_data schrijft niet automatisch naar gist",
         "_gist_write(gist_id, token, d)" not in dash_src.split("def _write")[0])

    # Grafiek en tijdlijn
    test("dashboard importeert plotly.graph_objects",
         "import plotly.graph_objects" in dash_src)
    test("milestones gebruikt go.Scatter voor markers", "go.Scatter(" in dash_src)
    test("Gantt-tijdlijn is verwijderd",
         "Gantt tijdlijn" not in dash_src and "px.timeline(" not in dash_src)

    # UI-patronen
    test("prioriteiten heeft Pijler SelectboxColumn", "taak_pijler_codes(data" in dash_src)
    test("waardepropositie heeft Doel SelectboxColumn", "taak_subtaken(data" in dash_src)
    test("prioriteiten heeft auto-sync voor taken",
         'existing_codes = {p["pijler"] for p in data["prioriteiten"]}' in dash_src)
    test("waardepropositie ondersteunt rijen verwijderen",
         dash_src.count('num_rows="dynamic"') >= 2)
    test("waardepropositie filtert lege rijen", "rij zonder Doel overslaan" in dash_src)

    # Milestones edit-feature
    test("milestones heeft bewerk-formulier", 'st.form(f"edit_ms_' in dash_src)

    # Strategische doelen pagina
    test("dashboard heeft pagina Strategische doelen",
         'page == "\U0001f9ed Strategische doelen"' in dash_src)
    test("Strategische doelen heeft bewerk-formulier",
         'st.form(f"edit_sd_' in dash_src)
    test("Strategische doelen heeft toevoeg-formulier",
         'st.form("new_sd")' in dash_src)
    test("Strategische doelen vult ontbrekende sleutel forward-compat",
         'if "strategische_doelen" not in data' in dash_src)
    test("Strategische doelen blokkeert lege naam",
         "Vul minimaal de naam in" in dash_src)

    # Externe bestanden
    test("requirements.txt bevat requests",
         "requests" in open(os.path.join(os.path.dirname(__file__),
                                         "requirements.txt"), encoding="utf-8").read())
    test("secrets.toml.example bevat gist_id placeholder",
         "gist_id" in open(os.path.join(os.path.dirname(__file__),
                                         ".streamlit", "secrets.toml.example"),
                           encoding="utf-8").read())

except Exception as e:
    test("referentiele integriteit check", False, str(e))

# -- 7. NL-DATUM PARSER -------------------------------------------------------
print("\n[7] parse_nl_date helper")
try:
    import datetime as _dt
    with open(DASHBOARD_FILE, encoding="utf-8") as f:
        src = f.read()
    start_marker = "MAAND_NR = {"
    end_marker = "─── DATA FUNCTIONS"
    i1 = src.find(start_marker)
    i2 = src.find(end_marker, i1)
    if i1 == -1:
        raise ValueError(f"Marker '{start_marker}' niet gevonden in dashboard")
    if i2 == -1:
        for alt in ("def load_data", "# === DATA", "# ---- DATA"):
            i2 = src.find(alt, i1)
            if i2 != -1:
                break
    if i2 == -1:
        raise ValueError("Einde van parse_nl_date sectie niet gevonden in dashboard")
    snippet = src[i1:i2]
    ns = {"dt": _dt}
    exec(compile(snippet, "<parse_nl_date>", "exec"), ns)
    parse_nl_date = ns["parse_nl_date"]

    test("parse_nl_date 'Eind mei 2026' -> 31 mei",
         parse_nl_date("Eind mei 2026") == _dt.date(2026, 5, 31))
    test("parse_nl_date 'Eind juni 2026' -> 30 juni",
         parse_nl_date("Eind juni 2026") == _dt.date(2026, 6, 30))
    test("parse_nl_date 'Mei 2026' start=True -> 1 mei",
         parse_nl_date("Mei 2026", start=True) == _dt.date(2026, 5, 1))
    test("parse_nl_date 'Juni 2026' deadline -> 15 juni",
         parse_nl_date("Juni 2026") == _dt.date(2026, 6, 15))
    test("parse_nl_date leeg -> None", parse_nl_date("") is None)
    test("parse_nl_date 'Doorlopend (maandelijks)' -> None",
         parse_nl_date("Doorlopend (maandelijks)") is None)
    test("parse_nl_date 'Eind december 2026' -> 31 dec",
         parse_nl_date("Eind december 2026") == _dt.date(2026, 12, 31))
except Exception as e:
    test("parse_nl_date helper werkt", False, str(e))

# Herstel originele data
shutil.copy2(backup, DATA_FILE)
try:
    os.unlink(backup)
except Exception:
    pass

# -- RESULTAAT -----------------------------------------------------------------
print("\n" + "=" * 45)
print(f"  Resultaat: {len(PASSED)} geslaagd  |  {len(FAILED)} mislukt")
print("=" * 45)
if FAILED:
    print("\n  Mislukte tests:")
    for name in FAILED:
        print(f"    FAIL {name}")
    sys.exit(1)
else:
    print("\n  Alle tests geslaagd!")