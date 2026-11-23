import pandas as pd, os, re
B=r"verification\Data - IC1 and PECD1"
T={"NO","DE","DK","UK"}
SCOPE=T|{"BE","NL"}
et=pd.read_csv(os.path.join(B,"Electricity_Transmission","Electricity_Transmission.csv"))
et["f"]=et.From_node.astype(str).str.strip(); et["t"]=et.To_node.astype(str).str.strip()
def ctry(x): return x[:2] if re.fullmatch(r"(BE|NL)C\d",x) else x
et["fc"]=et.f.map(ctry); et["tc"]=et.t.map(ctry)
ins=et[et.fc.isin(SCOPE)&et.tc.isin(SCOPE)]
print(f"transmission links fully inside scope: {len(ins)} of {len(et)}")
print("\ncross-border pairs in scope (country level):")
cb=ins[ins.fc!=ins.tc]
print(cb.groupby(["fc","tc"]).size().to_string())
print("\nlinks with exactly one end in scope (would need a boundary):",
      len(et[(et.fc.isin(SCOPE))^(et.tc.isin(SCOPE))]))
out=sorted(set(et[(et.fc.isin(SCOPE))^(et.tc.isin(SCOPE))][["fc","tc"]].values.ravel())-SCOPE)
print("  external neighbours touched:",out)
