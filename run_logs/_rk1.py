import sqlite3,yaml,collections
cfg=yaml.safe_load(open(r"data-pipelines\europe\userconfig.yaml",encoding="utf-8"))
def names(p,cls):
    c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
    r=sorted(x[0] for x in c.execute("SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name=?",(cls,)))
    c.close(); return r
pairs=[("industry",r".spinetoolbox\items\industry_db\industry_db.sqlite",r"EU_case\.spinetoolbox\items\industry_db\industry_db.sqlite"),
       ("other_ind",r".spinetoolbox\items\other_industry_db\other_industry_db.sqlite",r"EU_case\.spinetoolbox\items\other_industry_db\Other_Industry_DB.sqlite"),
       ("heat",r".spinetoolbox\items\heat_db\heat_db.sqlite",r"EU_case\.spinetoolbox\items\heat_db\heat_db.sqlite"),
       ("transport",r".spinetoolbox\items\transport_db\transport_db.sqlite",r"EU_case\.spinetoolbox\items\transport_db\transport_db.sqlite")]
for lab,a,b in pairs:
    print("==========",lab)
    for cls in ["technology","vehicle","commodity","end-use"]:
        try: ia=names(a,cls); ib=names(b,cls)
        except Exception: continue
        if not ia and not ib: continue
        print("  %s: IC1=%d EU=%d  EU-only=%s"%(cls,len(ia),len(ib),sorted(set(ib)-set(ia))[:12]))
        # config status for EU-only
        key={"technology":"technology","vehicle":"vehicle","commodity":"commodity","end-use":"end-use"}[cls]
        miss=[n for n in set(ib)-set(ia) if n not in cfg.get(key,{})]
        print("     EU-only NOT in userconfig[%s]: %s"%(key,sorted(miss)[:12]))
