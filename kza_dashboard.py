#!/usr/bin/env python3
"""
KZA Doelen AI – Lokaal Dashboard
Start met: streamlit run kza_dashboard.py
"""

import streamlit as st
import pandas as pd
import json, os, copy, uuid, time, datetime as dt
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="KZA Doelen AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main .block-container { padding-top: 1.5rem; max-width: 1400px; }
section[data-testid="stSidebar"] { background: #1F4E79; }
section[data-testid="stSidebar"] * { color: white !important; }
section[data-testid="stSidebar"] .stRadio label { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ─── WACHTWOORD-POORT ─────────────────────────────────────────
# Configureer een wachtwoord op Streamlit Cloud via Settings → Secrets:
#   password = "jouw-geheime-wachtwoord"
# Lokaal kun je hetzelfde doen in .streamlit/secrets.toml.
# Wanneer er geen 'password' in st.secrets staat, draait het dashboard
# zonder poort (handig voor lokale ontwikkeling).
def check_password():
    """Return True als gebruiker geauthenticeerd is, anders toon login en False."""
    try:
        expected = st.secrets.get("password", None)
    except (FileNotFoundError, KeyError, Exception):
        expected = None
    if not expected:
        return True  # Geen secret geconfigureerd → dev-modus, vrije toegang
    if st.session_state.get("authenticated"):
        return True
    st.title("🔒 KZA Doelen AI")
    st.caption("Voer het wachtwoord in om verder te gaan.")
    pw = st.text_input("Wachtwoord", type="password", key="pw_input")
    if st.button("Inloggen", type="primary"):
        if pw == expected:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ Onjuist wachtwoord")
    return False

if not check_password():
    st.stop()

# ─── DATA FILE ────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kza_data.json")

INITIAL_DATA = {
    "taken": [
        {"id":"1","nummer":"1.1","pijler":"PIJLER 1 – VERSPREIDING","subtaak":"Organisatiewijde AI Awareness","verantwoordelijke":"KZAcademy lead","startmaand":"Maand 1","deadline":"Eind mei 2026","beschrijving":"Rollout basistraining voor alle niveaus","status":"Gepland"},
        {"id":"2","nummer":"1.2","pijler":"PIJLER 1 – VERSPREIDING","subtaak":"AI Tool Ecosystem","verantwoordelijke":"Jij","startmaand":"Maand 2","deadline":"Eind juni 2026","beschrijving":"Kurateren van 10+ AI-tools, documentatie","status":"Gepland"},
        {"id":"3","nummer":"1.3","pijler":"PIJLER 1 – VERSPREIDING","subtaak":"Pilot-projecten alle teams","verantwoordelijke":"Jij + team leads","startmaand":"Maand 3","deadline":"Eind juli 2026","beschrijving":"≥3 pilotprojecten starten","status":"Gepland"},
        {"id":"4","nummer":"1.4","pijler":"PIJLER 1 – VERSPREIDING","subtaak":"Interne Communicatie","verantwoordelijke":"Jij","startmaand":"Maand 2","deadline":"Eind september 2026","beschrijving":"Maandelijkse AI-updates, success stories","status":"Gepland"},
        {"id":"5","nummer":"2.1","pijler":"PIJLER 2 – KENNISVERHOGING","subtaak":"AI Fundamentals Track","verantwoordelijke":"KZAcademy","startmaand":"Maand 1","deadline":"Eind maart 2027","beschrijving":"Basistrack AI-fundamenten voor alle medewerkers","status":"Gepland"},
        {"id":"6","nummer":"2.2","pijler":"PIJLER 2 – KENNISVERHOGING","subtaak":"AI-Specialisatie Tracks","verantwoordelijke":"Domain experts per track","startmaand":"Maand 2","deadline":"Eind augustus 2026","beschrijving":"Gespecialiseerde tracks per domein","status":"Gepland"},
        {"id":"7","nummer":"2.3","pijler":"PIJLER 2 – KENNISVERHOGING","subtaak":"Internal AI Champions Network","verantwoordelijke":"Jij","startmaand":"Maand 3","deadline":"Eind september 2026","beschrijving":"Opbouwen intern netwerk van AI-ambassadeurs","status":"Gepland"},
        {"id":"8","nummer":"2.4","pijler":"PIJLER 2 – KENNISVERHOGING","subtaak":"External Knowledge Integration","verantwoordelijke":"Jij","startmaand":"Maand 4","deadline":"Eind oktober 2026","beschrijving":"Externe kennisbronnen integreren in leertrajecten","status":"Gepland"},
        {"id":"9","nummer":"3.1","pijler":"PIJLER 3 – NIEUWE INITIATIEVEN","subtaak":"AI-Enhanced Service Offerings","verantwoordelijke":"Jij + Sales","startmaand":"Maand 2","deadline":"Eind augustus 2026","beschrijving":"Ontwikkelen van AI-verrijkte dienstverlening","status":"Gepland"},
        {"id":"10","nummer":"3.2","pijler":"PIJLER 3 – NIEUWE INITIATIEVEN","subtaak":"AI Automation Internal Processes","verantwoordelijke":"Cross-functional team","startmaand":"Maand 3","deadline":"Eind augustus 2026","beschrijving":"Automatiseren van interne processen met AI","status":"Gepland"},
        {"id":"11","nummer":"3.3","pijler":"PIJLER 3 – NIEUWE INITIATIEVEN","subtaak":"Responsible AI Governance","verantwoordelijke":"Jij","startmaand":"Maand 2","deadline":"Eind juli 2026","beschrijving":"Opstellen AI-beleid, ethiek en governance kader","status":"Gepland"},
        {"id":"12","nummer":"3.4","pijler":"PIJLER 3 – NIEUWE INITIATIEVEN","subtaak":"Innovation Lab","verantwoordelijke":"Jij","startmaand":"Maand 3","deadline":"Eind oktober 2026","beschrijving":"Opzetten intern AI-innovatielab voor experimenten","status":"Gepland"},
    ],
    "milestones": [
        {"id":"m1","naam":"Maand 1 Review","datum":"Eind mei 2026","betrokkenen":"Alle pijlerleads","aandachtspunten":"Pijler 1.1 gestart? Basistraining uitgerold?","afgerond":False},
        {"id":"m2","naam":"Maand 2–3 Review","datum":"Eind juni 2026","betrokkenen":"Alle pijlerleads","aandachtspunten":"AI-tools gekureerd? Pilotprojecten gedefinieerd?","afgerond":False},
        {"id":"m3","naam":"Maand 3–4 Review","datum":"Eind juli 2026","betrokkenen":"Jij + team leads","aandachtspunten":"≥3 pilots gestart? Governance kader gereed?","afgerond":False},
        {"id":"m4","naam":"Maand 4–5 Review","datum":"Eind augustus 2026","betrokkenen":"Alle pijlerleads","aandachtspunten":"Specialisatietracks actief? Automatisering geïmplementeerd?","afgerond":False},
        {"id":"m5","naam":"Maand 5–6 Review","datum":"Eind september 2026","betrokkenen":"Alle pijlerleads","aandachtspunten":"Champions netwerk actief? KPI's op target?","afgerond":False},
    ],
    "kpis": [
        {"id":"k1","naam":"% Organisatie AI-actief","target":"≥ 80%","eenheid":"%","Mei":"","Juni":"","Juli":"","Aug":"","Sep":"","Okt":""},
        {"id":"k2","naam":"Actieve AI-tool users","target":"≥ 50","eenheid":"#","Mei":"","Juni":"","Juli":"","Aug":"","Sep":"","Okt":""},
        {"id":"k3","naam":"Training completion rate","target":"≥ 90%","eenheid":"%","Mei":"","Juni":"","Juli":"","Aug":"","Sep":"","Okt":""},
        {"id":"k4","naam":"Aantal pilotprojecten gestart","target":"≥ 3","eenheid":"#","Mei":"","Juni":"","Juli":"","Aug":"","Sep":"","Okt":""},
        {"id":"k5","naam":"AI Champions aangesteld","target":"≥ 5","eenheid":"#","Mei":"","Juni":"","Juli":"","Aug":"","Sep":"","Okt":""},
        {"id":"k6","naam":"Nieuwe AI-diensten gelanceerd","target":"≥ 2","eenheid":"#","Mei":"","Juni":"","Juli":"","Aug":"","Sep":"","Okt":""},
        {"id":"k7","naam":"Interne processen geautomatiseerd","target":"≥ 3","eenheid":"#","Mei":"","Juni":"","Juli":"","Aug":"","Sep":"","Okt":""},
        {"id":"k8","naam":"Maandelijkse AI-updates verstuurd","target":"6 van 6","eenheid":"#","Mei":"","Juni":"","Juli":"","Aug":"","Sep":"","Okt":""},
    ],
    "prioriteiten": [
        {"rang":1,"urgentie":"🔴 Nu","actie":"Start AI Awareness basistraining","pijler":"P1.1","verantwoordelijke":"KZAcademy lead","deadline":"Eind mei 2026","impact":"⭐⭐⭐⭐⭐","reden":"Fundament voor alles — zonder bewustzijn geen adoptie","status":"Gepland"},
        {"rang":2,"urgentie":"🔴 Nu","actie":"Stel AI Governance kader op","pijler":"P3.3","verantwoordelijke":"Jij","deadline":"Eind juli 2026","impact":"⭐⭐⭐⭐⭐","reden":"Noodzakelijk voor veilig gebruik & vertrouwen klanten","status":"Gepland"},
        {"rang":3,"urgentie":"🔴 Nu","actie":"Kureer & documenteer 10+ AI-tools","pijler":"P1.2","verantwoordelijke":"Jij","deadline":"Eind juni 2026","impact":"⭐⭐⭐⭐","reden":"Geeft medewerkers direct werkbare instrumenten","status":"Gepland"},
        {"rang":4,"urgentie":"🔴 Nu","actie":"Launch AI-Enhanced Service propositie","pijler":"P3.1","verantwoordelijke":"Jij + Sales","deadline":"Eind augustus 2026","impact":"⭐⭐⭐⭐⭐","reden":"Directe commerciële waarde voor KZA als bedrijf","status":"Gepland"},
        {"rang":5,"urgentie":"🟡 Q3","actie":"Start ≥3 pilotprojecten per team","pijler":"P1.3","verantwoordelijke":"Jij + team leads","deadline":"Eind juli 2026","impact":"⭐⭐⭐⭐","reden":"Praktijkbewijs, draagvlak & leercases voor marketing","status":"Gepland"},
        {"rang":6,"urgentie":"🟡 Q3","actie":"Lanceer AI Fundamentals Track","pijler":"P2.1","verantwoordelijke":"KZAcademy","deadline":"Eind maart 2027","impact":"⭐⭐⭐⭐","reden":"Structurele kennisopbouw voor alle medewerkers","status":"Gepland"},
        {"rang":7,"urgentie":"🟡 Q3","actie":"Start maandelijkse AI-communicatie","pijler":"P1.4","verantwoordelijke":"Jij","deadline":"Eind mei 2026","impact":"⭐⭐⭐","reden":"Zichtbaarheid & momentum vasthouden","status":"Gepland"},
        {"rang":8,"urgentie":"🟡 Q3","actie":"Selecteer & benoem AI Champions","pijler":"P2.3","verantwoordelijke":"Jij","deadline":"Eind september 2026","impact":"⭐⭐⭐⭐","reden":"Interne verspreiding van kennis schaalt sneller","status":"Gepland"},
        {"rang":9,"urgentie":"🟢 Q4","actie":"Start AI-Specialisatie Tracks","pijler":"P2.2","verantwoordelijke":"Domain experts","deadline":"Eind augustus 2026","impact":"⭐⭐⭐","reden":"Verdieping na brede basislaag","status":"Gepland"},
        {"rang":10,"urgentie":"🟢 Q4","actie":"Identificeer automatiseringsprojecten","pijler":"P3.2","verantwoordelijke":"Cross-func. team","deadline":"Eind augustus 2026","impact":"⭐⭐⭐⭐","reden":"Kostenbesparing & efficiëntie intern","status":"Gepland"},
        {"rang":11,"urgentie":"🟢 Q4","actie":"Integreer externe kennisbronnen","pijler":"P2.4","verantwoordelijke":"Jij","deadline":"Eind oktober 2026","impact":"⭐⭐⭐","reden":"Thought leadership & future-proofing","status":"Gepland"},
        {"rang":12,"urgentie":"🟢 Q4","actie":"Richt Innovation Lab in","pijler":"P3.4","verantwoordelijke":"Jij","deadline":"Eind oktober 2026","impact":"⭐⭐⭐","reden":"Lange termijn innovatiecultuur & klantenwaarde","status":"Gepland"},
    ],
    "waarde_medewerkers": [
        {"doel":"Organisatiewijde AI Awareness","waarde_mw":"Basiskennis AI, zelfvertrouwen met tools","resultaat_mw":"Medewerkers werken sneller & slimmer","pijler":"P1.1"},
        {"doel":"AI Tool Ecosystem","waarde_mw":"Toegang tot bewezen, veilige AI-tools","resultaat_mw":"Tijdsbesparing in dagelijkse taken","pijler":"P1.2"},
        {"doel":"AI Fundamentals Track","waarde_mw":"Persoonlijke groei, up-to-date vakkennis","resultaat_mw":"Hoger competentieniveau, meer werkplezier","pijler":"P2.1"},
        {"doel":"AI-Specialisatie Tracks","waarde_mw":"Diepere expertise per vakgebied","resultaat_mw":"Doorgroeikansen, specialisatie","pijler":"P2.2"},
        {"doel":"Internal AI Champions Network","waarde_mw":"Leiderschapsrol, kennisdeling met collega's","resultaat_mw":"Interne ambassadeurs, minder kenniskloof","pijler":"P2.3"},
        {"doel":"Pilot-projecten alle teams","waarde_mw":"Hands-on ervaring met AI in eigen werk","resultaat_mw":"Praktische vaardigheden, innovatiecultuur","pijler":"P1.3"},
        {"doel":"Innovation Lab","waarde_mw":"Ruimte om te experimenteren en innoveren","resultaat_mw":"Creativiteit, eigenaarschap, motivatie","pijler":"P3.4"},
        {"doel":"Interne Communicatie","waarde_mw":"Zichtbaarheid van AI-successen","resultaat_mw":"Inspiratie, betrokkenheid, gedeelde trots","pijler":"P1.4"},
    ],
    "waarde_bedrijven": [
        {"doel":"AI-Enhanced Service Offerings","waarde_bdr":"Innovatievere, snellere dienstverlening","resultaat_bdr":"Hogere klanttevredenheid & concurrentievoordeel","pijler":"P3.1"},
        {"doel":"AI Automation Internal Processes","waarde_bdr":"Lagere operationele kosten, minder fouten","resultaat_bdr":"Efficiëntere processen, snellere levering","pijler":"P3.2"},
        {"doel":"Responsible AI Governance","waarde_bdr":"Vertrouwen, compliance en transparantie","resultaat_bdr":"Minder risico, sterkere reputatie bij klanten","pijler":"P3.3"},
        {"doel":"External Knowledge Integration","waarde_bdr":"Toegang tot nieuwste AI-inzichten","resultaat_bdr":"Toekomstbestendige propositie, thought leadership","pijler":"P2.4"},
        {"doel":"Pilot-projecten alle teams","waarde_bdr":"Bewijs van innovatievermogen KZA","resultaat_bdr":"Concrete cases voor marketing & sales","pijler":"P1.3"},
        {"doel":"Innovation Lab","waarde_bdr":"Co-innovatie mogelijkheden met klanten","resultaat_bdr":"Nieuwe businessmodellen, partnership kansen","pijler":"P3.4"},
    ]
}

STATUS_OPTIONS = ["Gepland", "Loopt", "Klaar", "Vertraagd"]
MONTHS = ["Mei", "Juni", "Juli", "Aug", "Sep", "Okt"]

def taak_pijler_codes(taken):
    return [f"P{t['nummer']}" for t in taken]

def taak_subtaken(taken):
    return [t["subtaak"] for t in taken]

# ─── NL-DATUM PARSER ─────────────────────────────────────────
MAAND_NR = {
    "januari": 1, "jan": 1,
    "februari": 2, "feb": 2,
    "maart": 3, "mrt": 3,
    "april": 4, "apr": 4,
    "mei": 5,
    "juni": 6, "jun": 6,
    "juli": 7, "jul": 7,
    "augustus": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "oktober": 10, "okt": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}

def parse_nl_date(s, default_year=2026, start=False):
    """Parse NL-datumstring als 'Eind mei 2026' / 'Juni 2026' / 'Mei 2026'.
    - 'eind/einde' → laatste dag van de maand
    - anders → eerste dag van de maand (voor start) of midden (voor deadline zonder 'eind')
    Retourneert datetime.date of None bij onparseerbaar."""
    if not s:
        return None
    raw = s.strip().lower()
    einde = raw.startswith("eind") or raw.startswith("einde")
    # Jaar vinden
    year = default_year
    parts = raw.replace(",", " ").replace(".", " ").split()
    for p in parts:
        if p.isdigit() and len(p) == 4:
            year = int(p)
    # Maand vinden
    month = None
    for w in parts:
        if w in MAAND_NR:
            month = MAAND_NR[w]
            break
    if month is None:
        return None
    if einde:
        if month == 12:
            return dt.date(year, 12, 31)
        return dt.date(year, month + 1, 1) - dt.timedelta(days=1)
    if start:
        return dt.date(year, month, 1)
    # deadline zonder 'eind' → midden van de maand (15e)
    return dt.date(year, month, 15)

# ─── DATA FUNCTIONS ───────────────────────────────────────────
# Persistente opslag werkt via één van twee backends:
#   1. GitHub Gist  — als 'gist_id' én 'github_token' in st.secrets staan
#   2. Lokaal bestand kza_data.json — als die secrets ontbreken
# Zie .streamlit/secrets.toml.example voor setup-instructies.
GIST_FILENAME = "kza_data.json"
GIST_API = "https://api.github.com/gists"

def _gist_config():
    """Return (gist_id, token) als beide secrets gezet zijn, anders (None, None)."""
    try:
        gid = st.secrets.get("gist_id", None)
        tok = st.secrets.get("github_token", None)
    except Exception:
        return None, None
    if gid and tok:
        return gid, tok
    return None, None

@st.cache_data(ttl=30, show_spinner=False)
def _gist_fetch(gist_id, token):
    """Haal de JSON op uit de gist (gecached, 30s TTL)."""
    import requests
    headers = {"Authorization": f"Bearer {token}",
               "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28"}
    r = requests.get(f"{GIST_API}/{gist_id}", headers=headers, timeout=10)
    r.raise_for_status()
    files = r.json().get("files", {})
    if GIST_FILENAME not in files:
        return None
    return json.loads(files[GIST_FILENAME]["content"])

def _gist_write(gist_id, token, data):
    """Schrijf de JSON terug naar de gist."""
    import requests
    headers = {"Authorization": f"Bearer {token}",
               "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28"}
    body = {"files": {GIST_FILENAME: {
        "content": json.dumps(data, ensure_ascii=False, indent=2)
    }}}
    r = requests.patch(f"{GIST_API}/{gist_id}", headers=headers,
                       json=body, timeout=15)
    r.raise_for_status()

def load_data():
    gist_id, token = _gist_config()
    if gist_id and token:
        try:
            d = _gist_fetch(gist_id, token)
            if d is None:
                # Gist bestaat maar bevat kza_data.json nog niet → seed
                d = copy.deepcopy(INITIAL_DATA)
                _gist_write(gist_id, token, d)
                _gist_fetch.clear()
            for key in INITIAL_DATA:
                if key not in d:
                    d[key] = copy.deepcopy(INITIAL_DATA[key])
            return d
        except Exception as e:
            st.error(f"⚠️ Gist-opslag onbereikbaar ({e}). Val terug op lokaal bestand.")
    # Lokale fallback
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            d = json.load(f)
        for key in INITIAL_DATA:
            if key not in d:
                d[key] = copy.deepcopy(INITIAL_DATA[key])
        return d
    data = copy.deepcopy(INITIAL_DATA)
    _write(data)
    return data

def _write(data):
    gist_id, token = _gist_config()
    if gist_id and token:
        try:
            _gist_write(gist_id, token, data)
            _gist_fetch.clear()  # cache busten zodat volgende load vers leest
            return
        except Exception as e:
            st.error(f"⚠️ Gist-write faalt ({e}). Val terug op lokaal bestand.")
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save(data, msg="✅ Opgeslagen!"):
    _write(data)
    st.session_state["saved_msg"] = msg

# ─── SIDEBAR ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 KZA Doelen AI")
    st.caption("AI-strategie tracker 2026")
    st.divider()
    page = st.radio(
        "Navigatie",
        ["🏠 Dashboard", "📋 Taken", "🎯 Milestones", "📈 KPI's", "🏆 Prioriteiten", "💡 Waardepropositie"],
        label_visibility="hidden"
    )
    st.divider()
    if st.button("🔄 Vernieuwen", use_container_width=True, type="primary"):
        _gist_fetch.clear()  # forceer verse data uit Gist
        st.rerun()
    auto_refresh = st.toggle("⚡ Auto-refresh (10 sec)", value=False)
    st.divider()
    # Backend-indicator
    _gid, _tok = _gist_config()
    if _gid and _tok:
        st.caption("☁️ Opslag: GitHub Gist")
    else:
        st.caption("💾 Opslag: lokaal bestand")
    if st.button("↺ Data resetten naar standaard", use_container_width=True):
        _write(copy.deepcopy(INITIAL_DATA))
        st.session_state.pop("confirm_reset", None)
        st.rerun()

data = load_data()

if "saved_msg" in st.session_state:
    st.success(st.session_state.pop("saved_msg"))

# Auto-refresh
if auto_refresh:
    with st.sidebar:
        st.caption("Volgende refresh over 10 sec...")
    time.sleep(10)
    st.rerun()

# ═══════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.title("🤖 KZA Doelen AI – Dashboard")
    st.caption("Overzicht AI-strategie voortgang · 2026")

    taken = data["taken"]
    milestones = data["milestones"]
    status_counts = {s: sum(1 for t in taken if t["status"] == s) for s in STATUS_OPTIONS}
    ms_klaar = sum(1 for m in milestones if m["afgerond"])
    pct_klaar = round(status_counts["Klaar"] / len(taken) * 100) if taken else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("📋 Taken totaal", len(taken))
    c2.metric("🔵 Gepland", status_counts["Gepland"])
    c3.metric("🟡 Loopt", status_counts["Loopt"])
    c4.metric("🟢 Klaar", status_counts["Klaar"])
    c5.metric("🔴 Vertraagd", status_counts["Vertraagd"])
    c6.metric("🎯 Milestones", f"{ms_klaar}/{len(milestones)}")

    st.progress(pct_klaar / 100, text=f"Totale voortgang: {pct_klaar}% afgerond")
    st.divider()

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("📊 Voortgang per Pijler")
        rows = []
        for t in taken:
            label = t["pijler"].replace("PIJLER 1 – VERSPREIDING", "P1 – Verspreiding") \
                               .replace("PIJLER 2 – KENNISVERHOGING", "P2 – Kennis") \
                               .replace("PIJLER 3 – NIEUWE INITIATIEVEN", "P3 – Initiatieven")
            rows.append({"Pijler": label, "Status": t["status"]})
        df = pd.DataFrame(rows)
        counts = df.groupby(["Pijler", "Status"]).size().reset_index(name="Aantal")
        fig = px.bar(
            counts, x="Pijler", y="Aantal", color="Status",
            color_discrete_map={"Gepland": "#93C6E7", "Loopt": "#FFD966", "Klaar": "#70AD47", "Vertraagd": "#FF4444"},
            text="Aantal", barmode="stack"
        )
        fig.update_layout(height=340, margin=dict(t=10, b=10), plot_bgcolor="white",
                         paper_bgcolor="white", legend_title="Status")
        fig.update_traces(textposition="inside")
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("🎯 Milestones")
        for m in milestones:
            icon = "✅" if m["afgerond"] else "⏳"
            st.markdown(f"{icon} **{m['naam']}**  \n&nbsp;&nbsp;&nbsp;📅 _{m['datum']}_")

        st.divider()
        pie_df = pd.DataFrame(
            [(s, c) for s, c in status_counts.items() if c > 0],
            columns=["Status", "Aantal"]
        )
        if not pie_df.empty:
            fig2 = px.pie(pie_df, values="Aantal", names="Status", hole=0.45,
                         color="Status",
                         color_discrete_map={"Gepland": "#93C6E7", "Loopt": "#FFD966",
                                             "Klaar": "#70AD47", "Vertraagd": "#FF4444"})
            fig2.update_layout(height=220, margin=dict(t=10, b=5, l=5, r=5))
            st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("🔴 Openstaande taken")
    open_taken = [t for t in taken if t["status"] != "Klaar"]
    if open_taken:
        df_open = pd.DataFrame(open_taken)[["nummer", "subtaak", "verantwoordelijke", "deadline", "status"]]
        df_open.columns = ["#", "Subtaak", "Verantwoordelijke", "Deadline", "Status"]
        st.dataframe(df_open, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════
# PAGE: TAKEN
# ═══════════════════════════════════════════════════════════════
elif page == "📋 Taken":
    st.title("📋 Taken Beheren")
    tab1, tab2 = st.tabs(["📄 Overzicht & bewerken", "➕ Nieuwe taak"])

    with tab1:
        col1, col2 = st.columns(2)
        pijlers = ["Alle"] + list(dict.fromkeys(t["pijler"] for t in data["taken"]))
        with col1:
            pf = st.selectbox("Filter pijler", pijlers)
        with col2:
            sf = st.selectbox("Filter status", ["Alle"] + STATUS_OPTIONS)

        filtered = [t for t in data["taken"]
                    if (pf == "Alle" or t["pijler"] == pf)
                    and (sf == "Alle" or t["status"] == sf)]

        if not filtered:
            st.info("Geen taken gevonden met deze filters.")
        else:
            st.caption(f"{len(filtered)} taken")
            display_cols = ["nummer", "pijler", "subtaak", "verantwoordelijke", "startmaand", "deadline", "beschrijving", "status"]
            df = pd.DataFrame(filtered)[display_cols].copy()
            df.columns = ["#", "Pijler", "Subtaak", "Verantwoordelijke", "Start", "Deadline", "Beschrijving", "Status"]

            edited = st.data_editor(
                df,
                column_config={
                    "Status": st.column_config.SelectboxColumn(options=STATUS_OPTIONS, required=True, width="small"),
                    "Pijler": st.column_config.TextColumn(width="medium"),
                    "Subtaak": st.column_config.TextColumn(width="large"),
                    "Beschrijving": st.column_config.TextColumn(width="large"),
                    "#": st.column_config.TextColumn(width="small"),
                },
                use_container_width=True,
                hide_index=True,
                key="taken_editor"
            )

            if st.button("💾 Wijzigingen opslaan", type="primary", key="save_taken"):
                filtered_ids = [t["id"] for t in filtered]
                for i, tid in enumerate(filtered_ids):
                    for t in data["taken"]:
                        if t["id"] == tid:
                            row = edited.iloc[i]
                            t["nummer"] = row["#"]
                            t["pijler"] = row["Pijler"]
                            t["subtaak"] = row["Subtaak"]
                            t["verantwoordelijke"] = row["Verantwoordelijke"]
                            t["startmaand"] = row["Start"]
                            t["deadline"] = row["Deadline"]
                            t["beschrijving"] = row["Beschrijving"]
                            t["status"] = row["Status"]
                            break
                save(data)
                st.rerun()

    with tab2:
        with st.form("new_task"):
            st.subheader("Nieuwe taak toevoegen")
            c1, c2 = st.columns(2)
            with c1:
                nn = st.text_input("Nummer (bv. 1.5)")
                np_ = st.selectbox("Pijler", list(dict.fromkeys(t["pijler"] for t in data["taken"])))
                ns = st.text_input("Subtaak naam *")
                nv = st.text_input("Verantwoordelijke")
            with c2:
                nm = st.text_input("Startmaand (bv. Maand 3)")
                nd = st.text_input("Deadline (bv. Eind juni 2026)")
                nstat = st.selectbox("Status", STATUS_OPTIONS)
                nb = st.text_area("Beschrijving", height=80)
            if st.form_submit_button("➕ Taak toevoegen", type="primary"):
                if ns:
                    new_id = str(max((int(t["id"]) for t in data["taken"]), default=0) + 1)
                    data["taken"].append({
                        "id": new_id, "nummer": nn, "pijler": np_, "subtaak": ns,
                        "verantwoordelijke": nv, "startmaand": nm, "deadline": nd,
                        "beschrijving": nb, "status": nstat
                    })
                    save(data)
                    st.rerun()
                else:
                    st.error("Vul minimaal de naam van de subtaak in.")

# ═══════════════════════════════════════════════════════════════
# PAGE: MILESTONES
# ═══════════════════════════════════════════════════════════════
elif page == "🎯 Milestones":
    st.title("🎯 Milestones & Reviews")
    tab1, tab_mstl, tab2 = st.tabs(
        ["📄 Overzicht & bewerken", "🎯 Milestone tijdlijn", "➕ Nieuw milestone"]
    )

    with tab1:
        st.caption("Klik op een milestone om deze te bewerken. Het vinkje zet 'afgerond' direct aan/uit.")
        changed = False
        for i, m in enumerate(data["milestones"]):
            # Kop-regel: checkbox + samenvatting + verwijder-knop
            c1, c2, c3 = st.columns([0.5, 5, 0.7])
            with c1:
                checked = st.checkbox(
                    "afgerond", value=m["afgerond"], key=f"ms_{m['id']}",
                    label_visibility="collapsed"
                )
                if checked != m["afgerond"]:
                    data["milestones"][i]["afgerond"] = checked
                    changed = True
            with c2:
                icon = "✅" if m["afgerond"] else "⏳"
                with st.expander(
                    f"{icon} **{m['naam']}**  —  📅 {m['datum']}  —  👥 {m['betrokkenen']}",
                    expanded=False
                ):
                    with st.form(f"edit_ms_{m['id']}"):
                        e_naam = st.text_input("Naam", value=m["naam"], key=f"en_{m['id']}")
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            e_datum = st.text_input("Datum", value=m["datum"], key=f"ed_{m['id']}")
                        with ec2:
                            e_betrok = st.text_input("Betrokkenen", value=m["betrokkenen"], key=f"eb_{m['id']}")
                        e_punten = st.text_area(
                            "Aandachtspunten", value=m["aandachtspunten"],
                            height=100, key=f"ep_{m['id']}"
                        )
                        if st.form_submit_button("💾 Opslaan", type="primary"):
                            data["milestones"][i]["naam"] = e_naam
                            data["milestones"][i]["datum"] = e_datum
                            data["milestones"][i]["betrokkenen"] = e_betrok
                            data["milestones"][i]["aandachtspunten"] = e_punten
                            save(data, msg=f"✅ Milestone '{e_naam}' opgeslagen")
                            st.rerun()
            with c3:
                if st.button("🗑️", key=f"del_{m['id']}", help="Verwijderen"):
                    data["milestones"].pop(i)
                    save(data)
                    st.rerun()
            st.divider()

        if changed:
            _write(data)
            st.rerun()

    # ─── LOSSE MILESTONE-TIJDLIJN ─────────────────────────────────────
    with tab_mstl:
        st.subheader("🎯 Milestone-tijdlijn")
        st.caption("Alleen de milestones op een tijdas — ideaal voor reviews en planning.")

        ms_rows = []
        for m in data["milestones"]:
            d = parse_nl_date(m.get("datum", ""))
            if d is None:
                continue
            ms_rows.append({
                "id": m["id"],
                "Naam": m["naam"],
                "Datum": d,
                "Betrokkenen": m.get("betrokkenen", ""),
                "Aandachtspunten": m.get("aandachtspunten", ""),
                "Status": "✅ Afgerond" if m["afgerond"] else "⏳ Open",
            })

        if not ms_rows:
            st.info("Nog geen milestones met parseerbare datum.")
        else:
            df_m = pd.DataFrame(ms_rows).sort_values("Datum")
            fig_m = go.Figure()
            # Horizontale basislijn
            fig_m.add_shape(type="line",
                            x0=df_m["Datum"].min() - dt.timedelta(days=15),
                            x1=df_m["Datum"].max() + dt.timedelta(days=15),
                            y0=0, y1=0,
                            line=dict(color="#9ca3af", width=2))
            # Markers afwisselend boven/onder de lijn
            y_positions = [1 if i % 2 == 0 else -1 for i in range(len(df_m))]
            colors = ["#10b981" if s.startswith("✅") else "#f59e0b"
                      for s in df_m["Status"]]
            fig_m.add_trace(go.Scatter(
                x=df_m["Datum"], y=y_positions,
                mode="markers+text",
                marker=dict(symbol="diamond", size=26, color=colors,
                            line=dict(color="#1f2937", width=1.5)),
                text=[f"<b>{n}</b><br>{d.strftime('%d %b %Y')}"
                      for n, d in zip(df_m["Naam"], df_m["Datum"])],
                textposition=["top center" if p > 0 else "bottom center"
                              for p in y_positions],
                hovertemplate="<b>%{customdata[0]}</b><br>"
                              "📅 %{x|%d %b %Y}<br>"
                              "👥 %{customdata[1]}<br>"
                              "📝 %{customdata[2]}<extra></extra>",
                customdata=df_m[["Naam", "Betrokkenen", "Aandachtspunten"]].values,
                showlegend=False,
            ))
            fig_m.update_yaxes(visible=False, range=[-2.5, 2.5])
            fig_m.update_xaxes(showgrid=True, gridcolor="#e5e7eb")
            fig_m.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=10),
                                plot_bgcolor="white")
            st.plotly_chart(fig_m, use_container_width=True)

            # Begeleidende tabel
            st.markdown("#### Milestone-details")
            st.dataframe(
                df_m[["Naam", "Datum", "Status", "Betrokkenen", "Aandachtspunten"]],
                hide_index=True, use_container_width=True
            )

    with tab2:
        with st.form("new_ms"):
            st.subheader("Nieuw milestone toevoegen")
            nm_naam = st.text_input("Naam milestone *")
            c1, c2 = st.columns(2)
            with c1:
                nm_datum = st.text_input("Datum")
                nm_betrok = st.text_input("Betrokkenen")
            with c2:
                nm_punten = st.text_area("Aandachtspunten", height=80)
            if st.form_submit_button("➕ Toevoegen", type="primary"):
                if nm_naam:
                    data["milestones"].append({
                        "id": str(uuid.uuid4())[:8], "naam": nm_naam,
                        "datum": nm_datum, "betrokkenen": nm_betrok,
                        "aandachtspunten": nm_punten, "afgerond": False
                    })
                    save(data)
                    st.rerun()
                else:
                    st.error("Vul de naam in.")

# ═══════════════════════════════════════════════════════════════
# PAGE: KPI TRACKING
# ═══════════════════════════════════════════════════════════════
elif page == "📈 KPI's":
    st.title("📈 KPI Tracking")
    tab1, tab2, tab3 = st.tabs(["📊 Maandelijkse waarden", "📈 Trendgrafiek", "➕ Nieuwe KPI"])

    with tab1:
        df_kpi = pd.DataFrame(data["kpis"])[["naam", "target"] + MONTHS]
        df_kpi.columns = ["KPI", "Target"] + MONTHS

        edited_kpi = st.data_editor(
            df_kpi,
            use_container_width=True,
            hide_index=True,
            column_config={
                "KPI": st.column_config.TextColumn(width="large"),
                "Target": st.column_config.TextColumn(width="small"),
                **{m: st.column_config.TextColumn(m, width="small") for m in MONTHS}
            },
            key="kpi_editor"
        )

        if st.button("💾 KPI-waarden opslaan", type="primary"):
            for i in range(len(data["kpis"])):
                if i < len(edited_kpi):
                    row = edited_kpi.iloc[i]
                    data["kpis"][i]["naam"] = row["KPI"]
                    data["kpis"][i]["target"] = row["Target"]
                    for m in MONTHS:
                        data["kpis"][i][m] = row[m]
            save(data)
            st.rerun()

    with tab2:
        st.subheader("KPI Trends over tijd")
        kpi_namen = [k["naam"] for k in data["kpis"]]
        selected = st.multiselect("Selecteer KPI's", kpi_namen, default=kpi_namen[:3])

        trend_rows = []
        for kpi in data["kpis"]:
            if kpi["naam"] in selected:
                for m in MONTHS:
                    val = kpi.get(m, "")
                    if val and str(val).strip():
                        try:
                            num = float(str(val).replace("%", "").replace(",", ".").strip())
                            trend_rows.append({"KPI": kpi["naam"], "Maand": m, "Waarde": num})
                        except ValueError:
                            pass

        if trend_rows:
            df_trend = pd.DataFrame(trend_rows)
            fig = px.line(df_trend, x="Maand", y="Waarde", color="KPI",
                         markers=True, title="KPI Verloop 2026",
                         category_orders={"Maand": MONTHS})
            fig.update_layout(height=420, plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("💡 Vul eerst meetwaarden in via de **Maandelijkse waarden** tab om de trend te zien.")

    with tab3:
        with st.form("new_kpi"):
            st.subheader("Nieuwe KPI toevoegen")
            c1, c2 = st.columns(2)
            with c1:
                nk_naam = st.text_input("KPI naam *")
                nk_target = st.text_input("Target (bv. ≥ 80%)")
            with c2:
                nk_eenheid = st.selectbox("Eenheid", ["%", "#", "score", "anders"])
            if st.form_submit_button("➕ KPI toevoegen", type="primary"):
                if nk_naam:
                    data["kpis"].append({
                        "id": str(uuid.uuid4())[:8], "naam": nk_naam,
                        "target": nk_target, "eenheid": nk_eenheid,
                        **{m: "" for m in MONTHS}
                    })
                    save(data)
                    st.rerun()
                else:
                    st.error("Vul een naam in.")

# ═══════════════════════════════════════════════════════════════
# PAGE: PRIORITEITEN
# ═══════════════════════════════════════════════════════════════
elif page == "🏆 Prioriteiten":
    st.title("🏆 Prioriteitenlijst")

    # ── Auto-sync: elke taak moet een prioriteit-rij hebben ──
    existing_codes = {p["pijler"] for p in data["prioriteiten"]}
    max_rang = max((p["rang"] for p in data["prioriteiten"]), default=0)
    toegevoegd = 0
    for t in data["taken"]:
        code = f"P{t['nummer']}"
        if code not in existing_codes:
            max_rang += 1
            data["prioriteiten"].append({
                "rang": max_rang, "urgentie": "🟡 Q3",
                "actie": t["subtaak"], "pijler": code,
                "verantwoordelijke": t.get("verantwoordelijke", ""),
                "deadline": t.get("deadline", ""),
                "impact": "⭐⭐⭐", "reden": "",
                "status": t.get("status", "Gepland")
            })
            toegevoegd += 1
    if toegevoegd:
        _write(data)
        st.info(f"🔄 {toegevoegd} nieuwe taak/taken automatisch toegevoegd aan prioriteiten. "
                "Vul Urgentie, Impact en Reden hieronder aan.")

    tab1, tab2 = st.tabs(["📄 Overzicht", "➕ Nieuwe prioriteit"])

    with tab1:
        urgentie_filter = st.selectbox("Filter op urgentie", ["Alle", "🔴 Nu", "🟡 Q3", "🟢 Q4"])
        filtered_p = data["prioriteiten"] if urgentie_filter == "Alle" else \
                     [p for p in data["prioriteiten"] if p["urgentie"] == urgentie_filter]

        if not filtered_p:
            st.info("Geen items gevonden.")
        else:
            df_p = pd.DataFrame(filtered_p)[["rang", "urgentie", "actie", "pijler", "verantwoordelijke", "deadline", "impact", "status", "reden"]]
            df_p.columns = ["#", "Urgentie", "Actie", "Pijler", "Verantwoordelijke", "Deadline", "Impact", "Status", "Reden"]

            edited_p = st.data_editor(
                df_p,
                column_config={
                    "Status": st.column_config.SelectboxColumn(options=STATUS_OPTIONS, required=True, width="small"),
                    "Urgentie": st.column_config.SelectboxColumn(options=["🔴 Nu", "🟡 Q3", "🟢 Q4"], width="small"),
                    "Impact": st.column_config.SelectboxColumn(
                        options=["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐", "⭐"], width="small"),
                    "Pijler": st.column_config.SelectboxColumn(
                        options=taak_pijler_codes(data["taken"]), width="small"),
                    "Actie": st.column_config.TextColumn(width="large"),
                    "Reden": st.column_config.TextColumn(width="large"),
                },
                use_container_width=True,
                hide_index=True,
                key="prio_editor"
            )

            if st.button("💾 Opslaan", type="primary", key="save_prio"):
                filtered_rangs = [p["rang"] for p in filtered_p]
                for i, rang in enumerate(filtered_rangs):
                    for p in data["prioriteiten"]:
                        if p["rang"] == rang:
                            row = edited_p.iloc[i]
                            p["urgentie"] = row["Urgentie"]
                            p["actie"] = row["Actie"]
                            p["pijler"] = row["Pijler"]
                            p["verantwoordelijke"] = row["Verantwoordelijke"]
                            p["deadline"] = row["Deadline"]
                            p["impact"] = row["Impact"]
                            p["status"] = row["Status"]
                            p["reden"] = row["Reden"]
                            break
                save(data)
                st.rerun()

    with tab2:
        with st.form("new_prio"):
            st.subheader("Nieuwe prioriteit toevoegen")
            c1, c2 = st.columns(2)
            with c1:
                np_actie = st.text_input("Actie *")
                np_verantw = st.text_input("Verantwoordelijke")
                np_deadline = st.text_input("Deadline")
                np_pijler = st.selectbox("Pijler (koppel aan taak)", taak_pijler_codes(data["taken"]))
            with c2:
                np_urgentie = st.selectbox("Urgentie", ["🔴 Nu", "🟡 Q3", "🟢 Q4"])
                np_impact = st.selectbox("Impact", ["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐", "⭐"])
                np_status = st.selectbox("Status", STATUS_OPTIONS)
                np_reden = st.text_area("Reden / toelichting", height=80)
            if st.form_submit_button("➕ Toevoegen", type="primary"):
                if np_actie:
                    max_rang = max((p["rang"] for p in data["prioriteiten"]), default=0)
                    data["prioriteiten"].append({
                        "rang": max_rang + 1, "urgentie": np_urgentie, "actie": np_actie,
                        "pijler": np_pijler, "verantwoordelijke": np_verantw,
                        "deadline": np_deadline, "impact": np_impact,
                        "reden": np_reden, "status": np_status
                    })
                    save(data)
                    st.rerun()
                else:
                    st.error("Vul de actie in.")

# ═══════════════════════════════════════════════════════════════
# PAGE: WAARDEPROPOSITIE
# ═══════════════════════════════════════════════════════════════
elif page == "💡 Waardepropositie":
    st.title("💡 Waardepropositie – Doelen ↔ Waarde KZA")

    tab1, tab2 = st.tabs(["👥 Voor medewerkers", "🏢 Voor bedrijven / klanten"])

    with tab1:
        subtab_mw1, subtab_mw2 = st.tabs(["📄 Overzicht & bewerken", "➕ Nieuwe rij"])
        MW_COLS = {"doel": "Doel", "waarde_mw": "Wat levert het de medewerker op?",
                   "resultaat_mw": "Concreet resultaat", "pijler": "Pijler"}
        with subtab_mw1:
            st.subheader("Waarde voor medewerkers")
            df_mw = pd.DataFrame(data["waarde_medewerkers"] or [],
                                 columns=list(MW_COLS.keys())).rename(columns=MW_COLS)
            edited_mw = st.data_editor(
                df_mw, use_container_width=True, hide_index=True,
                column_config={
                    "Doel": st.column_config.SelectboxColumn(
                        options=taak_subtaken(data["taken"]), width="large"),
                    "Pijler": st.column_config.SelectboxColumn(
                        options=taak_pijler_codes(data["taken"]), width="small"),
                    "Wat levert het de medewerker op?": st.column_config.TextColumn(width="large"),
                    "Concreet resultaat": st.column_config.TextColumn(width="large"),
                },
                key="mw_editor"
            )
            if st.button("💾 Opslaan", type="primary", key="save_mw"):
                data["waarde_medewerkers"] = [
                    {"doel": row["Doel"], "waarde_mw": row["Wat levert het de medewerker op?"],
                     "resultaat_mw": row["Concreet resultaat"], "pijler": row["Pijler"]}
                    for _, row in edited_mw.iterrows()
                ]
                save(data)
                st.rerun()
        with subtab_mw2:
            with st.form("new_mw"):
                st.subheader("Nieuwe rij toevoegen")
                subtaken = taak_subtaken(data["taken"])
                pijler_codes = taak_pijler_codes(data["taken"])
                mw_doel = st.selectbox("Taak (Doel) *", subtaken)
                default_pijler = pijler_codes[subtaken.index(mw_doel)] if mw_doel in subtaken else pijler_codes[0]
                mw_pijler = st.selectbox("Pijler", pijler_codes,
                                         index=pijler_codes.index(default_pijler))
                mw_waarde = st.text_area("Wat levert het de medewerker op?", height=70)
                mw_resultaat = st.text_area("Concreet resultaat", height=70)
                if st.form_submit_button("➕ Toevoegen", type="primary"):
                    data["waarde_medewerkers"].append({
                        "doel": mw_doel, "waarde_mw": mw_waarde,
                        "resultaat_mw": mw_resultaat, "pijler": mw_pijler
                    })
                    save(data)
                    st.rerun()

    with tab2:
        subtab_bdr1, subtab_bdr2 = st.tabs(["📄 Overzicht & bewerken", "➕ Nieuwe rij"])
        BDR_COLS = {"doel": "Doel", "waarde_bdr": "Wat levert het het bedrijf op?",
                    "resultaat_bdr": "Concreet resultaat", "pijler": "Pijler"}
        with subtab_bdr1:
            st.subheader("Waarde voor bedrijven / klanten")
            df_bdr = pd.DataFrame(data["waarde_bedrijven"] or [],
                                  columns=list(BDR_COLS.keys())).rename(columns=BDR_COLS)
            edited_bdr = st.data_editor(
                df_bdr, use_container_width=True, hide_index=True,
                column_config={
                    "Doel": st.column_config.SelectboxColumn(
                        options=taak_subtaken(data["taken"]), width="large"),
                    "Pijler": st.column_config.SelectboxColumn(
                        options=taak_pijler_codes(data["taken"]), width="small"),
                    "Wat levert het het bedrijf op?": st.column_config.TextColumn(width="large"),
                    "Concreet resultaat": st.column_config.TextColumn(width="large"),
                },
                key="bdr_editor"
            )
            if st.button("💾 Opslaan", type="primary", key="save_bdr"):
                data["waarde_bedrijven"] = [
                    {"doel": row["Doel"], "waarde_bdr": row["Wat levert het het bedrijf op?"],
                     "resultaat_bdr": row["Concreet resultaat"], "pijler": row["Pijler"]}
                    for _, row in edited_bdr.iterrows()
                ]
                save(data)
                st.rerun()
        with subtab_bdr2:
            with st.form("new_bdr"):
                st.subheader("Nieuwe rij toevoegen")
                subtaken_b = taak_subtaken(data["taken"])
                pijler_codes_b = taak_pijler_codes(data["taken"])
                bdr_doel = st.selectbox("Taak (Doel) *", subtaken_b)
                default_pijler_b = pijler_codes_b[subtaken_b.index(bdr_doel)] if bdr_doel in subtaken_b else pijler_codes_b[0]
                bdr_pijler = st.selectbox("Pijler", pijler_codes_b,
                                          index=pijler_codes_b.index(default_pijler_b))
                bdr_waarde = st.text_area("Wat levert het het bedrijf op?", height=70)
                bdr_resultaat = st.text_area("Concreet resultaat", height=70)
                if st.form_submit_button("➕ Toevoegen", type="primary"):
                    data["waarde_bedrijven"].append({
                        "doel": bdr_doel, "waarde_bdr": bdr_waarde,
                        "resultaat_bdr": bdr_resultaat, "pijler": bdr_pijler
                    })
                    save(data)
                    st.rerun()
