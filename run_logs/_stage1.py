import os, hashlib

OLD = "data"
NEW = "verification/Data - IC1 and PECD1"

def walk(root):
    out = {}
    for dp, _, fs in os.walk(root):
        for f in fs:
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, root).replace("\\", "/")
            out[rel] = os.path.getsize(full)
    return out

a, b = walk(OLD), walk(NEW)
# normalise: new tree has CO2_network(direct_link_ines_builder)
def norm(p):
    return p.replace("CO2_network(direct_link_ines_builder)/", "CO2_network/")
b = {norm(k): v for k, v in b.items()}

ka, kb = set(a), set(b)
print("active files: %d   new files: %d" % (len(a), len(b)))
print("in BOTH     : %d" % len(ka & kb))
print("NEW only    : %d" % len(kb - ka))
print("ACTIVE only : %d" % len(ka - kb))

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

same = diff = 0
changed = []
for k in sorted(ka & kb):
    pa = os.path.join(OLD, k)
    pb = os.path.join(NEW, k.replace("CO2_network/", "CO2_network(direct_link_ines_builder)/"))
    if a[k] != b[k]:
        diff += 1; changed.append((k, a[k], b[k])); continue
    if md5(pa) == md5(pb):
        same += 1
    else:
        diff += 1; changed.append((k, a[k], b[k]))
print("identical   : %d" % same)
print("CHANGED     : %d" % diff)
print()
print("--- CHANGED (size active -> new) ---")
for k, x, y in changed[:40]:
    print("  %-62s %9d -> %9d" % (k[:62], x, y))
print()
print("--- NEW ONLY ---")
for k in sorted(kb - ka)[:40]:
    print("  %-62s %9d" % (k[:62], b[k]))
