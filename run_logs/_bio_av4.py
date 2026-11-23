import pandas as pd, pickle, sqlite3, glob, json
for k, run in [("IC1", "nb_ccslow_ccu_cap16_dac0"), ("MR", "mr_ccslow_ccu_cap16_dac0")]:
    e = pickle.load(open(rf"run_logs\{run}_NLBE.pkl", "rb"))["emis"].query("year==2050")
    print(k, "all 2050 emissions NL+BE by tech:", e.groupby("tech").co2.sum().div(1e3).round(2).loc[lambda s: s.abs() > .05].to_dict())
    df = pd.read_pickle(rf"run_logs\_flows2050_{k}.pkl")
    r = df[df.obj.str.startswith("REF-SMR-MEA") & df.cn.isin(["NL", "BE"])]
    print(k, "refinery flows:", r.groupby(["node", "dir"]).v.sum().div(1e3).round(1).to_dict())
db = glob.glob(r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\input\*.sqlite")[0]; c = sqlite3.connect(db)
tot = {}
for name, val in c.execute("""select e.name, pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id
 join alternative a on a.id=pv.alternative_id where pd.name='storage_investment_count_max_cumulative' and e.name like 'biomass-stock_%' and e.name not like '%\\_\\_%' escape '\\'"""):
    tot.setdefault(name, []).append(float(val))
print("biomass-stock max_cumulative per zone (all alternatives):", {k: [round(x, 1) for x in v] for k, v in tot.items()})
for r in c.execute("""select e.name, pd.name, substr(pv.value,1,60) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id
 where e.name like 'biomass-stock_NLC3%' and pd.name in ('storage_capacity','node_state_cap','storage_state_max','capacity_per_unit','node_state_coeff')"""): print(r)
print([r for r in c.execute("select a.name from alternative a")][:20])
