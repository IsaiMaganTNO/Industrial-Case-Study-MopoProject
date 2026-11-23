import sqlite3, re, json, collections
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
            return (list(x.keys()),list(x.values())) if isinstance(x,dict) else ([k for k,_ in x],[v for _,v in x])
    except Exception: pass
    return None
shapes=[]
for k in diff:
    a,b=vals(old[k]),vals(new[k])
    if a is None or b is None or len(a[1])!=len(b[1]): shapes.append((k,a,b))
print("n shapes",len(shapes))
cnt=collections.Counter(k[0] for k,_,_ in shapes)
print(cnt)
for k,a,b in shapes[:6]:
    print("---",k[0],k[1][:60],k[2])
    print("  OLD keys:",(a[0] if a else None))
    print("  OLD vals:",(a[1] if a else old[k][:200]))
    print("  NEW keys:",(b[0] if b else None))
    print("  NEW vals:",(b[1] if b else new[k][:200]))
