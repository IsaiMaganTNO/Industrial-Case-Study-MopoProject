"""Compare postprocessing outputs between a baseline run and one or more
candidate runs. Reads the CSVs produced by `visualization.py` for each run.

Example:
    python _visualization/compare_runs.py \\
        --baseline _baselines/2026-07-22_baseline_v1.0.0-upgrade/files_out \\
        --candidate _visualization/files_out \\
        --candidate-label "with-vre-fix"

    python _visualization/compare_runs.py \\
        --baseline _baselines/2026-07-22_baseline_v1.0.0-upgrade/files_out \\
        --candidate _baselines/2026-07-27_with-co2-patch_no-annual-cap/files_out \\
        --candidate-label "co2-patched-no-cap" \\
        --candidate _visualization/files_out \\
        --candidate-label "with-vre-fix"

Emits `_comparison_report.txt` in the current directory (or --output).

Notes:
  - The label list must have the same length as the candidate list, in the
    same order. If labels are omitted, folder names are used.
  - No hardcoded run names — this replaces the old `compare_three_runs.py`
    that had baselines baked in.
"""
from pathlib import Path
import argparse
import sys
import pandas as pd


YEARS = ["y2030", "y2040", "y2050"]


def _load(files_out: Path, name: str) -> pd.DataFrame:
    p = files_out / name
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p, index_col=0)
    return df.loc[:, ~df.columns.str.contains(r"^Unnamed")]


def total_emissions(files_out: Path) -> pd.Series:
    df = _load(files_out, "emissions_flows.csv")
    if df.empty or "technology" not in df.columns:
        return pd.Series(0.0, index=YEARS)
    to_atmo = df[df["technology"] == "atmosphere"]
    return to_atmo[YEARS].sum()


def installed_by_tech(files_out: Path, top_n: int = 15) -> pd.DataFrame:
    df = _load(files_out, "installed_capacity.csv")
    if df.empty or "technology" not in df.columns:
        return pd.DataFrame()
    return (df.groupby("technology")[YEARS].sum()
              .sort_values("y2050", ascending=False)
              .head(top_n))


def invested_by_tech(files_out: Path, top_n: int = 15) -> pd.DataFrame:
    df = _load(files_out, "invested_capacity.csv")
    if df.empty or "technology" not in df.columns:
        return pd.DataFrame()
    return (df.groupby("technology")[YEARS].sum()
              .sort_values("y2050", ascending=False)
              .head(top_n))


def total_invested_cost(files_out: Path) -> pd.Series:
    df = _load(files_out, "invested_cost.csv")
    if df.empty:
        return pd.Series(0.0, index=YEARS)
    return df[YEARS].sum()


def emissions_by_sector(files_out: Path, top_n: int = 8) -> pd.DataFrame:
    df = _load(files_out, "emissions_flows.csv")
    if df.empty or "technology" not in df.columns:
        return pd.DataFrame()
    to_atmo = df[df["technology"] == "atmosphere"].copy()
    to_atmo["source"] = to_atmo["source"].fillna("(unlabeled)")
    return (to_atmo.groupby("source")[YEARS].sum()
              .sort_values("y2030", ascending=False)
              .head(top_n))


def _run_label(files_out: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    # Try parent folder name (e.g. _baselines/YYYY-MM-DD_label/files_out → the parent)
    return files_out.parent.name if files_out.name == "files_out" else files_out.name


def compare(baseline_dir: Path, baseline_label: str,
            candidates: list[tuple[Path, str]]) -> str:
    """Produce the human-readable comparison report."""
    lines = []
    lines.append(f"Baseline: [{baseline_label}] {baseline_dir}")
    for path, label in candidates:
        lines.append(f"Candidate: [{label}] {path}")
    lines.append("=" * 80)

    # 1. Total emissions
    lines.append("\n1. TOTAL EMISSIONS INTO ATMOSPHERE (Mt CO2/yr)")
    lines.append("-" * 80)
    rows = {baseline_label: total_emissions(baseline_dir)}
    for path, label in candidates:
        rows[label] = total_emissions(path)
    df = pd.DataFrame(rows).T
    lines.append(df.round(1).to_string())

    # 2. Emissions by sector — one block per run
    lines.append("\n2. EMISSIONS BY SECTOR (top 8 by y2030 per run)")
    lines.append("-" * 80)
    for label, path in [(baseline_label, baseline_dir)] + [(l, p) for p, l in candidates]:
        lines.append(f"\n[{label}]")
        sec = emissions_by_sector(path)
        if sec.empty:
            lines.append("  (no data)")
        else:
            lines.append(sec.round(2).to_string())

    # 3. Installed capacity top-15 by y2050
    lines.append("\n3. INSTALLED CAPACITY — top 15 by y2050 (GW)")
    lines.append("-" * 80)
    for label, path in [(baseline_label, baseline_dir)] + [(l, p) for p, l in candidates]:
        lines.append(f"\n[{label}]")
        inst = installed_by_tech(path)
        if inst.empty:
            lines.append("  (no data)")
        else:
            lines.append(inst.round(2).to_string())

    # 4. Invested capacity
    lines.append("\n4. INVESTED CAPACITY — top 15 by y2050 (GW)")
    lines.append("-" * 80)
    for label, path in [(baseline_label, baseline_dir)] + [(l, p) for p, l in candidates]:
        lines.append(f"\n[{label}]")
        inv = invested_by_tech(path)
        if inv.empty:
            lines.append("  (no data)")
        else:
            lines.append(inv.round(3).to_string())

    # 5. Total invested cost
    lines.append("\n5. TOTAL INVESTED COST BY YEAR")
    lines.append("-" * 80)
    rows = {baseline_label: total_invested_cost(baseline_dir)}
    for path, label in candidates:
        rows[label] = total_invested_cost(path)
    df = pd.DataFrame(rows).T
    lines.append(df.round(0).to_string())

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--baseline", type=Path, required=True,
                        help="Path to baseline files_out directory")
    parser.add_argument("--baseline-label", type=str, default=None,
                        help="Label for the baseline row (default: folder name)")
    parser.add_argument("--candidate", type=Path, action="append", required=True,
                        help="Path to a candidate files_out directory. Repeatable.")
    parser.add_argument("--candidate-label", type=str, action="append", default=[],
                        help="Label for the corresponding candidate. Repeat "
                             "once per --candidate, in the same order.")
    parser.add_argument("--output", type=Path, default=Path("_comparison_report.txt"),
                        help="Output file path")
    args = parser.parse_args()

    if not args.baseline.exists():
        print(f"ERROR: baseline does not exist: {args.baseline}")
        sys.exit(2)
    for c in args.candidate:
        if not c.exists():
            print(f"ERROR: candidate does not exist: {c}")
            sys.exit(2)

    # Align labels with candidates
    labels = list(args.candidate_label)
    while len(labels) < len(args.candidate):
        labels.append(_run_label(args.candidate[len(labels)], None))

    baseline_label = args.baseline_label or _run_label(args.baseline, None)

    report = compare(args.baseline, baseline_label, list(zip(args.candidate, labels)))
    print(report)
    args.output.write_text(report, encoding="utf-8")
    print(f"\nReport written to: {args.output.resolve()}")


if __name__ == "__main__":
    main()
