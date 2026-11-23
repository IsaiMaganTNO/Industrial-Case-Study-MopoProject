import sqlite3, re, collections
M = r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.sqlite"
c = sqlite3.connect(M)
q = """select e.name, pd.name, pv.type from parameter_value pv join entity e on e.id=pv.entity_id
 join parameter_definition pd on pd.id=pv.parameter_definition_id where pv.type in ('time_series','map')"""
ts = collections.defaultdict(set)
for n, p, t in c.execute(q):
    for cc in ("DE","DK","NO","UK","FR","LU","NLC1"):
        if re.search(rf"(?<![A-Za-z]){cc}(?![A-Za-z])", n):
            ts[cc].add((re.sub(rf"(?<![A-Za-z]){cc}(?![A-Za-z])", "XX", n), p))
ref = collections.Counter(k for cc in ("DE","DK","NO","UK") for k in ts[cc])
common = {k for k, v in ref.items() if v >= 3}
for cc in ("FR","LU"):
    miss = sorted(common - ts[cc])
    print(f"== {cc} missing time-series params ({len(miss)}):")
    for e, p in miss[:40]: print("   ", p, e)
