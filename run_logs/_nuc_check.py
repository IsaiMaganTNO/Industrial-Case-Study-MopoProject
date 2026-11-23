import sqlite3
o = open(r"run_logs\_nuc_check.out", "w", encoding="utf8")
db = r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"
c = sqlite3.connect(db)
rows = c.execute("""select e.name, a.name from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id join alternative a on a.id=pv.alternative_id
 where e.name like 'nuclear-3\\_%' escape '\\' and pd.name='investment_count_total_max_cumulative'""").fetchall()
print("caps:", rows, file=o)
print("links:", c.execute("select count(*) from entity e join entity_class ec on ec.id=e.class_id where ec.name='unit__investment_group' and e.name like '%nuclear-3%'").fetchone(), file=o)
print("DONE", file=o); o.close()
