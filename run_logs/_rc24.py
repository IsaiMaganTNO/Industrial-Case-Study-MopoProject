import sqlite3, re
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
ko={k for k in old if ic1.search(k[1])}
kn={k for k in new if ic1.search(k[1])}
print("BE/NL-keyed parameter values: baseline=%d new=%d"%(len(ko),len(kn)))
print("  lost:",len(ko-kn),"  added:",len(kn-ko))
shared=ko&kn
diff=[k for k in shared if old[k]!=new[k]]
print("  shared=%d  DIFFERING=%d"%(len(shared),len(diff)))
import collections
if diff:
    print("  differing by parameter:",collections.Counter(k[0] for k in diff).most_common(10))
    for k in diff[:5]: print("     ",k[0],"|",k[1])
