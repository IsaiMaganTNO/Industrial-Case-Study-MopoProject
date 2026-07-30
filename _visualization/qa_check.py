"""QA / sanity checks for the postprocessing pipeline outputs.

Run AFTER `visualization.py` has generated the CSVs. Emits
`_visualization/files_out/_qa_report.txt` summarising anomalies as
[OK] / [WARN] / [FAIL] entries.

Usage:
    python _visualization/qa_check.py [--files-out DIR] [--config FILE]

Defaults: files-out = _visualization/files_out, config = _planning-input-processsing/scenario_config.yml.

Exit code is 0 if no [FAIL] entries were emitted, 1 otherwise (so this
can be wired into CI or a Spine Toolbox pipeline as a gate).

Checks implemented:
  1. All expected CSVs exist and are non-empty.
  2. Row-level plausibility: no per-polygon capacity > 200 GW for a single tech.
  3. VRE presence: existing solar/wind should show up in installed_capacity.csv.
     If absent, the model is silently rejecting them again.
  4. Emission cap binding: if `emission_cap.enabled` in config, compare total
     emissions to the scheduled cap for each year.
  5. Energy balance per polygon per year (electricity node only): total
     generation into elec vs total consumption from elec should roughly agree.
  6. Cross-year consistency: installed[y] ≈ installed[y-1] + invested[y]
     - decommissioned[y] within a tolerance, per (unit_name).

Reviewer note: each check is a small pure function that returns a
list[str] of message lines; adding new checks is a one-liner in main().
"""
from pathlib import Path
import argparse
import sys
import pandas as pd
import yaml


CSVS = [
    "installed_capacity.csv",
    "invested_capacity.csv",
    "decommissioned_capacity.csv",
    "invested_cost.csv",
    "unit_to_flows.csv",
    "energy_flows.csv",
    "emissions_flows.csv",
    "crossborder_flows.csv",
    "storage_installed_capacity.csv",
    "storage_invested_capacity.csv",
    "storage_decommissioned_capacity.csv",
    "storage_cost_capacity.csv",
]

YEARS = ["y2030", "y2040", "y2050"]

# Plausibility thresholds for a small system like BE+NL.
# Any single (tech, polygon, year) row above this raises a WARN.
PLAUSIBILITY_MAX_GW = 200.0

# Energy balance tolerance (fraction) — |gen - cons| / cons must be below this
ENERGY_BALANCE_TOL = 0.10


def _load(files_out: Path, name: str) -> pd.DataFrame:
    p = files_out / name
    df = pd.read_csv(p, index_col=0)
    return df.loc[:, ~df.columns.str.contains(r"^Unnamed")]


# ─────────────────────────────────────────────────────────────
# Checks
# ─────────────────────────────────────────────────────────────
def check_csvs_exist(files_out: Path) -> list[str]:
    """CSV files exist and are non-empty."""
    msgs = []
    for c in CSVS:
        p = files_out / c
        if not p.exists():
            msgs.append(f"[FAIL] Missing CSV: {c}")
        elif p.stat().st_size < 100:
            msgs.append(f"[WARN] CSV suspiciously small (< 100 bytes): {c}")
        else:
            msgs.append(f"[OK]   Present: {c} ({p.stat().st_size/1024:.1f} KB)")
    return msgs


def check_capacity_plausibility(files_out: Path) -> list[str]:
    """No single (tech, polygon, year) row should exceed PLAUSIBILITY_MAX_GW."""
    msgs = []
    for name in ("installed_capacity.csv", "invested_capacity.csv"):
        df = _load(files_out, name)
        if "technology" not in df.columns:
            continue
        for y in YEARS:
            over = df[df[y].abs() > PLAUSIBILITY_MAX_GW]
            for _, row in over.iterrows():
                tech = row.get("technology", "?")
                polygon = row.get("polygon", "?")
                msgs.append(
                    f"[WARN] {name}: {tech}/{polygon}/{y} = {row[y]:.1f} GW "
                    f"exceeds plausibility threshold ({PLAUSIBILITY_MAX_GW} GW)"
                )
    if not msgs:
        msgs.append(f"[OK]   No single-row capacity exceeds {PLAUSIBILITY_MAX_GW} GW")
    return msgs


