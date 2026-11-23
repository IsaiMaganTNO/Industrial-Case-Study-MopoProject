import sqlite3, re, json
def grab(p):
    c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
    q="""SELECT pd.name,e.name,a.name,pv.value FROM parameter_value pv
         JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
         JOIN entity e ON e.id=pv.entity_id JOIN alternative a ON a.id=pv.alternative_id"""
    d={(x[0],x[1],x[2]):x[3] for x in c.execute(q)}
    c.close(); return d
old=grab(r"backups\spinetoolbox-items-pre-mixedres\items\ines_db\ines_db.sqlite")
new=grab(r".spinetoolbox\items\ines_db\ines_db.sqlite")
ic1=re.compile(r"(BEC\d|NLC\d)(_|$)")
diff=[k for k in (set(old)&set(new)) if ic1.search(k[1]) and old[k]!=new[k]]
def vals(b):
    try:
        d=json.loads(b.decode())
        if isinstance(d,dict) and "data" in d:
            x=d["data"]
            return list(x.values()) if isinstance(x,dict) else [v for _,v in x]
    except Exception: pass
    return None
worst=[]
for k in diff:
    a,b=vals(old[k]),vals(new[k])
    if not a or not b or len(a)!=len(b): worst.append((999,k,"SHAPE")); continue
    try:
        rel=max(abs(y-x)/max(abs(x),1e-9) for x,y in zip(a,b) if isinstance(x,(int,float)) and isinstance(y,(int,float)))
    except ValueError: continue
    worst.append((rel,k,""))
worst.sort(reverse=True)
print("max relative change per differing value - top 15:")
for r,k,note in worst[:15]:
    print("   %9.3e  %-24s %s %s"%(r,k[0],k[1][:46],note))
import statistics
rs=[r for r,_,n in worst if n!="SHAPE"]
print("\nn=%d  median rel change=%.2e  95th=%.2e  max=%.2e"%(len(rs),statistics.median(rs),sorted(rs)[int(.95*len(rs))],max(rs)))
print("shape changes:",sum(1 for _,_,n in worst if n=="SHAPE"))
