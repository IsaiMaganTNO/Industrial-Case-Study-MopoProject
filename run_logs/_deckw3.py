import sys
sys.path.insert(0,"presentation"); sys.path.insert(0,"analysis_v2")
import pandas as pd
import model as M, spine_io as sio
rc=sio.connect(r"..\checkpoints\Investment_Results.3day_vre15.sqlite")
ic=sio.connect(r"..\checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite")
y2m,rw=M.temporal_structure(ic)
uf=M.unit_flows(rc,y2m,rw)
print("cols:",list(uf.columns))
yc=[c for c in uf.columns if c in ("year","period","milestone_year")][0]
e=uf[(uf.node.astype(str).str.startswith("elec_"))&(uf.direction=="to_node")]
g=e.groupby([e.unit.map(M.tech_of),e[yc]]).value_annual.sum().unstack(fill_value=0)/1e3
last=g.columns[-1]
print(f"\n{last} top elec sources (TWh):")
print(g[last].sort_values(ascending=False).head(12).round(1).to_string())
print("TOTAL:",round(g[last].sum(),1))
