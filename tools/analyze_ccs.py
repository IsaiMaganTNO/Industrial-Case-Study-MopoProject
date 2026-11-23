import collections, re, sqlite3
import pandas as pd

DB = r"checkpoints\Final_SpineOpt_Model.tiny.1rep.gwfix.sqlite"
con = sqlite3.connect(DB); con.execute("PRAGMA foreign_keys = OFF")
rows = con.execute("""
  SELECT e.name, GROUP_CONCAT(el.name,'|')
  FROM entity e JOIN entity_class c ON e.class_id=c.id
  JOIN entity_element ee ON ee.entity_id=e.id
  JOIN entity el ON el.id=ee.element_id
  WHERE c.name='unit_flow__unit_flow' GROUP BY e.id
""").fetchall()
con.close()

# name form: "<unit>__atmosphere|<fuel>__<unit>"  -> unit is the token before __atmosphere
atm_units = set()
for nm, els in rows:
    if els and "atmosphere" in els:
        for part in els.split("|"):
            if part.endswith("__atmosphere"):
                atm_units.add(part[: -len("__atmosphere")])
print("units WITH an atmosphere row:", len(atm_units))

YEARS = ["2030","2040","2050"]
yr = lambda t: t[:4]
fam = lambda u: re.sub(r"_(NL|BE)C\d+$", "", u)

def pack(recs):
    flows = collections.defaultdict(lambda: collections.defaultdict(float)); inv={}
    for var, bn, ser in recs:
        if var=="unit_flow":
            for t,v in ser.items(): flows[tuple(bn)][yr(t)] += v
        elif var=="units_invested_available":
            acc=collections.defaultdict(list)
            for t,v in ser.items(): acc[yr(t)].append(v)
            inv[bn[1]] = {y: sum(v)/len(v) for y,v in acc.items()}
    return flows, inv

fa, ia = pack(pd.read_pickle("logs/res_after.pkl"))
fg, ig = pack(pd.read_pickle("logs/res_gwfix.pkl"))

# CO2 captured = flow TO a CO2_* node
def co2_to(flows):
    agg = collections.defaultdict(lambda: collections.defaultdict(float))
    for k,d in flows.items():
        unit, node, direction = k[1], k[2], k[3]
        if direction=="to_node" and node.startswith("CO2"):
            for y in YEARS: agg[fam(unit)][y] += d.get(y,0.0)
    return agg
qa, qg = co2_to(fa), co2_to(fg)

def cls(f):
    if f.startswith("DAC"): return "DAC"
    if re.search(r"\(BM|BMW|bio", f, re.I): return "BIO/BECCS"
    if re.search(r"\(NG\)|SMR|CCGT|REF|\(LN\)|coal|Oxy-CaL", f): return "FOSSIL+CCS"
    if re.search(r"\(COEL\)|\(EL\)|\(H2\)|\(MeOH\)", f): return "ELEC/H2 synth"
    return "OTHER"

out=[]
out.append("=== CO2 CAPTURED (flow to CO2_* nodes, daily totals; x365 for annual) ===")
hdr="{:<24}{:<14}{:>12}{:>12}{:>12}{:>9}".format("family","class","co2patch50","gwfix50","delta","atmRow")
out.append(hdr); out.append("-"*len(hdr))
ta=collections.defaultdict(float); tg=collections.defaultdict(float)
for k in sorted(set(qa)|set(qg), key=lambda k:-abs(qg[k].get("2050",0)-qa[k].get("2050",0))):
    a,g = qa[k].get("2050",0.0), qg[k].get("2050",0.0)
    c=cls(k); ta[c]+=a; tg[c]+=g
    sib=[u for u in ig if fam(u)==k]
    flag = "yes" if any(u in atm_units for u in sib) else "NO"
    if abs(g-a)>0.5 or g>0.5:
        out.append("{:<24}{:<14}{:>12.1f}{:>12.1f}{:>12.1f}{:>9}".format(k[:23],c,a,g,g-a,flag))
out.append("")
out.append("=== 2050 CAPTURE TOTALS BY CLASS ===")
out.append("{:<16}{:>14}{:>14}{:>12}".format("class","co2patch","gwfix","delta"))
for c in sorted(set(ta)|set(tg)):
    out.append("{:<16}{:>14.1f}{:>14.1f}{:>12.1f}".format(c,ta[c],tg[c],tg[c]-ta[c]))

# how much capture comes from units with NO atmosphere row (free negatives)
free_a=free_g=tot_a2=tot_g2=0.0
for k,d in fg.items():
    if k[3]=="to_node" and k[2].startswith("CO2"):
        v=d.get("2050",0.0); tot_g2+=v
        if k[1] not in atm_units: free_g+=v
for k,d in fa.items():
    if k[3]=="to_node" and k[2].startswith("CO2"):
        v=d.get("2050",0.0); tot_a2+=v
        if k[1] not in atm_units: free_a+=v
out.append("")
out.append("=== CAPTURE FROM UNITS LACKING AN ATMOSPHERE ROW (unpriced carbon) ===")
out.append("co2patch: {:.1f} of {:.1f} ({:.0f}%)".format(free_a, tot_a2, 100*free_a/max(tot_a2,1e-9)))
out.append("gwfix   : {:.1f} of {:.1f} ({:.0f}%)".format(free_g, tot_g2, 100*free_g/max(tot_g2,1e-9)))
open("logs/ccs_compare.txt","w",encoding="utf-8").write("\n".join(out))
