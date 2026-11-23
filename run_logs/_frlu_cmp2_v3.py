import sqlite3, json
B = r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"
N = r"checkpoints\\frlu\\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v3.sqlite"
def v(db, ent, par):
    r = sqlite3.connect(db).execute("""select e.name,a.name,cast(pv.value as text) from parameter_value pv join entity e on e.id=pv.entity_id
     join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id
     where e.name like ? and pd.name=? order by e.name limit 3""", (ent, par)).fetchall()
    return [(e, a, t[:90]) for e, a, t in r]
for ent, par in [("LNG-terminal_%","availability_factor"),("gas-extraction_NL%","availability_factor"),("DAC%","investment_count_max_cumulative"),("DAC%","existing_units"),("nuclear-3_BE","unit_investment_count_max_cumulative")]:
    print("##", ent, par)
    for tag, db in (("BASE",B),("FRLU",N)):
        for r in v(db, ent, par): print("  ", tag, r)
for tag, db in (("BASE",B),("FRLU",N)):
    c = sqlite3.connect(db)
    print(tag, "rows w/ 2040-01-01:", c.execute("select count(*) from parameter_value where cast(value as text) like '%2040-01-01%'").fetchone()[0])

