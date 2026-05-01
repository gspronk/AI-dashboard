#!/usr/bin/env python3
"""
KZA CLI – command-line tool voor het bijwerken van kza_data.json
Gebruik: python kza_cli.py <commando> [opties]

Commando's:
  status                              Toon overzicht van alle taken en KPI's
  taak list                           Toon alle taken
  taak update <nummer> --status <s>   Verander de status van een taak
  taak add                            Voeg een nieuwe taak toe (interactief)
  kpi list                            Toon alle KPI's
  kpi update <naam> --<maand> <waarde> Sla een KPI-meting op
  milestone list                      Toon alle milestones
  milestone done <naam_of_id>         Markeer een milestone als afgerond
  milestone open <naam_of_id>         Zet milestone terug op open
  prio list                           Toon prioriteitenlijst
  prio update <rang> --status <s>     Update status van een prioriteit
"""

import json
import os
import sys
import argparse

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kza_data.json")
STATUS_OPTIONS = ["Gepland", "Loopt", "Klaar", "Vertraagd"]
MONTHS = ["Mei", "Juni", "Juli", "Aug", "Sep", "Okt"]


def load():
    if not os.path.exists(DATA_FILE):
        print(f"FOUT: {DATA_FILE} niet gevonden.")
        sys.exit(1)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def ok(msg):
    print(f"✅ {msg}")


def err(msg):
    print(f"❌ {msg}")
    sys.exit(1)


# ── STATUS OVERZICHT ──────────────────────────────────────────
def cmd_status(args):
    data = load()
    taken = data["taken"]
    totaal = len(taken)
    counts = {s: sum(1 for t in taken if t["status"] == s) for s in STATUS_OPTIONS}
    ms_klaar = sum(1 for m in data["milestones"] if m["afgerond"])

    print("\n══════════════════════════════════════")
    print("  KZA DOELEN AI – STATUS OVERZICHT")
    print("══════════════════════════════════════")
    print(f"  Taken totaal : {totaal}")
    for s, c in counts.items():
        bar = "█" * c
        print(f"  {s:12} : {c:2}  {bar}")
    print(f"  Milestones   : {ms_klaar}/{len(data['milestones'])} afgerond")
    print()

    open_taken = [t for t in taken if t["status"] != "Klaar"]
    if open_taken:
        print("  Openstaande taken:")
        for t in open_taken:
            icon = {"Gepland": "⏳", "Loopt": "🔄", "Vertraagd": "🔴"}.get(t["status"], "")
            print(f"    {icon} [{t['nummer']}] {t['subtaak']} — {t['deadline']} ({t['status']})")
    print()


