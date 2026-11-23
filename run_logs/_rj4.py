import sqlite3,json
def probe(p,lab):
    c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
    r=c.execute("""SELECT e.name,pv.value FROM parameter_value pv
     JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id JOIN entity e ON e.id=pv.entity_id
     WHERE pd.name='flow_profile' LIMIT 1""").fetchone()
    c.close()
    d=json.loads(r[1].decode())
    print("==",lab,r[0])
    print("   index_name:",d.get("index_name"),"index_type:",d.get("index_type"))
    data=d["data"]
    ks=list(data.keys()) if isinstance(data,dict) else [t[0] for t in data]
    print("   n keys:",len(ks)," first:",ks[:3]," last:",ks[-2:])
    v0=data[ks[0]] if isinstance(data,dict) else data[0][1]
    print("   nested type:",type(v0).__name__, str(v0)[:160])
probe(r"EU_case\.spinetoolbox\items\heat_db\heat_db.sqlite","EU heat")
probe(r".spinetoolbox\items\heat_db\heat_db.sqlite","IC1 heat")
