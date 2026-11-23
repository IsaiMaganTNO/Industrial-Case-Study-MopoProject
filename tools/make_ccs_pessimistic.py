"""Pessimistic CCS variant of an NL+BE IC1 model: low storage caps + high-cost CO2 tariffs.
- scenario_alternative: high_CO2 -> low_CO2 (same rank)
- connection_flow_cost on CO2 connections: replaced by high-cost `network` tariff (EUR/t / 1000, as in the model)
- vom_cost on CO2-injection units: replaced by high-cost `network_to_storage` tariff
Every value is first checked to equal the LOW-cost file, so a mismatch aborts.
Usage: make_ccs_pessimistic.py SRC DST LOW.xlsx HIGH.xlsx
"""
import sys, os, shutil, sqlite3, json, re
import pandas as pd
src, dst, lowf, highf = sys.argv[1:5]
if os.path.exists(dst): sys.exit(f"{dst} exists")
lo = pd.read_excel(lowf, sheet_name=None); hi = pd.read_excel(highf, sheet_name=None)
def tab(x, s): return {(r["from"], r["to"]): float(r["tariff"]) for _, r in x[s].iterrows()}
NL, NH = tab(lo, "network"), tab(hi, "network"); SL, SH = tab(lo, "network_to_storage"), tab(hi, "network_to_storage")
shutil.copy(src, dst)
con = sqlite3.connect(dst); con.execute("PRAGMA foreign_keys=ON"); q = lambda s, *a: con.execute(s, a).fetchall()
aid = {n: i for i, n in q("select id,name from alternative")}
sc = q("select scenario_id,rank from scenario_alternative where alternative_id=?", aid["high_CO2"]); assert len(sc) == 1, sc
assert not q("select 1 from scenario_alternative where alternative_id=?", aid["low_CO2"])
con.execute("update scenario_alternative set alternative_id=? where alternative_id=?", (aid["low_CO2"], aid["high_CO2"]))
print("scenario: high_CO2 -> low_CO2 at rank", sc[0][1])
def fix(par, pat, lookup_lo, lookup_hi):
    rows = q("""select pv.id,e.name,pv.type,pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
               join entity e on e.id=pv.entity_id where pd.name=?""", par)
    n = 0
    for pid, name, typ, val in rows:
        k = pat(name)
        if k is None: continue
        assert typ in (None, "float"), (name, typ)
        old = float(json.loads(val)) * 1000
        lo_ = lookup_lo.get(k) or lookup_lo.get(k[::-1]); hi_ = lookup_hi.get(k) if k in lookup_hi else lookup_hi.get(k[::-1])
        assert lo_ is not None and abs(old - lo_) < 1e-6, (name, old, lo_)
        con.execute("update parameter_value set value=? where id=?", (json.dumps(hi_ / 1000).encode(), pid)); n += 1
        print(f"  {par:22s} {name[:55]:55s} {old:8.3f} -> {hi_:8.3f} EUR/t")
    return n
def conn_key(name):
    c = name.split("__")[0]; m = re.match(r"^(\w+?)_CO2_(\w+)$", c)
    return (m.group(1), m.group(2)) if m else None
def inj_key(name):
    m = re.match(r"^CO2-injection-(\w+?)_(\w+?)__CO2-storage-", name)
    return (m.group(2), m.group(1)) if m else None
n1 = fix("connection_flow_cost", lambda n: conn_key(n) if "_CO2_" in n.split("__")[0] else None, NL, NH)
n2 = fix("vom_cost", lambda n: inj_key(n) if n.startswith("CO2-injection-") else None, SL, SH)
con.commit(); con.close()
print(f"WROTE {dst}: {n1} transport costs, {n2} injection costs updated")