# ── TAKEN ─────────────────────────────────────────────────────
def cmd_taak(args):
    data = load()

    if args.subcommand == "list":
        print("\n── TAKEN ─────────────────────────────────────────────")
        for t in data["taken"]:
            icon = {"Gepland": "⏳", "Loopt": "🔄", "Klaar": "✅", "Vertraagd": "🔴"}.get(t["status"], "")
            print(f"  {icon} [{t['nummer']}] {t['subtaak']}")
            print(f"       Wie: {t['verantwoordelijke']}  |  Deadline: {t['deadline']}  |  Status: {t['status']}")
        print()

    elif args.subcommand == "update":
        nummer = args.nummer
        match = [t for t in data["taken"] if t["nummer"] == nummer]
        if not match:
            err(f"Taak '{nummer}' niet gevonden. Gebruik 'taak list' voor een overzicht.")
        taak = match[0]
        changed = []

        if args.status:
            if args.status not in STATUS_OPTIONS:
                err(f"Ongeldige status '{args.status}'. Kies uit: {', '.join(STATUS_OPTIONS)}")
            taak["status"] = args.status
            changed.append(f"status → {args.status}")
        if args.wie:
            taak["verantwoordelijke"] = args.wie
            changed.append(f"verantwoordelijke → {args.wie}")
        if args.deadline:
            taak["deadline"] = args.deadline
            changed.append(f"deadline → {args.deadline}")
        if args.beschrijving:
            taak["beschrijving"] = args.beschrijving
            changed.append(f"beschrijving bijgewerkt")

        if not changed:
            err("Geen wijzigingen opgegeven. Gebruik --status, --wie, --deadline of --beschrijving.")
        save(data)
        ok(f"Taak [{nummer}] {taak['subtaak']} bijgewerkt: {', '.join(changed)}")

    elif args.subcommand == "add":
        print("\nNieuwe taak toevoegen (druk Enter om leeg te laten):")
        nummer = input("  Nummer (bv. 1.5): ").strip()
        pijlers = list(dict.fromkeys(t["pijler"] for t in data["taken"]))
        print("  Beschikbare pijlers:")
        for i, p in enumerate(pijlers, 1):
            print(f"    {i}. {p}")
        keuze = input("  Pijler (nummer of naam): ").strip()
        if keuze.isdigit() and 1 <= int(keuze) <= len(pijlers):
            pijler = pijlers[int(keuze) - 1]
        else:
            pijler = keuze
        naam = input("  Subtaak naam: ").strip()
        wie = input("  Verantwoordelijke: ").strip()
        start = input("  Startmaand (bv. Maand 3): ").strip()
        deadline = input("  Deadline (bv. Eind juni 2026): ").strip()
        beschrijving = input("  Beschrijving: ").strip()
        print(f"  Status: {', '.join(STATUS_OPTIONS)}")
        status = input("  Status [Gepland]: ").strip() or "Gepland"

        if not naam:
            err("Naam is verplicht.")
        new_id = str(max((int(t["id"]) for t in data["taken"] if t["id"].isdigit()), default=0) + 1)
        data["taken"].append({
            "id": new_id, "nummer": nummer, "pijler": pijler, "subtaak": naam,
            "verantwoordelijke": wie, "startmaand": start, "deadline": deadline,
            "beschrijving": beschrijving, "status": status
        })
        save(data)
        ok(f"Taak [{nummer}] '{naam}' toegevoegd aan {pijler}.")


# ── KPI ───────────────────────────────────────────────────────
def cmd_kpi(args):
    data = load()

    if args.subcommand == "list":
        print("\n── KPI OVERZICHT ──────────────────────────────────────")
        print(f"  {'KPI':<38} {'Target':<10} {'Mei':>5} {'Juni':>5} {'Juli':>5} {'Aug':>5} {'Sep':>5} {'Okt':>5}")
        print("  " + "─" * 80)
        for k in data["kpis"]:
            row = f"  {k['naam']:<38} {k['target']:<10}"
            for m in MONTHS:
                val = str(k.get(m, "")).strip()
                row += f" {val:>5}" if val else f" {'—':>5}"
            print(row)
        print()

    elif args.subcommand == "update":
        naam = args.naam
        match = [k for k in data["kpis"] if naam.lower() in k["naam"].lower()]
        if not match:
            err(f"KPI '{naam}' niet gevonden. Gebruik 'kpi list' voor een overzicht.")
        if len(match) > 1:
            print("Meerdere KPI's gevonden:")
            for i, k in enumerate(match, 1):
                print(f"  {i}. {k['naam']}")
            keuze = int(input("Kies nummer: ")) - 1
            kpi = match[keuze]
        else:
            kpi = match[0]

        changed = []
        for m in MONTHS:
            val = getattr(args, m.lower(), None)
            if val is not None:
                kpi[m] = val
                changed.append(f"{m} → {val}")

        if not changed:
            err(f"Geen maandwaarden opgegeven. Gebruik --mei, --juni, --juli, --aug, --sep of --okt")
        save(data)
        ok(f"KPI '{kpi['naam']}' bijgewerkt: {', '.join(changed)}")


# ── MILESTONES ────────────────────────────────────────────────
def cmd_milestone(args):
    data = load()

    if args.subcommand == "list":
        print("\n── MILESTONES ─────────────────────────────────────────")
        for m in data["milestones"]:
            icon = "✅" if m["afgerond"] else "⏳"
            print(f"  {icon} [{m['id']}] {m['naam']} — {m['datum']}")
            print(f"       {m['aandachtspunten']}")
        print()

    elif args.subcommand in ("done", "open"):
        zoek = args.naam_of_id.lower()
        match = [m for m in data["milestones"]
                 if m["id"].lower() == zoek or zoek in m["naam"].lower()]
        if not match:
            err(f"Milestone '{args.naam_of_id}' niet gevonden.")
        ms = match[0]
        ms["afgerond"] = (args.subcommand == "done")
        save(data)
        staat = "afgerond ✅" if ms["afgerond"] else "terug op open ⏳"
        ok(f"Milestone '{ms['naam']}' gezet op {staat}.")


