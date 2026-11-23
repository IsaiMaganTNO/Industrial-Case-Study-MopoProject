import sqlite3
B=r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"
N=r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0_v3\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v3.sqlite"
def ex(db):
    c=sqlite3.connect(db)
    return {r[0] for r in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='unit' and e.name like '%-existing%' and (e.name like '%NLC%' or e.name like '%BEC%')")}
b,n=ex(B),ex(N)
print("existing NL/BE units: base",len(b),"frlu",len(n))
print("missing in FRLU:",sorted(b-n))
print("extra in FRLU:",sorted(n-b))
