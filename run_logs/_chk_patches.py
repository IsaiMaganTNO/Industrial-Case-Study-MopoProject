import sqlite3,sys
db=r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.sqlite"
c=sqlite3.connect(db)
q=lambda s,p=():c.execute(s,p).fetchall()
def pv(like_ent=None,pname=None,limit=20):
    s="""SELECT pd.name, e.name, typeof(pv.value), substr(cast(pv.value as text),1,60)
         FROM parameter_value pv
         JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
         JOIN entity e ON e.id=pv.entity_id WHERE 1=1"""
    a=[]
    if pname: s+=" AND pd.name=?"; a.append(pname)
    if like_ent: s+=" AND e.name LIKE ?"; a.append(like_ent)
    return q(s+" LIMIT %d"%limit,tuple(a))
print("== atmosphere params ==")
for r in pv(like_ent="%atmosphere%",limit=200):
    if r[0] in ("storage_state_max","storage_investment_count_max_cumulative",
                "has_state","storage_active","node_state_cap"):
        print(r)
