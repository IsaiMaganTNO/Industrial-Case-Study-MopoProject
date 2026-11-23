import sqlite3, glob, os, re, collections
def regions(p):
    c=sqlite3.connect(p)
    names=[r[0] for r in c.execute("select name from entity")]
    ic1=set(); p1=set(); p2=set(); off=set()
    for n in names:
        for tok in re.split(r"[_|]",str(n)):
            if re.fullmatch(r"(BE|NL)C\d",tok): ic1.add(tok)
            elif re.fullmatch(r"[A-Z]{2}",tok): p1.add(tok)
            elif re.fullmatch(r"[A-Z]{2}\d{2}",tok): p2.add(tok)
            elif re.fullmatch(r"(NS|EM|AS|AT|BL|BS|MS)[A-Z]{2}\d*",tok): off.add(tok)
    return ic1,p1,p2,off
for d in ["vre_db","power_db","transmission_db","gas_db","industry_db","rdemand_db","biomass_db","heat_db","transport_db","hydro_db","ines_db"]:
    g=glob.glob(fr".spinetoolbox\items\{d}\*.sqlite")
    if not g: continue
    p=max(g,key=os.path.getsize)
    ic1,p1,p2,off=regions(p)
    print(f"  {d:18} IC1={len(ic1):3} PECD1={len(p1):3} PECD2={len(p2):4} OFF={len(off):3}  nonBENL_P1={sorted(p1-{'BE','NL'})[:10]}")
