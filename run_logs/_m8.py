import pandas as pd, os, re
B=r"verification\Data - IC1 and PECD1"
et=pd.read_csv(os.path.join(B,"Electricity_Transmission","Electricity_Transmission.csv"))
et["f"]=et.From_node.astype(str).str.strip(); et["t"]=et.To_node.astype(str).str.strip()
def c(x): return x[:2] if re.fullmatch(r"(BE|NL)C\d",x) else x
et["fc"]=et.f.map(c); et["tc"]=et.t.map(c)
SCOPE={"NO","DE","DK","UK","BE","NL"}
cut=et[((et.fc.isin(SCOPE))^(et.tc.isin(SCOPE)))]
cap=cut.groupby(cut.apply(lambda r: r.tc if r.fc in SCOPE else r.fc,axis=1))["Capacity (MW)"].agg(["sum","count"])
print("=== severed interconnection by external country (MW) ===")
print(cap.sort_values("sum",ascending=False).to_string())
tot_in=et[et.fc.isin(SCOPE)&et.tc.isin(SCOPE)&(et.fc!=et.tc)]["Capacity (MW)"].sum()
print(f"\nin-scope cross-border capacity: {tot_in:,.0f} MW")
print(f"severed capacity:               {cap['sum'].sum():,.0f} MW")
print(f"severed share: {cap['sum'].sum()/(tot_in+cap['sum'].sum()):.1%}")