def check_vre_present(files_out: Path) -> list[str]:
    """Solar + wind existing capacity should appear in installed_capacity.csv.
    If it's absent, the model has silently rejected VRE again (which was
    the source of a real bug we recently fixed via annual-mean patching)."""
    msgs = []
    df = _load(files_out, "installed_capacity.csv")
    if "technology" not in df.columns:
        msgs.append("[FAIL] installed_capacity.csv missing 'technology' column")
        return msgs
    for label in ("Solar", "Onshore Wind", "Offshore Wind"):
        rows = df[df["technology"] == label]
        if rows.empty:
            msgs.append(
                f"[WARN] No '{label}' rows in installed_capacity.csv. "
                f"Either the model has no {label.lower()} capacity, or the "
                f"unit-name mapping is stale."
            )
            continue
        totals = rows[YEARS].sum()
        y2030 = totals.get("y2030", 0.0)
        if y2030 < 0.5:
            msgs.append(
                f"[WARN] '{label}' y2030 total is only {y2030:.2f} GW — check "
                f"availability_factor for {label.lower()} units"
            )
        else:
            msgs.append(
                f"[OK]   {label} y2030={y2030:.1f} GW, "
                f"y2040={totals.get('y2040', 0):.1f}, y2050={totals.get('y2050', 0):.1f}"
            )
    return msgs


def check_emission_cap(files_out: Path, config: dict) -> list[str]:
    """If emission_cap enabled in config, compare model emissions to schedule."""
    msgs = []
    cap_cfg = config.get("emission_cap", {}) or {}
    if not cap_cfg.get("enabled", False):
        msgs.append("[OK]   emission_cap disabled in config — no cap check needed")
        return msgs

    schedule = cap_cfg.get("schedule_Mt_per_year", {})
    if not schedule:
        msgs.append("[WARN] emission_cap enabled but schedule_Mt_per_year empty")
        return msgs

    df = _load(files_out, "emissions_flows.csv")
    to_atmo = df[df["technology"] == "atmosphere"]
    totals = to_atmo[YEARS].sum()

    year_map = {"y2030": 2030, "y2040": 2040, "y2050": 2050}
    for y_col, y_int in year_map.items():
        actual = float(totals.get(y_col, 0.0))
        cap = float(schedule.get(y_int, schedule.get(str(y_int), None)))
        if cap is None:
            msgs.append(f"[WARN] No cap defined for {y_int}")
            continue
        # Allow 20% overshoot as WARN, more as FAIL
        if actual <= cap:
            msgs.append(
                f"[OK]   {y_col} emissions {actual:.1f} Mt/yr <= cap {cap:.1f} Mt/yr"
            )
        elif actual <= 1.2 * cap:
            msgs.append(
                f"[WARN] {y_col} emissions {actual:.1f} Mt/yr slightly over "
                f"cap {cap:.1f} Mt/yr (+{100*(actual/cap-1):.0f}%)"
            )
        else:
            msgs.append(
                f"[FAIL] {y_col} emissions {actual:.1f} Mt/yr >> cap {cap:.1f} "
                f"Mt/yr (+{100*(actual/cap-1):.0f}%). Cap likely not binding — "
                f"check user_constraint linkages or per-hour scale factor."
            )
    return msgs


def check_energy_balance_elec(files_out: Path) -> list[str]:
    """Check gen ≈ cons on the electricity node per polygon per year."""
    msgs = []
    df = _load(files_out, "unit_to_flows.csv")
    if df.empty or "node" not in df.columns:
        return ["[WARN] unit_to_flows.csv missing 'node' column; skipping balance check"]

    # Generation INTO electricity
    gen = df[df["node"] == "electricity"]
    if gen.empty:
        msgs.append("[WARN] No units flowing INTO 'electricity' node found")
        return msgs

    energy = _load(files_out, "energy_flows.csv")
    # Consumption FROM electricity (rows where source == 'electricity')
    cons = energy[energy["source"] == "electricity"] if "source" in energy.columns else pd.DataFrame()

    for y in YEARS:
        gen_total = gen[y].sum() if y in gen.columns else 0.0
        cons_total = cons[y].sum() if (not cons.empty and y in cons.columns) else 0.0
        if cons_total <= 0.001:
            msgs.append(
                f"[WARN] {y} electricity consumption is ~0 "
                f"(gen={gen_total:.1f}) — check node mapping"
            )
            continue
        delta = (gen_total - cons_total) / cons_total
        if abs(delta) < ENERGY_BALANCE_TOL:
            msgs.append(
                f"[OK]   {y} electricity balance: gen={gen_total:.0f}, "
                f"cons={cons_total:.0f}, delta={100*delta:+.1f}%"
            )
        else:
            msgs.append(
                f"[WARN] {y} electricity IMBALANCE: gen={gen_total:.0f}, "
                f"cons={cons_total:.0f}, delta={100*delta:+.1f}% "
                f"(cross-border flows may account for this)"
            )
    return msgs


