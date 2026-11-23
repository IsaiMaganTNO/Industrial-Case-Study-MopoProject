import sqlite3, glob
db = glob.glob(r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\*.sqlite")[0]
c = sqlite3.connect(db); q = lambda s, *a: c.execute(s, a).fetchall()
o = open(r"run_logs\_inj_chk2.out", "w", encoding="utf8"); P = lambda *a: print(*a, file=o)
for n, pd_, al, v in q("select e.name, pd.name, a.name, substr(pv.value,1,200) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id join entity e on e.id=pv.entity_id where e.name like '%CO2-injection-NSUK011_UK%' or e.name like '%CO2-injection-NSNL012_NLC1%' or (e.name like '%((COEL)MeOH)O-MEA_NLC5%')"):
    P(n, pd_, al, v)
# how many CO2 pipelines cross borders, and what connections touch atmosphere
P("conn x atm", q("select count(*) from entity e join entity_class ec on ec.id=e.class_id where ec.name like 'connection%' and e.name like '%atmos%'"))
P("co2 connections", [r[0] for r in q("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='connection' and e.name like '%CO2%'")][:80])
o.close()
