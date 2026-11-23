import pickle, sqlite3, pandas as pd
pd.set_option("display.width",108)
A=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
b=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite")
old={r[0] for r in b.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='connection'")}
cp=B["co2pipe"]; cp=cp[cp["year"].astype(str).str.contains("2050")]
cp=cp.groupby("connection")["co2"].sum().sort_values(ascending=False)
cp=cp[cp.abs()>1e-6]
new=cp[[c not in old for c in cp.index]]
print(f"P6: CO2 pipeline edges with 2050 flow: {len(cp)}  of which NEWLY CREATED: {len(new)}")
print("\ntop NEW (reversed) edges by 2050 flow:")
print(new.head(12).round(1).to_string())
print(f"\ntotal flow on new edges = {new.sum():,.1f}")
print()
for tag,D in [("BASELINE",A),("BIDIR   ",B)]:
    n=D["co2net"]; n=n[n["year"].astype(str).str.contains("2050")]
    cap=n[n["role"].astype(str)=="captured"]
    dac=cap[cap["tech"].astype(str).str.contains("DAC",case=False,na=False)]["co2"].sum()
    print(f"{tag}: 2050 total captured={cap['co2'].sum():,.1f}  DAC={dac:,.1f}")
