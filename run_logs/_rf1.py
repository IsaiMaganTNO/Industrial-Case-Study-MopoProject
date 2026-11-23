import csv,collections
p=r"data-pipelines\europe\_biomass\db_biomass_ener_mopo.csv"
raw=open(p,encoding="utf-8",errors="replace").readline()
print("HEADER RAW:",raw[:300])
delim=";" if raw.count(";")>raw.count(",") else ","
print("delim:",repr(delim))
rows=list(csv.DictReader(open(p,encoding="utf-8",errors="replace"),delimiter=delim))
print("rows",len(rows),"cols",list(rows[0].keys()))
for c in rows[0].keys():
    vals=set(r[c] for r in rows)
    if len(vals)<60: print("  %-22s n=%-4d %s"%(c,len(vals),sorted(vals)[:40]))
    else: print("  %-22s n=%-4d (many) e.g. %s"%(c,len(vals),sorted(vals)[:8]))
