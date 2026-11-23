import sqlite3, json, glob, re, collections
B = glob.glob(r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\output\*.sqlite")[0]
N = r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0\output\Investment_Results.3day_mr_frlu_ccslow_ccu_cap16_dac0.sqlite"
REG = re.compile(r"_((NL|BE)C\d+|DE|DK|NO|UK|FR|LU)$")
def load(db, par):
    c = sqlite3.connect(db); out = {}
    for e, t in c.execute("""select e.name, cast(pv.value as text) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
      join entity e on e.id=pv.entity_id where pd.name=?""", (par,)):
        nm = e.split("__")[1]
        d = json.loads(t)["data"]; items = d.items() if isinstance(d, dict) else d
        out[nm] = {k[:4]: v for k, v in items if isinstance(v, (int, float))}
    return out
for par in ("units_invested_available",):
    b, n = load(B, par), load(N, par)
    def split(nm):
        m = REG.search(nm); return (m.group(1)[:2], nm[:m.start()]) if m else ("??", nm)
    agg = lambda D, y: collections.Counter({split(k): v.get(y, 0) for k, v in D.items()})
    for y in ("2030", "2050"):
        ab, an = collections.defaultdict(float), collections.defaultdict(float)
        for k, v in b.items(): ab[split(k)] += v.get(y, 0)
        for k, v in n.items(): an[split(k)] += v.get(y, 0)
        print(f"\n=== {par} {y}: biggest changes, non-FR/LU")
        keys = set(ab) | set(an)
        for dv, k in sorted(((an[k]-ab[k], k) for k in keys if k[0] not in ("FR","LU")), key=lambda x: -abs(x[0]))[:20]:
            print(f"  {k[0]:3s}{k[1][:48]:48s}{ab[k]:10.2f} ->{an[k]:10.2f} ({dv:+.2f})")
        print(f"=== FR/LU {y} top")
        for k, v in sorted(((k, v) for k, v in an.items() if k[0] in ("FR","LU") and v > 0.01), key=lambda x: -x[1])[:20]:
            print(f"  {k[0]:3s}{k[1][:48]:48s}{v:10.2f}")
