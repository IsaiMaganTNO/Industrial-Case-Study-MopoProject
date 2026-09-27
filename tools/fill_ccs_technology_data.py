"""Fill the missing +CC technology rows in the gas dataset.

Problem
-------
Technology_Costs and Technology_Conversion declare two carbon-capture
technologies but leave every numeric field blank:

    bio-diges-up+CC        (capex, fom, vom, lifetime, conversion = NaN)
    bio-gasif-metha+CC     (idem)

gas_import.py guards every write with `if pd.notna(row.iloc[N])`, so those rows
are silently skipped. The technology entity is still created and still receives
an investment_count_max_cumulative cap, so SpineOpt sees a technology that is
FREE TO BUILD and capped at 1000 per region.

In the 2026-09-27 tiny test run bio-diges-up+CC was built to its cap in all 17
regions (17,000 units = 98.3% of all installed capacity) and, being charged FOM
on capacity nobody chose economically, produced an implausible 88.8% fixed-O&M
share of total system cost.

Approach
--------
Derive the CCS uplift from the SMR -> SMR+CC pair ALREADY PRESENT in the same
sheet, rather than inventing a number:

    capex / fom uplift : 1.1600   (0.6058/0.5222, identical in all three years)
    vom uplift         : 1.3206
    efficiency penalty : 0.69/0.76 = 0.9079
    CO2 output         : 0.132 per unit of fuel input (SMR+CC, CH4 -> CO2)

Lifetime and currency are copied unchanged from the parent: capture equipment
does not change the plant's economic life or the cost base year.

Only fills blanks; never overwrites existing data. Safe to re-run.
"""
import shutil
from pathlib import Path
import pandas as pd

CAPEX_FOM_UPLIFT = 0.6057532171 / 0.5222010492
VOM_UPLIFT = 1.3206
EFFICIENCY_PENALTY = 0.69 / 0.76
CO2_PER_FUEL_IN = 0.132

PAIRS = {
    "bio-diges-up+CC": "bio-diges-up",
    "bio-gasif-metha+CC": "bio-gasif-metha",
}

WORKBOOKS = [
    Path("data/Gas/Gas_Sectors_Dataset_IC1_placeholder.xlsx"),
    Path("data/Gas/Gas_Sectors_Dataset.xlsx"),
]


def fill_costs(df):
    changed = []
    tech_col = df.columns[0]
    for cc_name, parent_name in PAIRS.items():
        cc = df.index[df[tech_col] == cc_name]
        par = df.index[df[tech_col] == parent_name]
        if len(cc) == 0 or len(par) == 0:
            continue
        i, p = cc[0], par[0]
        if pd.notna(df.iat[i, 2]):
            continue
        for c in range(2, 8):
            df.iat[i, c] = df.iat[p, c] * CAPEX_FOM_UPLIFT
        for c in range(8, 11):
            if pd.notna(df.iat[p, c]):
                df.iat[i, c] = df.iat[p, c] * VOM_UPLIFT
        df.iat[i, 11] = df.iat[p, 11]
        df.iat[i, 12] = df.iat[p, 12]
        note = ("Derived from " + parent_name + " using the SMR->SMR+CC uplift "
                "in this sheet (capex/fom x%.4f, vom x%s)." % (CAPEX_FOM_UPLIFT, VOM_UPLIFT))
        if df.shape[1] > 14:
            df.iat[i, 14] = note
        if df.shape[1] > 15:
            df.iat[i, 15] = "derived: SMR/SMR+CC ratio"
        changed.append("%s: capex %.4f M/MW, fom %.0f /MW/y, lifetime %s"
                       % (cc_name, df.iat[i, 2], df.iat[i, 5], df.iat[i, 11]))
    return changed


def fill_conversion(df):
    changed = []
    for cc_name, parent_name in PAIRS.items():
        par = df.index[df["technology"] == parent_name]
        if len(par) == 0:
            continue
        p = par[0]
        for i in df.index[df["technology"] == cc_name]:
            if pd.notna(df.iat[i, 3]):
                continue
            to_node = df.iat[i, 2]
            for c in (3, 4, 5):
                if to_node == "CO2":
                    df.iat[i, c] = CO2_PER_FUEL_IN
                else:
                    df.iat[i, c] = round(df.iat[p, c] * EFFICIENCY_PENALTY, 4)
            df.iat[i, 6] = ("Derived from " + parent_name + " using the SMR->SMR+CC "
                            "efficiency penalty (%.4f) and CO2 capture ratio (%s)."
                            % (EFFICIENCY_PENALTY, CO2_PER_FUEL_IN))
            changed.append("%s: %s -> %s = %s" % (cc_name, df.iat[i, 1], to_node, df.iat[i, 3]))
    return changed


def main():
    print("CCS uplift derived from SMR -> SMR+CC in this dataset:")
    print("   capex / fom        x %.4f" % CAPEX_FOM_UPLIFT)
    print("   vom                x %s" % VOM_UPLIFT)
    print("   efficiency penalty x %.4f" % EFFICIENCY_PENALTY)
    print("   CO2 per fuel in      %s" % CO2_PER_FUEL_IN)
    print("")
    for wb in WORKBOOKS:
        if not wb.exists():
            print("skip (not found): %s" % wb)
            continue
        backup = wb.with_suffix(".xlsx.bak")
        if not backup.exists():
            shutil.copy2(wb, backup)
            print("backup -> %s" % backup.name)
        sheets = pd.read_excel(wb, sheet_name=None)
        costs = fill_costs(sheets["Technology_Costs"])
        conv = fill_conversion(sheets["Technology_Conversion"])
        if not costs and not conv:
            print("%s: nothing to fill (already populated)" % wb.name)
            continue
        with pd.ExcelWriter(wb, engine="openpyxl") as writer:
            for name, frame in sheets.items():
                frame.to_excel(writer, sheet_name=name, index=False)
        print("%s:" % wb.name)
        for line in costs + conv:
            print("   %s" % line)


if __name__ == "__main__":
    main()
