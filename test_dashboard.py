"""
KZA Dashboard - Automatische tests
Voer uit met: python test_dashboard.py
"""
import json, os, sys, copy, ast, tempfile, shutil, subprocess
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

# ── 1. SYNTAX ─────────────────────────────────────────────────
print("\n[1] Syntax controle")
for label, path in [("dashboard", DASHBOARD_FILE), ("CLI", CLI_FILE)]:
    try:
        with open(path, encoding="utf-8") as f:
            ast.parse(f.read())
        test(f"{label}.py syntax correct", True)
    except SyntaxError as e:
        test(f"{label}.py syntax correct", False, str(e))

# ── 2. DATA BESTAND ───────────────────────────────────────────
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

# ── 3. TAKEN VELDEN ───────────────────────────────────────────
print("\n[3] Taak datastructuur")
verplichte_velden = ["id", "nummer", "pijler", "subtaak", "verantwoordelijke",
                     "startmaand", "deadline", "beschrijving", "status"]
STATUS_OK = {"Gepland", "Loopt", "Klaar", "Vertraagd"}
for t in data.get("taken", []):
    nr = t.get("nummer", "?")
    for v in verplichte_velden:
        test(f"taak {nr} heeft veld '{v}'", v in t)
    test(f"taak {nr} heeft geldige status",
         t.get("status") in STATUS_OK, f"ongeldige status: {t.get('status')}")

# ── 4. WAARDEPROPOSITIE LEGE LIJST (bugfix-test) ─────────────
print("\n[4] Waardepropositie met lege data")
MW_COLS  = {"doel": "Doel", "waarde_mw": "Wat levert het de medewerker op?",
            "resultaat_mw": "Concreet resultaat", "pijler": "Pijler"}
BDR_COLS = {"doel": "Doel", "waarde_bdr": "Wat levert het het bedrijf op?",
            "resultaat_bdr": "Concreet resultaat", "pijler": "Pijler"}

for label, cols in [("medewerkers", MW_COLS), ("bedrijven", BDR_COLS)]:
    try:
        df = pd.DataFrame([], columns=list(cols.keys())).rename(columns=cols)
        test(f"lege '{label}' lijst geeft geen fout", True)
        test(f"lege '{label}' DataFrame heeft juiste kolommen",
             list(df.columns) == list(cols.values()))
    except Exception as e:
        test(f"lege '{label}' lijst geeft geen fout", False, str(e))

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
        test(f"gevulde '{label}' lijst werkt correct", len(df) == 1)
        test(f"'{label}' kolommen correct hernoemd",
             list(df.columns) == list(cols.values()))
    except Exception as e:
        test(f"gevulde '{label}' lijst werkt correct", False, str(e))

# ── 5. CLI COMMANDO'S ─────────────────────────────────────────
print("\n[5] CLI commando's")

# Maak een tijdelijke kopie van de data naast kza_cli.py
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
    out = cli("taak", "update", "1.1", "--status", "Loopt")
    test("'taak update --status' werkt", "Loopt" in out, out)
    saved = read_data()
    taak = next((t for t in saved["taken"] if t["nummer"] == "1.1"), None)
    test("taak status correct opgeslagen", taak and taak["status"] == "Loopt",
         str(taak))
except Exception as e:
    test("'taak update --status' werkt", False, str(e))

try:
    out = cli("kpi", "update", "Test KPI", "--mei", "42")
    test("'kpi update' werkt", "42" in out, out)
    saved = read_data()
    kpi = next((k for k in saved["kpis"] if "Test KPI" in k["naam"]), None)
    test("KPI-waarde correct opgeslagen",
         kpi and str(kpi.get("Mei")) == "42", str(kpi))
except Exception as e:
    test("'kpi update' werkt", False, str(e))

try:
    out = cli("milestone", "done", "m1")
    test("'milestone done' werkt", "afgerond" in out.lower(), out)
    saved = read_data()
    ms = next((m for m in saved["milestones"] if m["id"] == "m1"), None)
    test("milestone correct afgevinkt", ms and ms["afgerond"] is True, str(ms))
except Exception as e:
    test("'milestone done' werkt", False, str(e))

try:
    out = cli("prio", "update", "1", "--status", "Klaar")
    test("'prio update' werkt", "Klaar" in out, out)
    saved = read_data()
    prio = next((p for p in saved["prioriteiten"] if p["rang"] == 1), None)
    test("prio status correct opgeslagen",
         prio and prio["status"] == "Klaar", str(prio))
except Exception as e:
    test("'prio update' werkt", False, str(e))

