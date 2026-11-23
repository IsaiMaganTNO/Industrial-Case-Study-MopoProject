import sqlite3, json, statistics
c=sqlite3.connect(r"reports_3day_group1\INPUT_Final_SpineOpt_Model.tiny.3day.group1.sqlite")
def get(ent,par):
    q="""SELECT pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
         JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
         WHERE e.name=? AND pd.name=? AND pv.alternative_id=1"""
    r=c.execute(q,(ent,par)).fetchone()
    if not r: return None
    v=r[0].decode() if isinstance(r[0],bytes) else r[0]
    try: return json.loads(v)
    except Exception: return v
for u in ("bioST_NLC6","wind-on-SP277-HH100_NLC6","wind-off-FB-SP370-HH155_NSNL011","solar-PV-no-tracking_NLC6"):
    ic=get(u,"unit_investment_cost")
    fom=get(u,"fom_cost"); life=get(u,"lifetime_economic")
    d=ic.get("data",{}) if isinstance(ic,dict) else {}
    print(f"{u:34s} life={life.get('data') if isinstance(life,dict) else life}")
    print(f"    capex: "+"  ".join(f"{k[:4]}={float(v):,.0f}" for k,v in list(d.items())[:4]))
    print(f"    fom  : {fom}")
