"""Read-only verification of the CO2 emission/capture source data.

Writes findings to logs/verify_co2_source.txt. Does not modify any database.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "data" / "Industry" / "technology_catalogue_ind_nuts0_nuts3.xlsx"
OUT = ROOT / "logs" / "verify_co2_source.txt"
OUT.parent.mkdir(exist_ok=True)

YEARS = ["2030", "2040", "2050"]
lines = []


def say(msg=""):
    lines.append(str(msg))


say(f"source: {XLSX}")
xl = pd.ExcelFile(XLSX)
co2_sheets = [s for s in xl.sheet_names if "co2" in s.lower()]
say(f"co2-related sheets: {co2_sheets}")
say()

emi = xl.parse("ind_process_routes_co2_emission")
cap = xl.parse("ind_process_routes_co2_capture")

say("=== 1. shape and columns ===")
say(f"emission: {emi.shape}  cols={list(emi.columns)}")
say(f"capture : {cap.shape}  cols={list(cap.columns)}")
say()

say("=== 2. unit columns present? ===")
for name, df in (("emission", emi), ("capture", cap)):
    unit_cols = [c for c in df.columns if "unit" in str(c).lower()]
    say(f"{name}: unit-like columns = {unit_cols}")
    for c in unit_cols:
        say(f"    {c} values: {sorted(df[c].dropna().unique().tolist())}")
say()

say("=== 3. refinery routes (the dominant emitter in reports_1rep_repfix) ===")
ref = emi[emi["Industry"].astype(str).str.startswith("REF")]
say("emission sheet:")
say(ref.to_string(index=False))
say()
refc = cap[cap["Industry"].astype(str).str.startswith("REF")]
say("capture sheet:")
say(refc.to_string(index=False))
say()

say("=== 4. negative (BECCS) emission rows - must survive any >0 guard ===")
neg = emi[emi[YEARS].lt(0).any(axis=1)]
say(f"count = {len(neg)}")
if len(neg):
    say(neg.to_string(index=False))
say()

say("=== 5. emission+capture == unabated? (the 'already net' claim) ===")
key = ["Industry", "to_node"] if "to_node" in emi.columns else ["Industry"]
merged = emi.merge(cap, on=key, suffixes=("_emi", "_cap"), how="inner")
say(f"paired rows: {len(merged)}  (emission rows={len(emi)}, capture rows={len(cap)})")
if "unit_emi" in merged.columns and "unit_cap" in merged.columns:
    mismatch = merged[merged["unit_emi"] != merged["unit_cap"]]
    say(f"unit mismatches between the two sheets: {len(mismatch)}")
merged["sum2030"] = merged["2030_emi"] + merged["2030_cap"]
say()
say("sample of paired rows (emitted + captured = total):")
cols = key + ["2030_emi", "2030_cap", "sum2030"]
say(merged[cols].head(25).to_string(index=False))
say()

say("=== 6. guard check: how many rows would a '> 0.0' guard silently drop? ===")
say(f"emission rows with 2030 == 0 : {(emi['2030'] == 0).sum()}")
say(f"emission rows with 2030 <  0 : {(emi['2030'] < 0).sum()}")
say(f"capture  rows with 2030 == 0 : {(cap['2030'] == 0).sum()}")

OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"wrote {OUT} ({len(lines)} lines)")