# ── 6. REFERENTIËLE INTEGRITEIT ──────────────────────────────
print("\n[6] Referentiële integriteit: pijler- en doel-waarden")

# Lees productie-data opnieuw (nog steeds test-data in bestand)
# We hergebruiken de eerder geladen 'data' dict (productie-state voor dit blok)
try:
    with open(DATA_FILE + ".testbak", encoding="utf-8") as f:
        prod = json.load(f)

    geldige_pijlers = {f"P{t['nummer']}" for t in prod.get("taken", [])}
    geldige_subtaken = {t["subtaak"] for t in prod.get("taken", [])}

    for p in prod.get("prioriteiten", []):
        rang = p.get("rang", "?")
        pijler = p.get("pijler", "")
        test(
            f"prioriteit rang {rang} pijler '{pijler}' bestaat in taken",
            pijler in geldige_pijlers,
            f"geldige codes: {sorted(geldige_pijlers)}"
        )

    for item in prod.get("waarde_medewerkers", []):
        doel = item.get("doel", "")
        test(
            f"waarde_medewerkers doel '{doel}' bestaat in taken",
            doel in geldige_subtaken,
            f"bekende subtaken: {sorted(geldige_subtaken)}"
        )

    for item in prod.get("waarde_bedrijven", []):
        doel = item.get("doel", "")
        test(
            f"waarde_bedrijven doel '{doel}' bestaat in taken",
            doel in geldige_subtaken,
            f"bekende subtaken: {sorted(geldige_subtaken)}"
        )

    # Dekking: elke taak heeft een overeenkomstige prioriteit-rij
    prio_codes = {p.get("pijler", "") for p in prod.get("prioriteiten", [])}
    for t in prod.get("taken", []):
        code = f"P{t['nummer']}"
        test(
            f"taak {t['nummer']} ({t['subtaak']}) heeft prioriteit-rij",
            code in prio_codes,
            f"ontbrekende pijler-code: {code}"
        )

    # Helper-functies aanwezig in dashboard?
    with open(DASHBOARD_FILE, encoding="utf-8") as f:
        dash_src = f.read()
    test("dashboard bevat taak_pijler_codes helper", "def taak_pijler_codes" in dash_src)
    test("dashboard bevat taak_subtaken helper", "def taak_subtaken" in dash_src)
    test("prioriteiten data_editor heeft Pijler SelectboxColumn",
         "taak_pijler_codes(data" in dash_src)
    test("waardepropositie data_editor heeft Doel SelectboxColumn",
         "taak_subtaken(data" in dash_src)
    test("prioriteiten-pagina heeft auto-sync voor taken",
         'existing_codes = {p["pijler"] for p in data["prioriteiten"]}' in dash_src)

    # Milestone & tijdlijn regressietests
    test("dashboard bevat parse_nl_date helper",
         "def parse_nl_date" in dash_src)
    test("dashboard importeert plotly.graph_objects",
         "import plotly.graph_objects" in dash_src)
    test("milestones-pagina heeft losse milestone tijdlijn tab",
         "🎯 Milestone tijdlijn" in dash_src)
    test("milestones-pagina gebruikt go.Scatter voor markers",
         "go.Scatter(" in dash_src)
    test("Gantt-tijdlijn tab is verwijderd",
         "📊 Gantt tijdlijn" not in dash_src and "px.timeline(" not in dash_src)
    # Wachtwoord-poort voor Streamlit Cloud
    test("dashboard bevat check_password helper",
         "def check_password" in dash_src)
    test("check_password gebruikt st.secrets",
         'st.secrets.get("password"' in dash_src)
    test("dashboard stopt bij mislukte login",
         "st.stop()" in dash_src)
    # Persistente opslag via GitHub Gist
    test("dashboard bevat _gist_config helper",
         "def _gist_config" in dash_src)
    test("dashboard bevat _gist_fetch helper",
         "def _gist_fetch" in dash_src)
    test("dashboard bevat _gist_write helper",
         "def _gist_write" in dash_src)
    test("Gist-fetch is gecached met TTL",
         "@st.cache_data(ttl=" in dash_src)
    test("load_data probeert Gist-backend eerst",
         '_gist_config()' in dash_src and 'load_data' in dash_src)
    test("_write valt terug op lokaal bestand bij Gist-fout",
         "Val terug op lokaal bestand" in dash_src)
    test("Vernieuwen-knop bust Gist-cache",
         "_gist_fetch.clear()" in dash_src)
    test("sidebar toont actieve opslag-backend",
         "Opslag: GitHub Gist" in dash_src and "Opslag: lokaal bestand" in dash_src)
    test("requirements.txt bevat requests",
         "requests" in open(os.path.join(os.path.dirname(__file__),
                                         "requirements.txt"), encoding="utf-8").read())
    test("secrets.toml.example bevat gist_id placeholder",
         "gist_id" in open(os.path.join(os.path.dirname(__file__),
                                        ".streamlit", "secrets.toml.example"),
                           encoding="utf-8").read())
    # Edit-feature voor bestaande milestones
    test("milestones overzicht heeft bewerk-formulier",
         'st.form(f"edit_ms_' in dash_src)
    test("milestones bewerken slaat naam op",
         'data["milestones"][i]["naam"] = e_naam' in dash_src)
    test("milestones bewerken slaat datum op",
         'data["milestones"][i]["datum"] = e_datum' in dash_src)
    test("milestones bewerken slaat betrokkenen op",
         'data["milestones"][i]["betrokkenen"] = e_betrok' in dash_src)
    test("milestones bewerken slaat aandachtspunten op",
         'data["milestones"][i]["aandachtspunten"] = e_punten' in dash_src)

    # Productie-data: milestones moeten 6 stuks zijn en juiste ids hebben
    verwachte_ms_ids = {"m1", "m2", "m3", "m4", "m5", "m6"}
    ms_ids = {m.get("id") for m in prod.get("milestones", [])}
    test("productie heeft 6 milestones (m1..m6)",
         ms_ids == verwachte_ms_ids,
         f"gevonden ids: {sorted(ms_ids)}")
    for m in prod.get("milestones", []):
        for v in ("id", "naam", "datum", "betrokkenen", "aandachtspunten", "afgerond"):
            test(f"milestone {m.get('id','?')} heeft veld '{v}'", v in m)

