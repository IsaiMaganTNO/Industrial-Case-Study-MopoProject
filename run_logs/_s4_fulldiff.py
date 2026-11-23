import sqlite3,glob,re,collections
A=glob.glob(r"final_runs_pessimistic_ccs\3_*\input\*.sqlite")[0]; B=r"share_frlu_xpress\input.sqlite"
FRLU=re.compile(r"(^|[_\W])(FR|LU)($|[_\W])")
def load(db):
    c=sqlite3.connect(db)
    ent={r[0]:(r[1],r[2]) for r in c.execute("select e.id,ec.name,e.name from entity e join entity_class ec on ec.id=e.class_id")}
    pv={}
    for cls,en,p,a,v in c.execute("""select ec.name,e.name,pd.name,a.name,pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
        join entity e on e.id=pv.entity_id join entity_class ec on ec.id=e.class_id join alternative a on a.id=pv.alternative_id"""):
        pv[(cls,en,p,a)]=v
    sc=c.execute("select s.name,a.name,sa.rank from scenario s join scenario_alternative sa on sa.scenario_id=s.id join alternative a on a.id=sa.alternative_id").fetchall()
    ea={(r[0],r[1],r[2]):r[3] for r in c.execute("select ec.name,e.name,a.name,ea.active from entity_alternative ea join entity e on e.id=ea.entity_id join entity_class ec on ec.id=e.class_id join alternative a on a.id=ea.alternative_id")}
    return set(ent.values()),pv,sorted(sc),ea
ea_,pa,sa,eaa=load(A); eb,pb,sb,eab=load(B)
keep=lambda n: not FRLU.search(n)
o=open(r"run_logs\_s4_fulldiff.out","w")
onlyA=sorted(x for x in ea_-eb if keep(x[1])); onlyB=sorted(x for x in eb-ea_ if keep(x[1]))
print("entities only in MR:",len(onlyA),"only in S4:",len(onlyB),file=o)
for x in onlyA: print("  -MR",x,file=o)
for x in onlyB: print("  +S4",x,file=o)
cnt=collections.Counter(); 
for k in sorted(set(pa)|set(pb)):
    if not keep(k[1]): continue
    if pa.get(k)!=pb.get(k):
        tag="onlyMR" if k not in pb else "onlyS4" if k not in pa else "diff"
        cnt[(tag,k[0],k[2])]+=1
        print(tag,k,str(pa.get(k))[:120],"|",str(pb.get(k))[:120],file=o)
print("scen same:",sa==sb,file=o)
d=[(k,eaa.get(k),eab.get(k)) for k in set(eaa)|set(eab) if keep(k[1]) and eaa.get(k)!=eab.get(k)]; print("entity_alternative diffs",len(d),d[:10],file=o)
o.close()
for k,v in sorted(cnt.items(),key=lambda x:-x[1]): print(v,k)
print("entities only MR",len(onlyA),"only S4",len(onlyB))