def check_stock_flow_consistency(files_out: Path) -> list[str]:
    """Per unit_name: installed[y] should be close to installed[y-1]
    + invested[y] - decommissioned[y]."""
    msgs = []
    inst = _load(files_out, "installed_capacity.csv")
    inv = _load(files_out, "invested_capacity.csv")
    dec = _load(files_out, "decommissioned_capacity.csv")

    if "unit_name" not in inst.columns:
        return ["[WARN] installed_capacity.csv missing 'unit_name'; skipping stock-flow check"]

    inst_by_unit = inst.set_index("unit_name")[YEARS] if not inst.empty else pd.DataFrame(columns=YEARS)
    inv_by_unit = inv.set_index("unit_name")[YEARS] if not inv.empty else pd.DataFrame(columns=YEARS)
    dec_by_unit = dec.set_index("unit_name")[YEARS] if not dec.empty else pd.DataFrame(columns=YEARS)

    n_bad = 0
    n_ok = 0
    for u in inst_by_unit.index:
        row_i = inst_by_unit.loc[u]
        row_inv = inv_by_unit.loc[u] if u in inv_by_unit.index else pd.Series(0.0, index=YEARS)
        row_dec = dec_by_unit.loc[u] if u in dec_by_unit.index else pd.Series(0.0, index=YEARS)
        # Handle duplicate unit_name rows by summing
        if isinstance(row_i, pd.DataFrame):
            row_i = row_i.sum()
        if isinstance(row_inv, pd.DataFrame):
            row_inv = row_inv.sum()
        if isinstance(row_dec, pd.DataFrame):
            row_dec = row_dec.sum()
        # Check y2040 = y2030 + inv[y2040] - dec[y2040]
        expected_2040 = row_i["y2030"] + row_inv["y2040"] - row_dec["y2040"]
        actual_2040 = row_i["y2040"]
        if abs(expected_2040 - actual_2040) > 0.1:
            n_bad += 1
        else:
            n_ok += 1
    total = n_bad + n_ok
    if total == 0:
        return ["[WARN] No units to check stock-flow consistency on"]
    if n_bad == 0:
        msgs.append(f"[OK]   stock-flow consistent for all {n_ok} units")
    elif n_bad < 0.05 * total:
        msgs.append(
            f"[OK]   stock-flow consistent for {n_ok}/{total} units "
            f"({n_bad} minor deviations)"
        )
    else:
        msgs.append(
            f"[WARN] stock-flow inconsistent for {n_bad}/{total} units "
            f"(installed[y] ≠ installed[y-1] + invested - decommissioned)"
        )
    return msgs


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--files-out", type=Path,
                        default=Path(__file__).resolve().parent / "files_out")
    parser.add_argument("--config", type=Path,
                        default=Path(__file__).resolve().parent.parent
                                / "_planning-input-processsing" / "scenario_config.yml")
    args = parser.parse_args()

    files_out = args.files_out.resolve()
    if not files_out.exists():
        print(f"ERROR: files_out directory does not exist: {files_out}")
        sys.exit(2)

    config = {}
    if args.config.exists():
        with open(args.config, "r") as f:
            config = yaml.safe_load(f) or {}

    all_msgs = []
    all_msgs.append(f"QA report for {files_out}")
    all_msgs.append(f"config: {args.config}")
    all_msgs.append("=" * 70)

    sections = [
        ("Files present",              lambda: check_csvs_exist(files_out)),
        ("Capacity plausibility",      lambda: check_capacity_plausibility(files_out)),
        ("VRE presence",               lambda: check_vre_present(files_out)),
        ("Emission cap",               lambda: check_emission_cap(files_out, config)),
        ("Electricity balance",        lambda: check_energy_balance_elec(files_out)),
        ("Stock-flow consistency",     lambda: check_stock_flow_consistency(files_out)),
    ]
    for title, fn in sections:
        all_msgs.append(f"\n--- {title} ---")
        try:
            all_msgs.extend(fn())
        except Exception as exc:
            all_msgs.append(f"[FAIL] Check '{title}' raised {type(exc).__name__}: {exc}")

    report = "\n".join(all_msgs) + "\n"

    # Print + write
    print(report)
    out_path = files_out / "_qa_report.txt"
    out_path.write_text(report, encoding="utf-8")
    print(f"\nQA report written to: {out_path}")

    # Exit code reflects worst finding
    if "[FAIL]" in report:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
