"""Option 1: restore the refinery CO2 gateway charge.

WHY THIS EXISTS
---------------
patch_co2_in_model_db.py replaced every industrial unit's atmosphere
coefficient with the per-route factor from ind_process_routes_co2_emission.
For *terminal consumers* (coal/waste industry) that is right.

For *gateways* it is wrong. A refinery does not consume crude and stop; it
converts crude into HC_* which the rest of the model then burns. The original
0.26 on (REF*, atmosphere, crude) was load-bearing: it bundled the refinery's
own process emissions AND the downstream combustion carbon of every unit of
refined product. Replacing it with the on-site-only route factor (0.00128 for
REF-SMR-MEA, a 203x cut) deleted refined-product carbon from the model.

Observed consequence in the 1rep_co2patch solve:
    oil-eng charged 0.0057 tCO2/MWh_el  vs  CCGT at 0.3448 - i.e. oil-fired
    generation looked 60x CLEANER than gas. The model duly built 23.5 GW of
    oil-eng and 173.6 GW of REF-SMR-MEA as a carbon-laundering route.

WHY NOT CHARGE THE HC_* CONSUMERS INSTEAD (option 2)
----------------------------------------------------
That is the more correct fix and is documented as the pipeline change. It is
NOT done here because HC_* is a shared carrier: (BM)FT and (H2)FT-DC can also
feed it. Charging consumers a flat fossil 0.24 would mis-charge synthetic HC.
Today synthetic HC share is 0.0%, so option 2 would be safe *now* - but it is
a landmine, and CH4_* already shows why: 44.7% of methane is synthetic by 2050.

WHAT THIS DOES
--------------
Sets the 51 (REF*, atmosphere, crude, REF*) coefficients back to crude's
CO2_content = 0.26 (data/Commodities/commodity_data.csv). Pure UPDATEs - no
new entities - so it is trivially reversible.

KNOWN LIMITATION
----------------
REF-SMR and REF-SMR-MEA then emit identically, so refinery CCS loses its
incentive. That is the pre-patch behaviour, not a new defect.

Usage:
    python tools/revert_refinery_gateway.py <db>          # dry run
    python tools/revert_refinery_gateway.py <db> --apply
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from patch_co2_in_model_db import flat_byname, scalar  # noqa: E402

# crude's CO2_content, ton/MWh, from data/Commodities/commodity_data.csv
CRUDE_CO2_CONTENT = 0.26
PARAM = "flow_ratio_equality_coefficient"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--backup", action="store_true")
    args = ap.parse_args()

    if args.apply and args.backup:
        bak = Path(args.db).with_suffix(".pregwrevert.sqlite")
        shutil.copy2(args.db, bak)
        print("backup written: %s" % bak)

    con = sqlite3.connect(args.db)
    con.execute("PRAGMA foreign_keys = OFF")

    rows = con.execute(
        "SELECT pv.id, e.id, pv.value FROM parameter_value pv "
        "JOIN parameter_definition pd ON pd.id = pv.parameter_definition_id "
        "JOIN entity e ON e.id = pv.entity_id WHERE pd.name = ?",
        (PARAM,),
    ).fetchall()

    todo = []
    for pvid, eid, val in rows:
        bn = flat_byname(con, eid)
        # (unit, atmosphere, crude, unit) == the refinery gateway emission row
        if len(bn) == 4 and bn[1] == "atmosphere" and bn[2] == "crude":
            todo.append((pvid, bn[0], scalar(val)))

    print("refinery gateway rows found : %d" % len(todo))
    blob = repr(float(CRUDE_CO2_CONTENT)).encode()
    changed = 0
    for pvid, unit, old in sorted(todo, key=lambda r: r[1]):
        if old is not None and abs(old - CRUDE_CO2_CONTENT) < 1e-12:
            continue
        changed += 1
        if changed <= 6:
            print("  %-22s %-10s -> %.5f" % (unit, old, CRUDE_CO2_CONTENT))
        if args.apply:
            con.execute(
                "UPDATE parameter_value SET value = ?, type = 'float' WHERE id = ?",
                (blob, pvid),
            )
    if changed > 6:
        print("  ... and %d more" % (changed - 6))
    print("rows needing change         : %d" % changed)

    if args.apply:
        con.commit()
        print("APPLIED")
    else:
        print("DRY RUN - nothing written")
    con.close()


if __name__ == "__main__":
    main()
