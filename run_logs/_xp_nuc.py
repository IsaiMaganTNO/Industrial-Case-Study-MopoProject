import sqlite3, json
N = r"xpress_server\Investment_Results.3day_mr_frlu_ccslow_ccu_cap16_dac0.v3.xpress.sqlite"
M = r"xpress_server\Investment_Results.3day_mr_frlu_ccslow_ccu_cap16_dac0.v3.xpress.sqlite"
c = sqlite3.connect(N)
print("== results: nuclear units")
for e, t in c.execute("""select e.name, cast(pv.value as text) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id where pd.name='units_invested_available' and e.name like '%nuclear%'"""):
    d = json.loads(t)["data"]; print(" ", e.split("__")[1], {k[:4]: round(v, 2) for k, v in d.items()})
m = sqlite3.connect(M)
print("== model: FR nuclear entities + params")
for e, p, a, t in m.execute("""select e.name, pd.name, a.name, substr(cast(pv.value as text),1,120) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id join alternative a on a.id=pv.alternative_id
  where e.name like 'nuclear%FR' or e.name like 'nuclear%DE' or e.name like 'nuclear%UK' order by e.name, pd.name"""):
    if p in ("existing_units","initial_units_invested_available","unit_capacity","number_of_units","candidate_units","unit_investment_count_max_cumulative","units_invested_available_fix"): print(" ", e, p, a, t)

