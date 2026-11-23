"""Optimistic-CCS sensitivity of the baseline (3-day MR pessimistic, CCU fix, cap16, DAC0).
Reverses tools/make_ccs_pessimistic.py only: scenario low_CO2 -> high_CO2; CO2 tariffs high-cost -> low-cost.
DAC existing_units=0 and the methanation CCU patch are kept (Base alternative). NSNL012 cap16 lives in low_CO2 -> inactive."""
import os, shutil, sqlite3, json, re, pandas as pd
SRC = r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"
OPT = r"runs\3day_mr_fix\input\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite"
os.makedirs(r"runs\3day_mr_ccsopt_ccu_dac0", exist_ok=True)
DST = r"runs\3day_mr_ccsopt_ccu_dac0\Final_SpineOpt_Model.tiny.3day.mr_ccsopt_ccu_dac0.sqlite"
o = open(r"run_logs\_ccsopt_build.out", "w", encoding="utf8"); P = lambda *a: (print(*a, file=o), o.flush())
assert os.path.exists(SRC), SRC
if os.path.exists(DST): os.remove(DST)
shutil.copyfile(SRC, DST)
lo = pd.read_excel(r"verification\CO2_data_IC1_low_cost.xlsx", sheet_name=None); hi = pd.read_excel(r"verification\CO2_data_IC1_high_cost.xlsx", sheet_name=None)
tab = lambda x, s: {(r["from"], r["to"]): float(r["tariff"]) for _, r in x[s].iterrows()}
NL, NH, SL, SH = tab(lo, "network"), tab(hi, "network"), tab(lo, "network_to_storage"), tab(hi, "network_to_storage")
c = sqlite3.connect(DST); q = lambda s, *a: c.execute(s, a).fetchall()
aid = {n: i for i, n in q("select id,name from alternative")}
sa = q("select scenario_id,rank from scenario_alternative where alternative_id=?", aid["low_CO2"]); assert len(sa) == 1, sa
assert not q("select 1 from scenario_alternative where alternative_id=?", aid["high_CO2"])
c.execute("update scenario_alternative set alternative_id=? where alternative_id=?", (aid["high_CO2"], aid["low_CO2"]))
P("scenario low_CO2 -> high_CO2 at rank", sa[0][1])
def get(d, k): return d[k] if k in d else d.get(k[::-1])
def fix(par, keyf, H, L):
    n = 0
    for pid, name, val in q("select pv.id,e.name,pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id where pd.name=?", par):
        k = keyf(name)
        if k is None: continue
        old = float(json.loads(val)) * 1000; h, l = get(H, k), get(L, k)
        assert h is not None and abs(old - h) < 1e-6, (name, old, h)
        c.execute("update parameter_value set value=? where id=?", (json.dumps(l / 1000).encode(), pid)); n += 1
    return n
def ck(n):
    m = re.match(r"^(\w+?)_CO2_(\w+)$", n.split("__")[0]); return (m.group(1), m.group(2)) if m and "_CO2_" in n.split("__")[0] else None
def ik(n):
    m = re.match(r"^CO2-injection-(\w+?)_(\w+?)__CO2-storage-", n); return (m.group(2), m.group(1)) if m else None
n1 = fix("connection_flow_cost", ck, NH, NL); n2 = fix("vom_cost", ik, SH, SL)
c.commit(); P("tariffs reset to low-cost:", n1, "transport,", n2, "injection")
# ---- verification vs mr_fix (optimistic original) for CCS-related values
Q = "select e.name, pd.name, a.name, pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id"
v_new = {r[:3]: r[3] for r in q(Q)}; v_opt = {r[:3]: r[3] for r in sqlite3.connect(OPT).execute(Q)}
v_src = {r[:3]: r[3] for r in sqlite3.connect(SRC).execute(Q)}
def same(a, b):
    try: return json.loads(a) == json.loads(b)
    except Exception: return a == b
ccs = [k for k in v_new if ("CO2" in k[0] and k[1] in ("connection_flow_cost", "vom_cost"))]
P("CO2 tariff values:", len(ccs), " equal to mr_fix:", sum(1 for k in ccs if k in v_opt and same(v_new[k], v_opt[k])), " missing in mr_fix:", sum(1 for k in ccs if k not in v_opt))
hc = [k for k in v_opt if k[2] == "high_CO2"]
P("high_CO2 values in mr_fix:", len(hc), " identical in new:", sum(1 for k in hc if k in v_new and same(v_new[k], v_opt[k])))
d = [k for k in v_new if k in v_src and not same(v_new[k], v_src[k])]
P("changed vs baseline:", len(d), " by param:", pd.Series([k[1] for k in d]).value_counts().to_dict())
P("added/removed vs baseline:", len(set(v_new) - set(v_src)), len(set(v_src) - set(v_new)))
P("scenario_alternative:", q("select s.name, a.name, sa.rank from scenario_alternative sa join scenario s on s.id=sa.scenario_id join alternative a on a.id=sa.alternative_id order by s.name, sa.rank"))
P("DAC existing_units=0 kept:", sum(1 for k in v_new if k[0].startswith("DAC_") and k[1] == "existing_units"))
P("methanation->atmosphere coef kept:", sum(1 for k in v_new if k[0].startswith("methanation_") and "__atmosphere__" in k[0]))
P("DONE")

