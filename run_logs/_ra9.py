import glob, os, sqlite3, re
base = r".spinetoolbox\items"
pat = re.compile(r"^(BEC\d|NLC\d)")
for d in sorted(os.listdir(base)):
    for f in glob.glob(os.path.join(base, d, "*.sqlite")):
        try:
            c = sqlite3.connect("file:%s?mode=ro" % f.replace("\\","/"), uri=True)
            rows = [r[0] for r in c.execute(
                "SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name=\"region\"")]
            c.close()
        except Exception as ex:
            continue
        if not rows: continue
        ic1 = sorted(r for r in rows if pat.match(r))
        tgt = sorted(r for r in rows if r in ("DE","DK","NO","UK"))
        other = sorted(r for r in rows if not pat.match(r) and r not in ("DE","DK","NO","UK"))
        print("%-22s n=%-4d IC1=%-3d TARGETS=%s other=%d %s" % (
            d, len(rows), len(ic1), tgt or "NONE", len(other), other[:6]))
