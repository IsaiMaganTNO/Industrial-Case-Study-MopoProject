import pandas as pd, pickle, sqlite3, glob
for k in ["IC1", "MR"]:
    df = pd.read_pickle(rf"run_logs\_flows2050_{k}.pkl"); nb = df.cn.isin(["NL", "BE"])
    b = df[(df.kind == "connection_flow") & (df.node == "bio")]
    print(k, "bio connections into NL+BE regions (to_node):", b[nb & (b.dir == "to_node")].groupby("obj").v.sum().div(1e3).round(1).loc[lambda s: s > .1].to_dict())
    u = df[(df.kind == "unit_flow") & (df.node == "bio") & (df.dir == "from_node") & nb]
    print(k, "bio users NL+BE:", u.groupby(u.obj.str.replace(r"_(NLC\d|BEC\d)$", "", regex=True)).v.sum().div(1e3).round(1).to_dict())
    a = df[df.obj.str.contains("aviation") & (df.dir == "to_node")]
    print(k, "aviation NL / BE:", a[nb].groupby([a.cn, a.node]).v.sum().div(1e3).round(1).to_dict())
    e = pickle.load(open(rf"run_logs\{dict(IC1='nb_ccslow_ccu_cap16_dac0', MR='mr_ccslow_ccu_cap16_dac0')[k]}_NLBE.pkl", "rb"))["emis"].query("year==2050")
    print(k, "emissions by tech (top):", e.groupby("tech").co2.sum().div(1e3).round(1).sort_values().iloc[[0, 1, 2, -4, -3, -2, -1]].to_dict())
    print(k, "HC-related emis:", e[e.tech.str.contains("HC|aviation|REF", regex=True)].groupby("tech").co2.sum().div(1e3).round(2).to_dict())
db = glob.glob(r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\input\*.sqlite")[0]; c = sqlite3.connect(db)
for r in c.execute("""select e.name, pd.name, substr(pv.value,1,120) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id
 where e.name in ('biomass-stock_NLC3','biomass-stock_BEC2') or (e.name like 'HC_NLC5__int-aviation%') or e.name like '%atmosphere%int-aviation%' or (e.name like 'HC%atmosphere%')""").fetchall()[:30]: print(r)
