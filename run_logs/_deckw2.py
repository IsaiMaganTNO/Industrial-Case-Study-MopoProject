import sys
sys.path.insert(0,"presentation"); sys.path.insert(0,"analysis_v2")
import pandas as pd
import model as M, spine_io as sio
res=r"..\checkpoints\Investment_Results.3day_vre15.sqlite"
inp=r"..\checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite"
rc=sio.connect(res); ic=sio.connect(inp)
y2m,rw=M.temporal_structure(ic)
print("rep weights:",{str(k)[:10]:round(v,2) for k,v in rw.items()})
print("annual weight:",M.annual_weight(rw,y2m))
uf=M.unit_flows(rc,y2m,rw)
e=uf[(uf.node.astype(str).str.startswith("elec_"))&(uf.direction=="to_node")]
g=e.groupby([e.unit.map(M.tech_of),"milestone"]).value_annual.sum().unstack(fill_value=0)/1e3
print("\n2050 top elec sources (TWh):")
print(g[2050].sort_values(ascending=False).head(12).round(1).to_string())
print("TOTAL 2050:",round(g[2050].sum(),1))
