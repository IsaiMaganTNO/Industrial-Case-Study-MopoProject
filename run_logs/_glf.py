import pickle
d=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
s=d["supply"]; m=s[s.carrier=="methane"]
for y in [2030,2040,2050]:
    sub=m[m.year==y]
    be=sub[sub.region.str.startswith("BEC")]["energy"].sum()
    nl=sub[sub.region.str.startswith("NLC")]["energy"].sum()
    print(f"{y}: BE {be:10.1f} ({be/244221.4:5.1%} of BE LNG cap)   NL {nl:10.1f} ({nl/(313995+103859.0):5.1%} of NL cap)")
print()
print("Per-region 2050 vs its own cap (LF):")
import collections
caps={"BEC":3.4844*8760,"NLC":(3.9829+1.3174)*8760}
sub=m[m.year==2050].groupby("region")["energy"].sum()
for r,v in sub.items():
    c=caps["BEC" if r.startswith("BEC") else "NLC"]
    print(f"  {r} {v:10.1f} / {c:10.1f} = LF {v/c:6.2%}")
