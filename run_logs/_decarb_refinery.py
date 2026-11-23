import os, sys, pickle, shutil, pandas as pd
sys.path.insert(0, "tools"); import make_deck_final3 as F
hc = pickle.load(open(r"run_logs\_hc_supply.pkl", "rb"))
for k in F.K:
    rows = [dict(tech=t, region=c + "_ref", year=y, sector="refinery", output=v * 1e3, cc=t.endswith("MEA"), fuel="natural gas")
            for (t, c, y), v in hc[k].items() if c in ("NL", "BE") and v > 0]
    F.D[k]["prod"] = pd.concat([F.D[k]["prod"][F.D[k]["prod"].sector != "refinery"], pd.DataFrame(rows)], ignore_index=True)
    r = pd.DataFrame(rows); print(k, (r.groupby(["year", "cc"]).output.sum() / 1e3).round(1).to_dict())
F.SECS = F.SECS + ["refinery"]
src = F.f_decarb(); print("src", src)
dst = r"final_runs_pessimistic_ccs\industry_routes_by_sector_3runs_with_refinery.png"
tmp = dst + ".tmp.png"; shutil.copyfile(src, tmp); os.replace(tmp, dst); print("saved", dst)
