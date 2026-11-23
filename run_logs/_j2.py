import sqlite3, json, pandas as pd
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.hcco2.sqlite"
c=sqlite3.connect(db)
def P(ent,par):
    r=c.execute("""select cast(pv.value as text) from parameter_value pv
     join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id
     where e.name=? and pd.name=?""",(ent,par)).fetchone()
    return r[0] if r else None
def ts2050(s):
    if s is None: return None
    try:
        o=json.loads(s)
        d=o.get("data",o)
        if isinstance(d,dict):
            for k,v in d.items():
                if str(k).startswith("2050"): return float(v)
        return float(s)
    except Exception:
        try: return float(s)
        except Exception: return s
for u in ("CCGT_NLC1","CCGT+CC_NLC1","OCGT_NLC1","DAC_NLC1"):
    print(f"-- {u} --")
    for p in ("unit_investment_cost","fom_cost","discount_rate_technology_specific","lifetime_economic"):
        print(f"   {p:36s} {ts2050(P(u,p))}")
    for fr in c.execute("""select e.name, cast(pv.value as text) from parameter_value pv
      join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id
      where pd.name='flow_ratio_equality_coefficient' and e.name like ?""",(u+"__%",)):
        print("   ratio:", fr[0].replace(u,"<U>"), "=", fr[1])
    v=P(u+"__elec_NLC1","vom_cost")
    print("   vom(2050):", ts2050(v))
