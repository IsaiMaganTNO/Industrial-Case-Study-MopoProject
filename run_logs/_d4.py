import pandas as pd, os, re
B=r"verification\Data - IC1 and PECD1"
NB={"BE","NL"}
def cls(vals):
    v=[str(x).strip() for x in vals if str(x).strip() not in ("nan","None","")]
    return ({x for x in v if re.fullmatch(r"(BE|NL)C\d",x)},
            {x for x in v if re.fullmatch(r"[A-Z]{2}",x)},
            {x for x in v if re.fullmatch(r"[A-Z]{2}\d{2}",x)},
            {x for x in v if re.fullmatch(r"[A-Z]{2}\d{3}",x)})
def show(tag,vals):
    ic1,p1,p2,n3=cls(vals)
    print(f"  {tag[:46]:48} IC1={len(ic1):3} PECD1={len(p1):3} PECD2={len(p2):4} NUTS3={len(n3):4}"
          f"  nonBENL_P1={len(p1-NB)}")
print("=== Electricity transmission ===")
d=pd.read_csv(os.path.join(B,"Electricity_Transmission","Electricity_Transmission.csv"))
print("  cols:",list(d.columns)[:10],"rows",len(d))
print(d.head(3).to_string()[:400])
for c in d.columns[:4]: show("  col:"+c, d[c])
print("\n=== Commodities ===")
d=pd.read_csv(os.path.join(B,"Commodities","commodity_data.csv"))
print("  cols:",list(d.columns),"rows",len(d)); print(d.head(5).to_string()[:400])
print("\n=== Cargo ===")
d=pd.read_csv(os.path.join(B,"Cargo","cargo_network.csv"))
print("  cols:",list(d.columns),"rows",len(d)); print(d.head(3).to_string()[:300])
for c in d.columns[:3]: show("  col:"+c, d[c])
