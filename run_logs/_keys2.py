import sys; sys.path.insert(0,"tools")
import make_report_2050 as R
F=R.F
print(F.D["MR"].keys())
for key,v in F.D["MR"].items():
    try: print(key, list(v.columns)[:12], v.carrier.unique()[:40] if "carrier" in v else "")
    except Exception as e: print(key, type(v))
