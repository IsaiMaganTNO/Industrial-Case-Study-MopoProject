import re, collections
txt = open(r"run_logs\_frlu_audit.out", encoding="utf8").read().split("=====")
for blk in txt[1:]:
    lines = blk.splitlines(); print("=====", lines[0][:60])
    for l in lines[1:]:
        p = l.split()
        if len(p) < 2: continue
        cl, n = p[0], p[1]
        if cl.startswith("connection"): continue
        if re.search(r"(BEC|NLC)\d|CO2-injection|CO2-storage|ASUK|ATUK|NSUK|NSDE|NSDK|ASNO|NSNO", n): continue
        print("  ", l.strip()[:200])