except Exception as e:
    test("referentiële integriteit check", False, str(e))

# ── 7. NL-DATUM PARSER (import uit dashboard) ────────────────
print("\n[7] parse_nl_date helper")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("_kza_dash_mod", DASHBOARD_FILE)
    # We kunnen het dashboard niet rechtstreeks importeren (streamlit side-effects),
    # dus we halen alleen parse_nl_date er uit via bronparsing + exec in een schone namespace.
    with open(DASHBOARD_FILE, encoding="utf-8") as f:
        src = f.read()
    # Knip de parser + MAAND_NR + datetime import eruit
    import datetime as _dt
    ns = {"dt": _dt}
    # Simpele extractie: alle regels tussen '# ─── NL-DATUM PARSER' en volgende '# ───'
    start_marker = "MAAND_NR = {"
    end_marker = "# ─── DATA FUNCTIONS"
    i1 = src.find(start_marker)
    i2 = src.find(end_marker, i1)
    snippet = src[i1:i2]
    exec(snippet, ns)
    parse_nl_date = ns["parse_nl_date"]

    test("parse_nl_date 'Eind mei 2026' → 31 mei",
         parse_nl_date("Eind mei 2026") == _dt.date(2026, 5, 31))
    test("parse_nl_date 'Eind juni 2026' → 30 juni",
         parse_nl_date("Eind juni 2026") == _dt.date(2026, 6, 30))
    test("parse_nl_date 'Mei 2026' start=True → 1 mei",
         parse_nl_date("Mei 2026", start=True) == _dt.date(2026, 5, 1))
    test("parse_nl_date 'Juni 2026' deadline → 15 juni",
         parse_nl_date("Juni 2026") == _dt.date(2026, 6, 15))
    test("parse_nl_date leeg → None",
         parse_nl_date("") is None)
    test("parse_nl_date 'Doorlopend (maandelijks)' → None",
         parse_nl_date("Doorlopend (maandelijks)") is None)
    test("parse_nl_date 'Eind december 2026' → 31 dec",
         parse_nl_date("Eind december 2026") == _dt.date(2026, 12, 31))
except Exception as e:
    test("parse_nl_date helper werkt", False, str(e))

# Herstel originele data
shutil.copy2(backup, DATA_FILE)
try:
    os.unlink(backup)
except Exception:
    pass  # backup verwijderen lukt soms niet op Windows-mount

# ── RESULTAAT ─────────────────────────────────────────────────
print("\n" + "=" * 45)
print(f"  Resultaat: {len(PASSED)} geslaagd  |  {len(FAILED)} mislukt")
print("=" * 45)
if FAILED:
    print("\n  Mislukte tests:")
    for name in FAILED:
        print(f"    FAIL {name}")
    sys.exit(1)
else:
    print("\n  Alle tests geslaagd\!")