# ── PRIORITEITEN ──────────────────────────────────────────────
def cmd_prio(args):
    data = load()

    if args.subcommand == "list":
        print("\n── PRIORITEITEN ───────────────────────────────────────")
        for p in data["prioriteiten"]:
            icon = {"Gepland": "⏳", "Loopt": "🔄", "Klaar": "✅", "Vertraagd": "🔴"}.get(p["status"], "")
            print(f"  {icon} [{p['rang']:2}] {p['urgentie']} {p['actie']}")
            print(f"        Wie: {p['verantwoordelijke']}  |  Deadline: {p['deadline']}  |  Status: {p['status']}")
        print()

    elif args.subcommand == "update":
        rang = args.rang
        match = [p for p in data["prioriteiten"] if p["rang"] == rang]
        if not match:
            err(f"Prioriteit rang {rang} niet gevonden.")
        prio = match[0]
        changed = []

        if args.status:
            if args.status not in STATUS_OPTIONS:
                err(f"Ongeldige status. Kies uit: {', '.join(STATUS_OPTIONS)}")
            prio["status"] = args.status
            changed.append(f"status → {args.status}")
        if args.urgentie:
            prio["urgentie"] = args.urgentie
            changed.append(f"urgentie → {args.urgentie}")

        if not changed:
            err("Geen wijzigingen opgegeven. Gebruik --status of --urgentie.")
        save(data)
        ok(f"Prioriteit [{rang}] '{prio['actie']}' bijgewerkt: {', '.join(changed)}")


# ── MAIN ──────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="kza_cli",
        description="KZA Doelen AI – data bijwerken via de command line"
    )
    sub = parser.add_subparsers(dest="command")

    # status
    sub.add_parser("status", help="Toon overzicht")

    # taak
    p_taak = sub.add_parser("taak", help="Taakbeheer")
    taak_sub = p_taak.add_subparsers(dest="subcommand")
    taak_sub.add_parser("list")
    p_taak_upd = taak_sub.add_parser("update")
    p_taak_upd.add_argument("nummer", help="Taaknummer, bv. 1.1")
    p_taak_upd.add_argument("--status", choices=STATUS_OPTIONS)
    p_taak_upd.add_argument("--wie", dest="wie")
    p_taak_upd.add_argument("--deadline")
    p_taak_upd.add_argument("--beschrijving")
    taak_sub.add_parser("add")

    # kpi
    p_kpi = sub.add_parser("kpi", help="KPI-beheer")
    kpi_sub = p_kpi.add_subparsers(dest="subcommand")
    kpi_sub.add_parser("list")
    p_kpi_upd = kpi_sub.add_parser("update")
    p_kpi_upd.add_argument("naam", help="(Deel van) de KPI-naam")
    for m in MONTHS:
        p_kpi_upd.add_argument(f"--{m.lower()}", dest=m.lower(), metavar="WAARDE")

    # milestone
    p_ms = sub.add_parser("milestone", help="Milestone-beheer")
    ms_sub = p_ms.add_subparsers(dest="subcommand")
    ms_sub.add_parser("list")
    p_ms_done = ms_sub.add_parser("done")
    p_ms_done.add_argument("naam_of_id")
    p_ms_open = ms_sub.add_parser("open")
    p_ms_open.add_argument("naam_of_id")

    # prio
    p_prio = sub.add_parser("prio", help="Prioriteitenbeheer")
    prio_sub = p_prio.add_subparsers(dest="subcommand")
    prio_sub.add_parser("list")
    p_prio_upd = prio_sub.add_parser("update")
    p_prio_upd.add_argument("rang", type=int)
    p_prio_upd.add_argument("--status", choices=STATUS_OPTIONS)
    p_prio_upd.add_argument("--urgentie", choices=["🔴 Nu", "🟡 Q3", "🟢 Q4"])

    args = parser.parse_args()

    if args.command == "status":
        cmd_status(args)
    elif args.command == "taak":
        cmd_taak(args)
    elif args.command == "kpi":
        cmd_kpi(args)
    elif args.command == "milestone":
        cmd_milestone(args)
    elif args.command == "prio":
        cmd_prio(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
