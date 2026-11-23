import re,pandas as pd
u=pd.read_pickle(r"run_logs\_use_elec_h2_all.pkl"); u=u[u.year==2050]
def cat(t,car):
    if re.match(r"^PEM|^SOEC|^AEC|electroly",t): return "Electrolysis"
    if re.search(r"heatpump|electric-heating|electric-boiler",t): return "Heat pumps / e-heating (buildings)"
    if re.search(r"storage|battery|pumped|H2-tank|salt",t): return "Storage"
    if re.match(r"^CCGT-H2|^OCGT-H2|fuel-?cell",t): return "Power generation"
    if re.match(r"^REF",t): return "Refineries"
    if re.search(r"DAC|CO2-|compress|LH2|liquef|pipeline|terminal",t): return "Infrastructure"
    return "Industry"
u["cat"]=[cat(t,c) for t,c in zip(u.tech,u.carrier)]
print(u.groupby(["carrier","cat","run"]).twh.sum().unstack().round(1))
for car in ("elec","H2"):
  print("==",car); print(u[(u.carrier==car)&(u.cat!="Industry")].groupby("tech").twh.sum().round(1).loc[lambda s:s.abs()>.5].to_string())
  print("--industry top"); print(u[(u.carrier==car)&(u.cat=="Industry")].groupby("tech").twh.sum().round(1).sort_values().tail(25).to_string())
