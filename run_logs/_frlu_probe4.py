import os, re, sqlite3, pandas as pd
o = open(r"run_logs\_frlu_probe4.out", "w", encoding="utf8"); P = lambda *a: (print(*a, file=o), o.flush())
pat = re.compile(r"(?<![A-Za-z])(FR|LU|DE)(?![A-Za-z])")
R = r"verification\Data - IC1 and PECD1"
for d, _, fs in os.walk(R):
    for f in fs:
        p = os.path.join(d, f); cnt = {"FR": 0, "LU": 0, "DE": 0}
        try:
            if f.endswith((".csv", ".txt")):
                for m in pat.findall(open(p, encoding="utf8", errors="ignore").read()): cnt[m] += 1
            elif f.endswith((".xlsx", ".xls")):
                for s, df in pd.read_excel(p, sheet_name=None, header=None).items():
                    for v in df.astype(str).values.ravel():
                        for m in pat.findall(v): cnt[m] += 1
            else: continue
        except Exception as e:
            P("ERR", p, e); continue
        P(f"{os.path.relpath(p, R):80s} FR={cnt['FR']:6d} LU={cnt['LU']:6d} DE={cnt['DE']:6d}")
P("===== EU_case sector DBs: entities for FR/LU/DE")
base = r"EU_case\.spinetoolbox\items"
for it in sorted(os.listdir(base)) if os.path.isdir(base) else []:
    db = os.path.join(base, it, it + ".sqlite")
    if not os.path.exists(db): continue
    try:
        c = sqlite3.connect(db); n = {}
        for k in ("FR", "LU", "DE"):
            n[k] = c.execute(f"select count(*) from entity where name='{k}' or name like '%\\_{k}' escape '\\'").fetchone()[0]
        P(f"{it:25s}", n); c.close()
    except Exception as e:
        P("ERR", db, e)
P("DONE")
o.close()
