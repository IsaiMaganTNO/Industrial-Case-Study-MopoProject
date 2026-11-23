import sqlite3, glob, pickle, pandas as pd
db = glob.glob(r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\input\*.sqlite")[0]; c = sqlite3.connect(db)
q = """select e.name, pd.name, pv.type, substr(pv.value,1,160) from parameter_value pv join entity e on e.id=pv.entity_id
join parameter_definition pd on pd.id=pv.parameter_definition_id where {}"""
print("== LH2 / LNG terminal params")
for r in c.execute(q.format("(e.name like 'LH2-terminal%' or e.name like 'LNG-terminal%') and pd.name in ('investment_count_max_cumulative','investment_count_initial_cumulative','unit_capacity','capacity_per_unit','fuel_cost','vom_cost','unit_investment_cost','commodity_price','candidate_units','initial_units_invested_available','number_of_units','unit_availability_factor')")): print(r)
print("== commodity/hydrogen price nodes")
for r in c.execute(q.format("(e.name like '%LH2%' or e.name like 'H2-import%' or e.name like '%hydrogen-import%') and pd.name not like '%ratio%'")).fetchall()[:25]: print(r)
print("== biomass potential")
for r in c.execute(q.format("(e.name like 'bio%' or e.name like '%biomass%') and (pd.name like '%cumulative%' or pd.name like '%max%' or pd.name like '%potential%' or pd.name like '%demand%' or pd.name like '%state_cap%' or pd.name like '%availability%')")).fetchall()[:40]: print(r)
print("== aviation / kerosene entities")
print([r[0] for r in c.execute("select name from entity where name like '%kero%' or name like '%aviat%' or name like '%jet%' or name like '%FT%' limit 30")])
D = pickle.load(open(r"run_logs\nb_ccslow_ccu_cap16_dac0_NLBE.pkl","rb"))
print(D["fleet"].query("tech=='LH2-terminal'").groupby(["year","region"]).units.sum())
