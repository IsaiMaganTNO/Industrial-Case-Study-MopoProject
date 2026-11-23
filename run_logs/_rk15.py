import sqlite3,yaml
cfg=yaml.safe_load(open(r"data-pipelines\europe\userconfig.yaml",encoding="utf-8"))
for d in ["heat_db","industry_db","other_industry_db","hydro_db"]:
    a=sqlite3.connect(r"backups\sector-dbs-pre-eumerge\%s.sqlite"%d)
    b=sqlite3.connect(r".spinetoolbox\items\%s\%s.sqlite"%(d,d))
    qa=set(r[0] for r in a.execute("SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name='technology'"))
    qb=set(r[0] for r in b.execute("SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name='technology'"))
    newnames=sorted(qb-qa)
    miss_pre=sorted(n for n in qa if n not in cfg.get("technology",{}))
    miss_new=sorted(n for n in newnames if n not in cfg.get("technology",{}))
    print("%-18s tech before=%-3d after=%-3d NEW=%s"%(d,len(qa),len(qb),newnames or "-"))
    print("     missing-from-config PRE-EXISTING=%d  INTRODUCED-BY-MERGE=%s"%(len(miss_pre),miss_new or "-"))
    print("     wood names now:",sorted(n for n in qb if "wood" in n))
    a.close(); b.close()
