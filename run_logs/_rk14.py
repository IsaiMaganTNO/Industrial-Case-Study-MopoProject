import sqlite3,collections,hashlib,os,re,yaml
DBS=["heat_db","transport_db","industry_db","other_industry_db","hydro_db"]
print("### P1 regions + malformed-composite audit")
for d in DBS:
    p=r".spinetoolbox\items\%s\%s.sqlite"%(d,d)
    c=sqlite3.connect(p); cur=c.cursor()
    cls={r[0]:r[1] for r in cur.execute("SELECT id,name FROM entity_class")}
    dims=collections.Counter()
    for ecid,did,pos in cur.execute("SELECT entity_class_id,dimension_id,position FROM entity_class_dimension"):
        dims[ecid]+=1
    ents=cur.execute("SELECT id,class_id,name FROM entity").fetchall()
    ec=collections.Counter(r[0] for r in cur.execute("SELECT entity_id FROM entity_element").fetchall())
    regs=sorted(n for _,cid,n in ents if cls[cid]=="region")
    bad=[(n,cls[cid],ec.get(e,0),dims.get(cid,0)) for e,cid,n in ents if dims.get(cid,0) and ec.get(e,0)!=dims[cid]]
    print("  %-18s regions=%-3d  malformed=%d"%(d,len(regs),len(bad)))
    if bad: print("      ",bad[:5])
    c.close()
print("\n### P3 no new classes/paramdefs vs backup")
for d in DBS:
    a=sqlite3.connect(r"backups\sector-dbs-pre-eumerge\%s.sqlite"%d)
    b=sqlite3.connect(r".spinetoolbox\items\%s\%s.sqlite"%(d,d))
    ca=set(r[0] for r in a.execute("SELECT name FROM entity_class")); cb=set(r[0] for r in b.execute("SELECT name FROM entity_class"))
    pa=set(r[0] for r in a.execute("SELECT name FROM parameter_definition")); pb=set(r[0] for r in b.execute("SELECT name FROM parameter_definition"))
    print("  %-18s new_classes=%s new_pdefs=%s"%(d,sorted(cb-ca) or "-",sorted(pb-pa) or "-"))
    a.close(); b.close()
print("\n### P2 BE/NL values unchanged")
ic1=re.compile(r"(BEC\d|NLC\d)")
for d in DBS:
    def grab(p):
        c=sqlite3.connect(p); 
        q="""SELECT pd.name,e.name,a.name,pv.value FROM parameter_value pv
         JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
         JOIN entity e ON e.id=pv.entity_id JOIN alternative a ON a.id=pv.alternative_id"""
        r={(x[0],x[1],x[2]):hashlib.md5(x[3] or b"").hexdigest() for x in c.execute(q) if ic1.search(x[1])}
        c.close(); return r
    A=grab(r"backups\sector-dbs-pre-eumerge\%s.sqlite"%d); B=grab(r".spinetoolbox\items\%s\%s.sqlite"%(d,d))
    diff=[k for k in set(A)&set(B) if A[k]!=B[k]]
    print("  %-18s before=%-5d after=%-5d lost=%-3d added=%-3d CHANGED=%d"%(d,len(A),len(B),len(set(A)-set(B)),len(set(B)-set(A)),len(diff)))
print("\n### P5 technology names vs userconfig")
cfg=yaml.safe_load(open(r"data-pipelines\europe\userconfig.yaml",encoding="utf-8"))
for d in DBS:
    c=sqlite3.connect(r".spinetoolbox\items\%s\%s.sqlite"%(d,d))
    for cl,key in [("technology","technology"),("vehicle","vehicle"),("end-use","end-use")]:
        ns=[r[0] for r in c.execute("SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name=?",(cl,))]
        miss=[n for n in ns if n not in cfg.get(key,{})]
        if ns: print("  %-18s %-10s n=%-4d missing_from_config=%s"%(d,cl,len(ns),miss or "-"))
    c.close()
