import re, collections
L = open(r"run_logs\_frlu_audit.out", encoding="utf8").read().split("=====")[1].splitlines()[1:]
grp = collections.Counter(); ex = collections.defaultdict(list)
for l in L:
    p = l.split()
    if len(p) < 2: continue
    cl, n = p[0], p[1]
    # strip the counterpart region in 2-region names to get a "kind"
    k = re.sub(r"(BEC|NLC)\d", "R", n); k = re.sub(r"\b(AT|CH|CZ|PL|ES|IT|BE|NL|SE|IE)\b", "NB", k)
    kind = cl + " | " + re.sub(r"-?existing", "-existing", k.split("__")[0])[:55]
    grp[kind] += 1; ex[kind].append(n + " :: " + (p[2] if len(p) > 2 else ""))
for k, v in grp.most_common(70): print(f"{v:4d} {k:90s} e.g. {ex[k][0][:90]}")
