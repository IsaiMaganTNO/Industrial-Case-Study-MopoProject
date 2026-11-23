import sqlite3, re, collections
M = r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.sqlite"
c = sqlite3.connect(M)
rows = c.execute("""select e.name, pd.name from parameter_value pv join entity e on e.id=pv.entity_id
  join parameter_definition pd on pd.id=pv.parameter_definition_id""").fetchall()
ref = ("DE","DK","NO","UK")
def gen(n, cc): return re.sub(rf"(?<![A-Za-z]){cc}(?![A-Za-z])", "XX", n)
have = collections.defaultdict(set)
for n, p in rows:
    for cc in ref + ("FR","LU"):
        if re.search(rf"(?<![A-Za-z]){cc}(?![A-Za-z])", n): have[cc].add((gen(n, cc), p))
# pairs present in >=3 of the 4 reference countries but absent in FR or LU
cnt = collections.Counter(k for cc in ref for k in have[cc])
common = {k for k, v in cnt.items() if v >= 3}
for cc in ("FR","LU"):
    miss = sorted(common - have[cc])
    byp = collections.Counter(p for _, p in miss)
    print(f"== {cc}: {len(miss)} entity/param pairs that DE/DK/NO/UK (>=3 of 4) have")
    for p, k in byp.most_common(40): print(f"   {k:4d}  {p}")
    print("   examples:", [e for e, _ in miss[:30]])
