import os, json, hashlib
new = r"data"
old = r"backups/data-pre-mixedres"
exts = (".json", ".yaml", ".yml", ".ini", ".cfg", ".toml")
rows = []
for root, _, files in os.walk(new):
    for f in files:
        if not f.lower().endswith(exts):
            continue
        np_ = os.path.join(root, f)
        rel = os.path.relpath(np_, new)
        op_ = os.path.join(old, rel)
        if not os.path.exists(op_):
            rows.append(("NEW-ONLY", rel, "", ""))
            continue
        a = hashlib.md5(open(op_, "rb").read()).hexdigest()
        b = hashlib.md5(open(np_, "rb").read()).hexdigest()
        if a != b:
            rows.append(("CHANGED", rel, a[:10], b[:10]))
print("config-like files under data/ compared:", len(rows), "differing/new")
for r in sorted(rows):
    print("%-9s %-55s %s -> %s" % r)
