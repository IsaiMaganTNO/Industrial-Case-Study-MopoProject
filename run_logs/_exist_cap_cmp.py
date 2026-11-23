import sqlite3, json
B=r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"
N=r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0_v3\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v3.sqlite"
q="""select e.name, cast(pv.value as text) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
 join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id
 where ec.name='unit' and pd.name='investment_count_max_cumulative' and e.name like '%-existing%' and (e.name like '%NLC%' or e.name like '%BEC%')"""
def load(db):
    out={}
    for n,t in sqlite3.connect(db).execute(q):
        d=json.loads(t); d=d.get("data",d)
        tech=n.split("-existing")[0]
        if isinstance(d,dict):
            for k,v in d.items():
                y=k[:4]
                if y in ("2030","2040","2050") and isinstance(v,(int,float)): out[(tech,y)]=out.get((tech,y),0)+v
        elif isinstance(d,(int,float)):
            for y in ("2030","2040","2050"): out[(tech,y)]=out.get((tech,y),0)+d
    return out
b,n=load(B),load(N)
keys=sorted(set(b)|set(n))
print(f"{'tech':28s}{'year':>6s}{'base GW':>10s}{'FRLU GW':>10s}")
for k in keys:
    if abs(b.get(k,0)-n.get(k,0))>0.05 and k[0] in ("nuclear-3","CCGT","SCPC","bioST","wasteST","oil-eng","OCGT"):
        print(f"{k[0]:28s}{k[1]:>6s}{b.get(k,0):10.2f}{n.get(k,0):10.2f}")
