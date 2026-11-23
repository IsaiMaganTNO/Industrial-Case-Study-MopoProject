import pandas as pd, pickle, sqlite3, glob
pd.set_option("display.width", 220)
for k in ["IC1", "CTRY", "MR"]:
    df = pd.read_pickle(rf"run_logs\_flows2050_{k}.pkl")
    print("=====", k)
    q = df[(df.kind == "unit_flow") & (df.dir == "to_node") & df.node.str.startswith("bio")]
    print("biomass supply units:", q.groupby(["obj"]).v.sum().div(1e3).round(1).loc[lambda s: s > .05].to_dict())
    q = df[df.obj.str.contains("biomass-stock")]; print("biomass-stock flows:", q.groupby(["obj", "node", "dir"]).v.sum().div(1e3).round(1).to_dict())
    q = df[df.obj.str.contains(r"\(BM|FT|kero", regex=True)]; print("FT/BM units:", q.groupby(["obj", "node", "dir"]).v.sum().div(1e3).round(1).loc[lambda s: s.abs() > .05].to_dict())
    q = df[df.node.str.contains("aviation")]; print("aviation:", q.groupby(["obj", "node", "reg", "dir"]).v.sum().div(1e3).round(2).to_dict())
    q = df[(df.node == "HC") & (df.reg == "")]; print("HC regionless:", q.groupby(["obj", "dir"]).v.sum().div(1e3).round(1).to_dict())
db = glob.glob(r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\input\*.sqlite")[0]; c = sqlite3.connect(db)
Q = """select e.name, pd.name, pv.type, substr(pv.value,1,200) from parameter_value pv join entity e on e.id=pv.entity_id
join parameter_definition pd on pd.id=pv.parameter_definition_id where {}"""
print("== biomass-stock / bio supply params")
for r in c.execute(Q.format("e.name like 'biomass-stock%' and e.name not like '%BEC%' and e.name not like '%NLC%'")): print(r)
for r in c.execute(Q.format("e.name like '%aviation%' and pd.name in ('demand','fix_ratio','node_state_cap','balance_type')")).fetchall()[:6]: print(r)
print([r[0] for r in c.execute("select name from entity where name like 'biomass-stock%' or name like '%biomass-supply%' or name like 'bio-supply%' limit 20")])
