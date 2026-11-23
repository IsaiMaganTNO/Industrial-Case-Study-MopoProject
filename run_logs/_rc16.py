import sqlite3, os, re
base=r".spinetoolbox\items"
T=("DE","DK","NO","UK")
for d in ["power_db","vre_db","rdemand_db","gas_db"]:
    p=os.path.join(base,d,d+".sqlite")
    c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
    rows=[r[0] for r in c.execute("SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name='region'")]
    tot=c.execute("SELECT count(*) FROM entity").fetchone()[0]
    pv=c.execute("SELECT count(*) FROM parameter_value").fetchone()[0]
    c.close()
    ic=[r for r in rows if re.match(r"^(BEC|NLC)\d$",r)]
    tg=[r for r in rows if r in T]
    oth=[r for r in rows if r not in ic and r not in tg]
    print("%-12s regions=%-4d IC1=%-3d targets=%-22s other=%-3d entities=%-6d pvals=%d"%(
        d,len(rows),len(ic),str(sorted(tg)),len(oth),tot,pv))
    if oth[:6]: print("              other sample:",sorted(oth)[:6])
