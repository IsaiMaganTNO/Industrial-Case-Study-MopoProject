import sqlite3, re, json, collections, statistics
def grab(p):
    c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
    q="""SELECT pd.name,e.name,a.name,pv.value,pv.type FROM parameter_value pv
         JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
         JOIN entity e ON e.id=pv.entity_id JOIN alternative a ON a.id=pv.alternative_id"""
    d={(x[0],x[1],x[2]):(x[3],x[4]) for x in c.execute(q)}
    c.close(); return d
old=grab(r"backups\spinetoolbox-items-pre-mixedres\items\ines_db\ines_db.sqlite")
new=grab(r".spinetoolbox\items\ines_db\ines_db.sqlite")
ic1=re.compile(r"(BEC\d|NLC\d)(_|$)")
diff=[k for k in (set(old)&set(new)) if ic1.search(k[1]) and old[k][0]!=new[k][0]]
def vals(b):
    try:
        d=json.loads(b.decode())
    except Exception:
        return None
    if isinstance(d,(int,float)): return [float(d)]
    if isinstance(d,dict) and "data" in d:
        x=d["data"]
        v=list(x.values()) if isinstance(x,dict) else [t[-1] for t in x]
        return [float(y) for y in v if isinstance(y,(int,float))]
    return None
rows=[]; unparsed=[]
for k in diff:
    a,b=vals(old[k][0]),vals(new[k][0])
    if a is None or b is None or len(a)!=len(b) or not a:
        unparsed.append((k,old[k],new[k])); continue
    rel=max(abs(y-x)/max(abs(x),1e-9) for x,y in zip(a,b))
    rows.append((rel,k,a[:2],b[:2]))
rows.sort(reverse=True)
rs=[r for r,_,_,_ in rows]
print("parsed n=%d  median=%.2e 90th=%.2e max=%.2e"%(len(rs),statistics.median(rs),sorted(rs)[int(.9*len(rs))],max(rs)))
print("unparsable/len-mismatch:",len(unparsed))
for k,o,n in unparsed[:10]: print("   ",k[0],k[1][:50],o[1],o[0][:60],"->",n[0][:60])
print("\n--- top 25 by rel change")
for r,k,a,b in rows[:25]: print("  %8.3e %-26s %-50s %s -> %s"%(r,k[0],k[1][:50],a,b))
print("\n--- counts by param among rel>0.01")
print(collections.Counter(k[0] for r,k,_,_ in rows if r>0.01))
print("--- counts by param among rel<=0.01")
print(collections.Counter(k[0] for r,k,_,_ in rows if r<=0.01))
