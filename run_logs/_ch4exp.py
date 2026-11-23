import pandas as pd
df=pd.read_pickle(r"run_logs\ch4flows.pkl")
FOR={"CH4_DE","CH4_FR","CH4_UK","CH4_LU"}
# a connection named X_CH4_Y: flow into foreign node = export
f=df[df.node.isin(FOR)]
print("=== flows at FOREIGN CH4 nodes, by direction ===")
print(f.groupby(["node","dir","year"])["val"].sum().unstack().fillna(0).round(0).to_string())
print()
print("=== net export per year (to_node at foreign = leaving NL/BE) ===")
for y in [2030,2041,2050]:
    out=f[(f.year==y)&(f["dir"]=="to_node")]["val"].sum()
    inn=f[(f.year==y)&(f["dir"]=="from_node")]["val"].sum()
    print(f"  {y}: into foreign {out/1000:9.1f} TWh   out of foreign {inn/1000:9.1f} TWh   net export {(out-inn)/1000:9.1f} TWh")
