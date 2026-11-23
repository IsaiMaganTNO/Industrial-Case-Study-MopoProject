"""Stage the hybrid IC1+PECD1 inputs over data/ (PLAN step 1).

Copies every file from `verification/Data - IC1 and PECD1` into `data/`,
overwriting the active input. Writes a manifest so the operation is auditable
and reversible. Excel lock files (~$...) are skipped.

Backup of the affected folders: backups/data-pre-mixedres/
"""
import hashlib
import json
import os
import shutil
import sys

SRC = "verification/Data - IC1 and PECD1"
DST = "data"
MANIFEST = "run_logs/stage1_manifest.json"


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    apply = "--apply" in sys.argv
    records = []
    skipped = []
    for dp, _, fs in os.walk(SRC):
        for f in fs:
            if f.startswith("~$"):
                skipped.append(f)
                continue
            s = os.path.join(dp, f)
            rel = os.path.relpath(s, SRC).replace("\\", "/")
            # the CO2 folder carries an explanatory suffix in the new tree
            rel_out = rel.replace("CO2_network(direct_link_ines_builder)/",
                                  "CO2_network/")
            d = os.path.join(DST, rel_out.replace("/", os.sep))
            rec = {
                "src": rel,
                "dst": rel_out,
                "src_bytes": os.path.getsize(s),
                "existed": os.path.exists(d),
                "dst_bytes_before": os.path.getsize(d) if os.path.exists(d) else None,
            }
            if apply:
                os.makedirs(os.path.dirname(d), exist_ok=True)
                shutil.copy2(s, d)
                rec["dst_bytes_after"] = os.path.getsize(d)
                rec["md5"] = md5(d)
                rec["verified"] = rec["dst_bytes_after"] == rec["src_bytes"]
            records.append(rec)

    n_new = sum(1 for r in records if not r["existed"])
    print("files to stage : %d" % len(records))
    print("  overwriting  : %d" % (len(records) - n_new))
    print("  brand new    : %d" % n_new)
    print("  skipped lock : %d %s" % (len(skipped), skipped))
    if apply:
        bad = [r for r in records if not r.get("verified")]
        print("  VERIFIED     : %d/%d" % (len(records) - len(bad), len(records)))
        if bad:
            print("  FAILED:", [r["dst"] for r in bad])
        os.makedirs("run_logs", exist_ok=True)
        with open(MANIFEST, "w") as fh:
            json.dump(records, fh, indent=1)
        print("manifest -> %s" % MANIFEST)
        return 1 if bad else 0
    print()
    print("DRY RUN - pass --apply to copy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
