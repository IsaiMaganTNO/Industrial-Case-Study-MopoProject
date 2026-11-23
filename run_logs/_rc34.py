import sqlite3, re, json, statistics
def grab(p):
    c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
    q="""SELECT pd.name,e.name,a.name,pv.value FROM parameter_value pv
         JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
         JOIN entity e ON e.id=pv.entity_id JOIN alternative a ON a.id=pv.alternative_id
         WHERE pd.name IN ('flow_profile','profile_limit_upper')"""
    d={(x[0],x[1],x[2]):x[3] for x in c.execute(q)}
    c.close(); return d
old=grab(r"backups\spinetoolbox-items-pre-mixedres\items\ines_db\ines_db.sqlite")
new=grab(r".spinetoolbox\items\ines_db\ines_db.sqlite")
ic1=re.compile(r"(BEC\d|NLC\d)(_|$)")
def vals(b):
    d=json.loads(b.decode())
    if isinstance(d,(int,float)): return [float(d)]
    x=d["data"]; v=list(x.values()) if isinstance(x,dict) else [t[-1] for t in x]
    return [float(y) for y in v]
for pn in ("flow_profile","profile_limit_upper"):
    ks=[k for k in set(old)&set(new) if k[0]==pn and ic1.search(k[1]) and old[k]!=new[k]]
    print("==",pn,"differing:",len(ks))
    allrel=[]
    for k in ks[:5]+[]:
        pass
    for k in ks:
        a,b=vals(old[k]),vals(new[k])
        if len(a)!=len(b): print("  LEN",k, len(a),len(b)); continue
        allrel+= [abs(y-x)/max(abs(x),1e-9) for x,y in zip(a,b)]
        sa,sb=sum(a),sum(b)
        if k is ks[0]: print("   example",k[1],"n=",len(a),"sum %.6f -> %.6f"%(sa,sb))
    if allrel:
        allrel.sort()
        print("   pointwise n=%d median=%.2e p99=%.2e max=%.2e"%(len(allrel),statistics.median(allrel),allrel[int(.99*len(allrel))],allrel[-1]))
