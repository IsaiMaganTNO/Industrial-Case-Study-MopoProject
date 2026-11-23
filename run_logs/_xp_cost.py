import sqlite3, json, glob, re, collections
B = glob.glob(r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\output\*.sqlite")[0]
N = r"xpress_server\Investment_Results.3day_mr_frlu_ccslow_ccu_cap16_dac0.v3.xpress.sqlite"
print("BASE", B)
def costs(db):
    c = sqlite3.connect(db); out = {}
    for n, t in c.execute("""select pd.name, cast(pv.value as text) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
      where pd.name like 'objective_%' or pd.name='total_costs'"""):
        d = json.loads(t)["data"]; v = d.values() if isinstance(d, dict) else [y[1] for y in d]
        out[n] = out.get(n, 0) + sum(x for x in v if isinstance(x, (int, float)))
    return out
b, n = costs(B), costs(N)
print(f"{'component':40s}{'base':>14s}{'frlu':>14s}{'delta':>14s}")
for k in sorted(set(b) | set(n), key=lambda k: -abs(n.get(k,0)-b.get(k,0))):
    print(f"{k:40s}{b.get(k,0):14,.0f}{n.get(k,0):14,.0f}{n.get(k,0)-b.get(k,0):14,.0f}")

